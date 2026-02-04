"""
Map manager for generating and navigating game maps.
"""
import random
from typing import List, Dict, TYPE_CHECKING
from utils.types import RoomType
from .map_node import MapNode
from .map_data import MapData

# Avoid circular import - use TYPE_CHECKING for type hints
if TYPE_CHECKING:
    from rooms.base import Room


class MapManager:
    """
    Manages map generation and navigation for a single act.
    
    Based on Slay the Spire's map generation algorithm:
    - Each act has 17 floors (0-16)
    - Floors 0, 8, 14, 15 have fixed room types
    - Other floors have random room types with weighted probabilities
    - Each floor has 2-6 nodes
    - Nodes have 1-3 connections to adjacent floors
    """
    
    # Room type probabilities for random floors (weights)
    ROOM_TYPE_WEIGHTS = {
        RoomType.MONSTER: 53,
        RoomType.ELITE: 8,
        RoomType.REST: 12,
        RoomType.MERCHANT: 5,
        RoomType.UNKNOWN: 22,
    }
    
    def __init__(self, seed: int, act_id: int = 1, deadly_events: bool = False):
        """
        Initialize map manager.
        
        Args:
            seed: Random seed for deterministic generation
            act_id: The act number (default: 1)
            deadly_events: Whether Deadly Events modifier is active (default: False)
        """
        self.seed = seed
        self.act_id = act_id
        self.rng = random.Random(seed)
        self.map_data = MapData(act_id)
        self.deadly_events = deadly_events
        
        # Track visits to each ? room type for "bad luck protection"
        # Each increment represents a visit that didn't result in that type
        self.unknown_room_visits = {
            RoomType.MONSTER: 0,    # Starts at 10%, +10% per non-monster visit
            RoomType.MERCHANT: 0,    # Starts at 3%, +3% per non-merchant visit
            RoomType.TREASURE: 0,     # Starts at 2%, +2% (or +4%) per non-treasure visit
            RoomType.ELITE: 0,        # Starts at 20% (only with deadly_events, floor 6+), +20% per non-elite visit
        }
        
        # todo: use relic's own counter
        self._tiny_chest_counter = 0
    
    def generate_map(self) -> MapData:
        """
        Generate a complete map for the act.
        
        Returns:
            MapData containing the generated map
        """
        # Generate floor structure (number of nodes per floor)
        floor_sizes = self._generate_floor_structure()
        
        # Generate nodes with connections
        nodes_with_connections = self._generate_nodes_with_connections(floor_sizes)
        
        # Assign room types
        self._assign_room_types(nodes_with_connections)
        
        # Store in map data
        self.map_data.nodes = nodes_with_connections
        
        return self.map_data
    
    def _generate_floor_structure(self) -> List[int]:
        """
        Generate the number of nodes for each floor.
        
        Returns:
            List of node counts for each floor (17 floors for standard act)
        """
        floor_sizes = []
        
        for floor in range(17):  # 17 floors (0-16)
            if floor == 0:
                # Floor 0: 3 nodes (player can start at any)
                floor_sizes.append(3)
            elif floor == 15:
                # Floor 15: 1 node (boss)
                floor_sizes.append(1)
            elif floor == 16:
                # Floor 16: 0 nodes (boss chest is invisible)
                floor_sizes.append(0)
            else:
                # Other floors: 2-5 nodes
                floor_sizes.append(self.rng.randint(2, 5))
        
        return floor_sizes
    
    def _generate_nodes_with_connections(self, floor_sizes: List[int]) -> List[List[MapNode]]:
        """
        Generate all nodes with their connections.
        
        Args:
            floor_sizes: Number of nodes per floor
            
        Returns:
            2D array of MapNode objects with connections set
        """
        nodes: List[List[MapNode]] = []
        
        # Create nodes floor by floor
        for floor, size in enumerate(floor_sizes):
            floor_nodes = []
            for position in range(size):
                # Default room type, will be reassigned later
                node = MapNode(floor, position, RoomType.MONSTER)
                floor_nodes.append(node)
            nodes.append(floor_nodes)
        
        # Create connections between adjacent floors
        for floor in range(len(floor_sizes) - 1):
            current_floor_nodes = nodes[floor]
            next_floor_nodes = nodes[floor + 1]
            
            if not current_floor_nodes or not next_floor_nodes:
                continue
            
            # Track used positions to prevent multiple connections to same node
            used_positions = set()
            
            # Track the minimum position that can be connected to prevent line crossing
            # This ensures that if node A (at position i) connects to position j,
            # no node to the right of A (position > i) can connect to any position <= j
            min_allowed_position = 0
            
            # Process nodes from left to right
            for current_node in current_floor_nodes:
                # Calculate available positions (from min_allowed to end, excluding used)
                available_positions = [
                    pos for pos in range(min_allowed_position, len(next_floor_nodes))
                    if pos not in used_positions
                ]
                
                if not available_positions:
                    break
                
                # Determine number of connections (1-3, but limited by available positions)
                max_connections = min(3, len(available_positions))
                num_connections = self.rng.randint(1, max_connections)
                
                # Randomly select nodes to connect to from available range
                connected_positions = self.rng.sample(available_positions, num_connections)
                
                for pos in connected_positions:
                    current_node.add_connection_up(pos)
                    used_positions.add(pos)
                
                # Update min_allowed_position to prevent line crossing
                # Next node (to the right) can only connect to positions > max connected position
                # This ensures lines don't cross: if left node connects to position i,
                # right node can only connect to positions > i
                if connected_positions:
                    min_allowed_position = max(connected_positions) + 1
        
        return nodes
    
    def _assign_room_types(self, nodes: List[List[MapNode]]):
        """
        Assign room types to all nodes based on rules.
        
        Args:
            nodes: 2D array of MapNode objects
        """
        for floor in range(len(nodes)):
            for node in nodes[floor]:
                if floor == 0:
                    # Floor 0: All monsters (easy pool)
                    node.room_type = RoomType.MONSTER
                elif floor == 8:
                    # Floor 8: All treasure
                    node.room_type = RoomType.TREASURE
                elif floor == 14:
                    # Floor 14: All rest
                    node.room_type = RoomType.REST
                elif floor == 15:
                    # Floor 15: Boss
                    node.room_type = RoomType.BOSS
                else:
                    # Other floors: Random based on weights
                    node.room_type = self._get_random_room_type()
    
    def _get_random_room_type(self) -> RoomType:
        """
        Get a random room type based on weighted probabilities.
        
        Returns:
            A random RoomType
        """
        room_types = list(self.ROOM_TYPE_WEIGHTS.keys())
        weights = list(self.ROOM_TYPE_WEIGHTS.values())
        
        return self.rng.choices(room_types, weights=weights, k=1)[0]

    @staticmethod
    def _normalize_relic_name(name) -> str:
        if not name:
            return ""
        return str(name).strip().lower().replace(" ", "").replace("_", "").replace("-", "")

    def _get_player_relics(self):
        try:
            from engine.game_state import game_state
        except Exception:
            return ()
        player = getattr(game_state, "player", None)
        return getattr(player, "relics", ()) if player else ()

    def _player_has_relic(self, relic_key: str) -> bool:
        target = self._normalize_relic_name(relic_key)
        if not target:
            return False
        for relic in self._get_player_relics():
            if isinstance(relic, str):
                if self._normalize_relic_name(relic) == target:
                    return True
                continue
            relic_id = getattr(relic, "idstr", None)
            if relic_id and self._normalize_relic_name(relic_id) == target:
                return True
            relic_name = getattr(relic, "name", None)
            if relic_name and self._normalize_relic_name(relic_name) == target:
                return True
            relic_cls_name = relic.__class__.__name__
            if relic_cls_name and self._normalize_relic_name(relic_cls_name) == target:
                return True
        return False

    @property
    def has_tiny_chest(self) -> bool:
        return self._player_has_relic("tiny_chest") or self._player_has_relic("tinychest")

    @property
    def has_juzu_bracelet(self) -> bool:
        return self._player_has_relic("juzu_bracelet") or self._player_has_relic("juzubracelet")

    @property
    def has_ssserpent_head(self) -> bool:
        return self._player_has_relic("ssserpent_head") or self._player_has_relic("ssserpenthead")
    
    def get_available_moves(self) -> List[MapNode]:
        """
        Get all nodes that can be moved to from the current position.
        
        Returns:
            List of MapNode objects that are reachable from current position
        """
        if self.map_data.current_floor >= len(self.map_data.nodes) - 1:
            return []
        
        current_node = self.map_data.get_current_node()
        available_nodes = []
        
        for pos in current_node.connections_up:
            if self.map_data.current_floor + 1 < len(self.map_data.nodes):
                try:
                    node = self.map_data.get_node(
                        self.map_data.current_floor + 1,
                        pos
                    )
                    available_nodes.append(node)
                except IndexError:
                    pass
        
        return available_nodes
    
    def move_to_node(self, floor: int, position: int):
        """
        Move to a specific node and create the corresponding Room instance.
        
        Args:
            floor: The target floor number
            position: The position index on that floor
            
        Returns:
            Room instance for the target node
        """
        node = self.map_data.get_node(floor, position)
        
        # Create room instance based on room type
        room = self._create_room_instance(node.room_type)
        
        # Update current position
        self.map_data.set_current_position(floor, position)
        
        return room
    
    def _create_room_instance(self, room_type: RoomType):
        """
        Create a Room instance based on the room type.
        
        The room content is determined by the game state, not stored in the map.
        
        Args:
            room_type: The type of room to create
            
        Returns:
            Room instance
        """
        # Import here to avoid circular dependency
        from rooms.base import Room
        from rooms.combat import CombatRoom
        
        if room_type == RoomType.MONSTER:
            # TODO: Get monster encounter from game state
            return CombatRoom(enemies=[])
        
        elif room_type == RoomType.ELITE:
            # TODO: Get elite encounter from game state
            return CombatRoom(enemies=[], is_elite=True)
        
        elif room_type == RoomType.BOSS:
            # TODO: Get boss encounter from game state
            return CombatRoom(enemies=[], is_boss=True)
        
        elif room_type == RoomType.UNKNOWN:
            # Resolve unknown room type
            actual_type = self._resolve_unknown_type(self.map_data.current_floor)
            return self._create_room_instance(actual_type)
        
        else:
            # Other room types (REST, MERCHANT, TREASURE)
            # TODO: Implement these room types
            # For now, return a basic Room
            return Room()
    
    def _resolve_unknown_type(self, floor: int) -> RoomType:
        """
        Determine what type an unknown room becomes when entered.
        
        Based on Slay the Spire's ? room mechanics:
        - Base chances: Monster 10%, Treasure 2%, Shop 3%, Elite 20% (with deadly_events, floor 6+)
        - Each visit that doesn't result in a type increases its chance
        - Event fills remaining probability
        - Tiny Chest relic: Every 4th ? room is Treasure (resets treasure chance)
        - Juzu Bracelet: Regular enemy combats no longer in ? rooms
        - Ssserpent Head: Gain 50 Gold on entering ? room
        
        Args:
            floor: The current floor number
            
        Returns:
            The actual RoomType for this unknown room
        """
        # Check Tiny Chest relic - every 4th ? room is Treasure
        self._tiny_chest_counter += 1
        if self.has_tiny_chest and self._tiny_chest_counter % 4 == 0:
            # Tiny Chest forces Treasure room, resets treasure visit counter
            self.unknown_room_visits[RoomType.TREASURE] = 0
            return RoomType.TREASURE
        
        # Calculate current probabilities based on visit counts
        monster_chance = 10 + (self.unknown_room_visits[RoomType.MONSTER] * 10)
        treasure_chance = 2 + (self.unknown_room_visits[RoomType.TREASURE] * (4 if self.deadly_events else 2))
        shop_chance = 3 + (self.unknown_room_visits[RoomType.MERCHANT] * 3)
        
        # Elite only appears with deadly_events modifier on floor 6+
        elite_chance = 0
        if self.deadly_events and floor >= 6:
            elite_chance = 20 + (self.unknown_room_visits[RoomType.ELITE] * 20)
        
        # Juzu Bracelet removes regular monsters from ? rooms
        if self.has_juzu_bracelet:
            monster_chance = 0
        
        # Event fills remaining probability
        total_chances = monster_chance + treasure_chance + shop_chance + elite_chance
        event_chance = 100 - total_chances
        
        # Roll for encounter type
        roll = self.rng.randint(1, 100)
        
        if roll <= monster_chance:
            chosen_type = RoomType.MONSTER
        elif roll <= monster_chance + treasure_chance:
            chosen_type = RoomType.TREASURE
        elif roll <= monster_chance + treasure_chance + shop_chance:
            chosen_type = RoomType.MERCHANT
        elif roll <= monster_chance + treasure_chance + shop_chance + elite_chance:
            chosen_type = RoomType.ELITE
        else:
            chosen_type = RoomType.UNKNOWN  # Event
        
        # Reset visit counter for the chosen type
        self.unknown_room_visits[chosen_type] = 0
        
        # Increment visit counters for all other types
        for room_type in self.unknown_room_visits:
            if room_type != chosen_type:
                self.unknown_room_visits[room_type] += 1
        
        # Ssserpent Head effect: gain 50 Gold
        if self.has_ssserpent_head:
            # TODO: Add 50 gold to player
            pass
        
        return chosen_type

# PROJECT KNOWLEDGE BASE - ENGINE MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Game loop controller and singleton state management.

## STRUCTURE
```
engine/
├── game_flow.py        # Main game loop controller
├── game_state.py      # Singleton state manager
├── combat_state.py    # Combat state management
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Game loop | engine/game_flow.py | Iterates rooms, handles win/death |
| Global state | engine/game_state.py | Singleton with config, map, combat, player |
| Combat state | engine/combat_state.py | Combat-specific state (deck, discard, hand) |
| Event stack | engine/game_state.py | Tracks active events for rewards |

## CODE MAP

### GameState Singleton (engine/game_state.py: 200 lines)
```python
class GameState:
    def __init__(self):
        # Configuration
        self.config = GameConfig.load()
        self.language = self.config.language
        
        # Core game objects
        self.map_manager = None
        self.combat = None
        self.player = None
        self.event_pool = None
        self.current_floor = 0
        self.current_room = None
        
        # Event tracking
        self.event_stack = []  # Stack of active events
        
        # Game status
        self.act = 1
        self.game_over = False
        self.seed = self.config.seed
        
        # Initialize game
        self.initialize_map()
        self.initialize_player()
        self.initialize_combat()
    
    def initialize_map(self):
        """Create MapManager and generate initial map"""
        from map.map_manager import MapManager
        self.map_manager = MapManager(
            seed=self.seed,
            act_id=self.act
        )
        self.map_manager.generate_map()
    
    def initialize_player(self):
        """Create Player instance"""
        from player.player import Player
        self.player = Player(character=self.config.character)
    
    def initialize_combat(self):
        """Create CombatState instance"""
        from engine.combat_state import CombatState
        self.combat = CombatState()
    
    def start_game(self):
        """Start game loop"""
        # Initialize map
        self.map_manager.generate_map()
        
        # Reset player to starting room
        self.current_floor = 0
        self.current_room = None
        self.game_over = False
        
        # Clear event stack
        self.event_stack.clear()
        
        # Enter first room
        self._enter_first_room()
    
    def _enter_first_room(self):
        """Enter starting room (floor 0, act 1)"""
        first_room = self.map_manager.get_first_room()
        if first_room:
            self.current_room = first_room
            result = self.current_room.enter()
            self._handle_room_result(result)
```

### CombatState Class (engine/combat_state.py: 150 lines)
```python
class CombatState:
    def __init__(self, player: Player):
        self.player = player
        
        # Card piles (separate from player for combat isolation)
        self.deck = []
        self.hand = []
        self.discard = []
        self.exhaust = []
        
        # Turn state
        self.turn = 0
        self.player_energy = 0
        
        # Enemy
        self.enemies = []
        
        # Enemy turn order
        self.enemy_turn = 0
        
        # End combat state
        self.end_combat = False
```

### GameFlow Class (engine/game_flow.py: 170 lines)

```python
# Main game loop (lines 80-150)
while not game_state.game_over:
    # Select next room
    _select_next_room()
    
    # Enter room
    result = current_room.enter()
    
    # Handle result
    if result in ("DEATH", "WIN"):
        _handle_game_over(result)
    elif result is None:
        # Player chose to move
        pass
```

### Room Lifecycle

```python
# Room.enter() method flow (rooms/base.py:57-100)
def enter(self) -> str:
    self.init()                          # Setup
    while not self.should_leave:        # Main loop
        # Build options
        # Execute actions
        result = self.execute_actions()
        
        # Check for game end
        if result in ("DEATH", "WIN"):
            return result
        # Rebuild menu if not leaving
        if not self.should_leave:
            self.action_queue.clear()
    return None
```

## CONVENTIONS

**Singleton Pattern:**
- GameState is module-level singleton accessed via `game_state` import
- Only one GameState instance exists throughout game lifetime
- All game components (player, map, combat, event_pool) reference game_state

**Game Loop:**
- GameFlow iterates over rooms until game_over
- Player selects rooms via map selection
- Room.enter() returns "DEATH", "WIN", or None
- "WIN" triggers victory (floor 16 reached)
- "DEATH" triggers game over (player HP <= 0)

**Combat Isolation:**
- CombatState maintains its own card piles (deck, hand, discard)
- Combat cards are copied from player.deck and managed separately
- Reset to player deck after combat ends

**Event Stack:**
- Events can push rewards to game_state.event_stack
- Event.trigger() can return cards/relics/gold that are added immediately

## ANTI-PATTERNS (THIS PROJECT)
- NEVER: Direct GameState instantiation - always use game_state singleton
- NEVER: Modify player.deck during combat - use CombatState.deck
- NEVER: Create multiple GameState instances - singleton pattern
- ALWAYS: engine/game_flow.py:80-150 - Main game loop until game_over flag

## COMMANDS
```bash
# Run game
python __main__.py

# Run tests
pytest tests/test_game_flow.py -v          # Game loop tests
```

## NOTES
- GameState singleton prevents multiple game instances
- CombatState isolates combat card management from player deck
- Room enter() loop handles its own action queue
- GameFlow manages room transitions and game over conditions

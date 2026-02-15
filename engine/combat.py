"""
Combat logic class - independent from rooms.
Can be triggered by CombatRoom or Events.
Uses global action queue for action management.
"""
from typing import List
from actions.base import Action
from actions.card import DiscardCardAction
from actions.combat import EndTurnAction
from actions.display import DisplayTextAction, SelectAction
from enemies.base import Enemy
from utils.option import Option
from utils.result_types import BaseResult, GameStateResult, NoneResult
from utils.types import CombatType
from localization import LocalStr, Localizable


def _debug_print_combat_state(phase: str, enemies: List[Enemy] = None):
    """Print combat state for debugging."""
    from engine.game_state import game_state
    debug = game_state.config.get("debug", {})
    if not bool(debug.get("enable", False)):
        return
    
    player = game_state.player
    print(f"\n{'#'*60}")
    print(f"[COMBAT] Phase: {phase}")
    print(f"{'#'*60}")
    
    # Player state
    hand = player.card_manager.get_pile("hand") if player.card_manager else []
    hand_names = [c.__class__.__name__ for c in hand]
    print(f"[PLAYER] HP: {player.hp}/{player.max_hp}, Block: {player.block}, Energy: {player.energy}")
    print(f"[PLAYER] Hand ({len(hand)}): {hand_names}")
    if player.powers:
        power_names = [f"{p.__class__.__name__}({p.stacks})" for p in player.powers if hasattr(p, 'stacks')]
        print(f"[PLAYER] Powers: {power_names}")
    
    # Enemy state
    if enemies is None:
        enemies = game_state.current_combat.enemies if game_state.current_combat else []
    
    for i, enemy in enumerate(enemies):
        if hasattr(enemy, 'is_dead') and enemy.is_dead():
            print(f"[ENEMY {i}] {enemy.__class__.__name__}: DEAD")
        else:
            hp = getattr(enemy, 'hp', '?')
            max_hp = getattr(enemy, 'max_hp', '?')
            block = getattr(enemy, 'block', 0)
            print(f"[ENEMY {i}] {enemy.__class__.__name__}: HP {hp}/{max_hp}, Block: {block}")
            if hasattr(enemy, 'intention') and enemy.intention:
                intent = enemy.intention
                intent_type = getattr(intent, 'intent_type', '?')
                intent_damage = getattr(intent, 'damage', '?')
                print(f"[ENEMY {i}]   Intent: {intent_type}, Damage: {intent_damage}")
            if hasattr(enemy, 'powers') and enemy.powers:
                power_names = [f"{p.__class__.__name__}({getattr(p, 'stacks', '?')})" for p in enemy.powers]
                print(f"[ENEMY {i}]   Powers: {power_names}")
    
    print(f"{'#'*60}\n")


class Combat(Localizable):
    """
    Combat logic class - handles combat independently from room system.

    Can be triggered by:
    - CombatRoom (normal battles)
    - Events (event-based combat)
    Uses global action queue from game_state for action management.
    """

    def __init__(self, enemies: List[Enemy], combat_type: CombatType = CombatType.NORMAL):
        """
        Initialize combat.

        Args:
            enemies: List of enemy instances
            combat_type: Type of combat (Normal/Elite/Boss), used for relic effects
        """
        self.enemies = enemies
        self.combat_type = combat_type
        
        # Combat state
        from .combat_state import CombatState
        self.combat_state = CombatState()
        
        # Combat control flags
        self.combat_ended = False
        self.player_turn_ended = False

    def remove_enemy(self, enemy: Enemy):
        """Remove an enemy from combat (e.g., when killed)."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
        
        # Localization
        self.localization_prefix = "combat"

    def start(self) -> GameStateResult:
        """
        Start combat execution.

        Returns:
            Execution result: WIN / LOSE / ESCAPE
        """
        from engine.game_state import game_state

        # Initialize combat state
        self._init_combat()

        # Display combat start message
        game_state.action_queue.add_action(DisplayTextAction(
            text_key="combat.enter"
        ))

        # Combat main loop (as per todo.md)
        while True:
            # Execute player phase
            result = self.execute_player_phase()
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                break

            # Execute enemy phase
            result = self.execute_enemy_phase()
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                break

        return result

    def execute_player_phase(self) -> BaseResult:
        """
        Execute player phase.

        Returns:
            GameStateResult if combat ends, NoneResult otherwise
        """
        from engine.game_state import game_state

        # Start player phase: gain energy, draw cards, trigger start-of-turn effects
        self._start_player_turn()
        
        # Execute draw cards and start-of-turn effects immediately
        # This ensures hand is populated before building player actions
        result = game_state.execute_all_actions()
        if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
            return result
        
        # DEBUG: Print combat state at start of player phase
        _debug_print_combat_state("PLAYER_TURN_START", self.enemies)
        
        # Check for combat end (e.g., all enemies dead from start-of-turn effects)
        result = self._check_combat_end()
        if isinstance(result, GameStateResult):
            return result

        # Player action phase - wait for player to play cards, use potions, or end turn
        self.combat_state.current_phase = "player_action"

        while self.combat_state.current_phase == "player_action":
            self._build_player_action()

            result = game_state.execute_all_actions()
            
            if isinstance(result, GameStateResult) and result.state in ("COMBAT_WIN", "GAME_LOSE", "COMBAT_ESCAPE"):
                return result
            
            # Check for combat end (e.g., all enemies dead from card damage)
            result = self._check_combat_end()
            if isinstance(result, GameStateResult):
                return result

        # End player phase: trigger end-of-turn effects, discard hand
        return self._end_player_phase()
    
    def _build_player_action(self):
        """Build available player actions during player phase"""
        from engine.game_state import game_state
        actions = []

        # 1. Display combat information
        from localization import t, LocalStr
        from utils.types import CombatType

        # Get player info
        player = game_state.player
        enemies = self.enemies

        # Build status string
        status_parts = []
        status_parts.append(f"{t('ui.player_hp', default='Player HP')}: {player.hp}/{player.max_hp}")
        status_parts.append(f"{t('ui.player_block', default='Block')}: {player.block}")
        status_parts.append(f"{t('ui.player_energy', default='Energy')}: {player.energy}/{player.max_energy}")

        # Get enemy info
        for enemy in enemies:
            status_parts.append(f"{t('ui.enemy_hp', default='Enemy HP')}: {enemy.hp}/{enemy.max_hp}")
            status_parts.append(f"{t('ui.enemy_block', default='Block')}: {enemy.block}")

        actions.append(DisplayTextAction(text_key="combat.display"))

        # 2. Build SelectAction for cards in hand
        
        # 2. Build SelectAction for cards in hand
        hand = game_state.player.card_manager.get_pile("hand")
        options: List[Option] = []
        for card in hand:
            # can_play returns tuple (bool, Optional[str])
            can_play_result, reason = card.can_play()
            if can_play_result:
                # Use PlayCardAction to properly handle energy cost and card removal
                from actions.combat import PlayCardAction
                options.append(Option(
                    name=card.info(),
                    actions=[PlayCardAction(card=card, is_auto=True)]
                ))
        
        # 3. Build SelectAction for potions (if implemented)
        for potion in game_state.player.potions:
            options.append(Option(
                name=LocalStr(potion.info()),
                actions=potion.on_use()
            ))
            
        # 4. Add option to end turn
        options.append(Option(
            name=LocalStr("combat.end_turn"),
            actions=[EndTurnAction()]
        ))
        
        actions.append(SelectAction(
            options=options,
            prompt=LocalStr("combat.choose_action")
        ))
            
        game_state.action_queue.add_actions(actions)

    def _end_player_phase(self) -> BaseResult:
        """
        End player phase.

        Returns:
            GameStateResult if combat ends, None otherwise
        """
        from engine.game_state import game_state

         # Trigger end-of-turn effects
        # relics - powers - cards in hand
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_player_turn_end())
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_end())
        
        hand = game_state.player.card_manager.get_pile("hand")
        for card in hand:
            game_state.action_queue.add_actions(card.on_player_turn_end())

        # Discard hand (cards in hand are shuffled into discard pile)
        from actions.card import ExhaustCardAction
        if game_state.player.card_manager:
            hand = game_state.player.card_manager.get_pile("hand").copy()
            for card in hand:
                game_state.action_queue.add_action(DiscardCardAction(card=card, source_pile="hand"))

        # Reset player block
        game_state.player.block = 0

        return game_state.execute_all_actions()

    def execute_enemy_phase(self) -> BaseResult:
        """
        Execute enemy phase.

        Returns:
            GameStateResult if combat ends, None otherwise
        """
        from engine.game_state import game_state

        # DEBUG: Print combat state at start of enemy phase
        _debug_print_combat_state("ENEMY_PHASE_START", self.enemies)

        self.combat_state.current_phase = "enemy_action"

        # For each alive enemy, execute actions
        for enemy in self.enemies:
            if not enemy.is_dead():
                game_state.action_queue.add_actions(enemy.execute_intention())

        return game_state.execute_all_actions()
    
    def _remove_dead_enemies(self):
        """Remove dead enemies from the list"""
        self.enemies = [e for e in self.enemies if not e.is_dead()]
    
    def _check_combat_end(self) -> BaseResult:
        """Check if combat should end.
        
        Returns:
            GameStateResult("COMBAT_WIN") if all enemies are dead,
            GameStateResult("COMBAT_LOSE") if player is dead,
            NoneResult otherwise
        """
        from engine.game_state import game_state
        
        # Remove dead enemies first
        self._remove_dead_enemies()
        
        # Check if all enemies are dead
        if not self.enemies or all(e.is_dead() for e in self.enemies):
            print(f"\n[COMBAT END] COMBAT_WIN - All enemies defeated!")
            return GameStateResult("COMBAT_WIN")
        
        # Check if player is dead
        if game_state.player.is_dead():
            print(f"\n[COMBAT END] GAME_LOSE - Player defeated!")
            return GameStateResult("GAME_LOSE")
        
        return NoneResult()
    
    def _init_combat(self):
        """Initialize combat state"""
        from engine.game_state import game_state
        
        # Set current combat reference
        game_state.current_combat = self
        
        # Reset and setup combat state
        self.combat_state.reset_combat_info()
        
        # Reset card manager for combat (initialize draw pile from deck)
        if hasattr(game_state.player, 'card_manager'):
            game_state.player.card_manager.reset_for_combat()
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # Trigger combat start effects (relics)
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_combat_start(
                player=game_state.player,
                entities=self.enemies
            ))
        
        # Trigger combat start effects for enemies
        for enemy in self.enemies:
            enemy.on_combat_start(floor=game_state.current_floor)
        
        # Reset combat flags
        self.combat_ended = False
        self.player_turn_ended = False
        
        # todo: prepare innate cards to top of draw_pile

    def _start_player_turn(self):
        """Start player turn - draw cards, reset energy, trigger start-of-turn effects"""
        from engine.game_state import game_state
        # Draw cards
        draw_count = game_state.player.draw_count  # todo: modified by relics/powers
        if draw_count > 0:
            from actions.card import DrawCardsAction
            game_state.action_queue.add_action(DrawCardsAction(count=draw_count))

        # Reset energy
        game_state.player.energy = game_state.player.max_energy

        # Increment turn counter
        self.combat_state.combat_turn += 1
        self.combat_state.current_phase = "player_action"
        
        # relics - powers
        for relic in game_state.player.relics:
            game_state.action_queue.add_actions(relic.on_player_turn_start())
        for power in game_state.player.powers:
            game_state.action_queue.add_actions(power.on_turn_start())
        # enemies
        for enemy in self.enemies:
            enemy.on_player_turn_start()
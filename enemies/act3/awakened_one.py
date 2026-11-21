"""Awakened One - Act 3 Boss."""
from engine.random_streams import get_rng

from enemies.act3.awakened_one_intentions import (
    Slash,
    SoulStrike,
    Rebirth,
    DarkEcho,
    Sludge,
    Tackle,
)
from enemies.base import Enemy
from powers.definitions.regeneration import RegenerationPower
from powers.definitions.curiosity import CuriosityPower
from powers.definitions.strength import StrengthPower
from utils.types import EnemyType


class AwakenedOne(Enemy):
    """Awakened One is a Boss found at the end of Act 3.
    
    Phase One:
    - Always starts with Slash
    - Soul Strike (25%), Slash (75%)
    - No Slash 3x in a row, no Soul Strike 2x in a row
    
    Phase Two:
    - Triggered when HP reaches 0
    - Rebirth: Heals to full HP, removes debuffs, loses Curiosity
    - Starts with Dark Echo
    - 50/50 Tackle or Sludge, neither 3x in a row
    """
    
    enemy_type = EnemyType.BOSS
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        hp = 320 if ascension >= 9 else 300
        super().__init__(hp_range=(hp, hp))
        self.add_intention(Slash(self))
        self.add_intention(SoulStrike(self))
        self.add_intention(Rebirth(self))
        self.add_intention(DarkEcho(self))
        self.add_intention(Sludge(self))
        self.add_intention(Tackle(self))
        
        self._phase = 1
    
    def on_combat_start(self, floor: int):
        """Initialize combat state with starting powers.
        
        Phase 1 starting powers:
        - Regeneration: 10 (15 on Ascension 19+)
        - Curiosity: 1 (2 on Ascension 19+)
        - Strength: 2 on Ascension 4+
        """
        self._phase = 1
        super().on_combat_start(floor)
        
        # Get ascension level from game state
        from engine.game_state import game_state
        ascension = game_state.ascension
        
        # Regeneration: 10 normally, 15 on A19+
        # Note: RegenerationPower uses duration to determine heal amount
        # (amount_equals_duration=True), so we pass regen_amount as duration
        regen_amount = 15 if ascension >= 19 else 10
        self.add_power(RegenerationPower(duration=regen_amount, owner=self))
        
        # Curiosity: 1 normally, 2 on A19+
        curiosity_amount = 2 if ascension >= 19 else 1
        self.add_power(CuriosityPower(amount=curiosity_amount, owner=self))
        
        # Strength: 2 on A4+
        if ascension >= 4:
            self.add_power(StrengthPower(amount=2, owner=self))
    
    def is_dead(self) -> bool:
        """Only dead when HP <= 0 in phase 2.
        
        In phase 1, reaching 0 HP triggers rebirth instead of death.
        """
        return self._phase == 2 and self.hp <= 0

    @property
    def half_dead(self) -> bool:
        return self._phase == 1 and self.hp <= 0

    def on_hp_depleted(self) -> None:
        if self.half_dead:
            self.current_intention = self.intentions["Rebirth"]

    def after_hp_depleted(self) -> None:
        if self.half_dead:
            self.powers = [
                power for power in self.powers
                if getattr(power, "is_buff", True)
                and getattr(power, "name", "") not in {"Curiosity", "Unawakened", "Shackled"}
            ]
            from actions.card_play_lifecycle import ClearPendingCardPlaysAction
            from engine.runtime_api import add_action
            add_action(ClearPendingCardPlaysAction(), to_front=True)
    
    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if self.half_dead:
            move = "Rebirth"
        elif self._phase == 1:
            if not history:
                move = "Slash"
            elif roll < 25:
                move = "Slash" if history[-1] == "Soul Strike" else "Soul Strike"
            else:
                move = "Soul Strike" if history[-2:] == ["Slash", "Slash"] else "Slash"
        elif not history or history[-1] == "Rebirth":
            move = "Dark Echo"
        elif roll < 50:
            move = "Tackle" if history[-2:] == ["Sludge", "Sludge"] else "Sludge"
        else:
            move = "Sludge" if history[-2:] == ["Tackle", "Tackle"] else "Tackle"
        return self.intentions[move]

    def on_death(self) -> None:
        from actions.combat import RemoveEnemyAction
        from enemies.act1.cultist import Cultist
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        super().on_death()
        combat = game_state.current_combat
        if self._phase == 2 and combat is not None:
            add_actions([
                RemoveEnemyAction(enemy) for enemy in combat.enemies
                if isinstance(enemy, Cultist) and enemy.is_alive
            ])

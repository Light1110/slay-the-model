from engine.random_streams import StreamRandom, get_rng
# -*- coding: utf-8 -*-
from engine.runtime_api import add_action, add_actions
"""Looter - Common enemy in Act 1 and Act 2.

Steals gold when attacking and tries to escape after a few turns.
"""

from typing import TYPE_CHECKING, cast

from enemies.base import Enemy
from enemies.act1.looter_intentions import (
    LooterMugIntention,
    LooterLungeIntention,
    LooterSmokeBombIntention,
    LooterEscapeIntention
)
from powers.definitions.thievery import ThieveryPower
from utils.registry import register
from utils.types import EnemyType

if TYPE_CHECKING:
    from enemies.intention import Intention
    from actions.base import Action


@register("enemy")
@register("looter")
class Looter(Enemy):
    """Looter - Quick thief that steals gold and escapes.
    
    Pattern:
    - Uses Mug for the first 2 turns
    - Has a 50% chance to use Lunge or 50% chance to use Smoke Bomb
    - If Lunge is used on turn 3, it will then use Smoke Bomb next
    - The turn after Smoke Bomb has been used, it will Escape
    
    Attributes:
        HP: 44-48 (46-50 on Ascension 7+)
        Powers: Thievery 15 (20 on Ascension 7+)
    """
    
    enemy_type = EnemyType.NORMAL
    roll_fixed_opening_intention = True
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        super().__init__(
            hp_range=(46, 50) if self.ascension >= 7 else (44, 48)
        )
        
        # Turn tracking for AI pattern
        self._turn_count = 0
        self._used_lunge = False
        self._used_smoke_bomb = False
        self._use_smoke_after_mug: bool | None = None
        
        # Register intentions
        self.add_intention(LooterMugIntention(self))
        self.add_intention(LooterLungeIntention(self))
        self.add_intention(LooterSmokeBombIntention(self))
        self.add_intention(LooterEscapeIntention(self))
        self.intentions["mug"].base_damage = 11 if self.ascension >= 2 else 10
        self.intentions["lunge"].base_damage = 14 if self.ascension >= 2 else 12
    
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts - apply Thievery power."""
        super().on_combat_start(floor)
        
        thievery_amount = 20 if self.ascension >= 17 else 15
        thievery = ThieveryPower(amount=thievery_amount, owner=self)
        self.add_power(thievery)
        mug_intention = self.intentions.get("mug")
        if mug_intention is not None:
            mug_intention.base_amount = thievery_amount
    
    def determine_next_intention(self, floor: int = 1) -> 'Intention':
        """Determine next intention based on Looter's pattern.
        
        Pattern:
        - Turns 1-2: Always Mug
        - Turn 3: 50% Lunge or 50% Smoke Bomb
        - After Lunge (if on turn 4): Smoke Bomb
        - After Smoke Bomb: Escape
        
        Returns:
            The next Intention to execute
        """
        next_turn = self._turn_count + 1  # What turn we're planning for
        
        # After Smoke Bomb, always Escape
        if self._used_smoke_bomb:
            return self.intentions["escape"]
        
        # After Lunge on turn 3, use Smoke Bomb
        if self._used_lunge and next_turn == 4:
            return self.intentions["smoke_bomb"]
        
        # Turns 1-2: Always Mug
        if next_turn <= 2:
            return self.intentions["mug"]
        
        # Turn 3: 50% Lunge or 50% Smoke Bomb
        if next_turn == 3:
            use_smoke = self._use_smoke_after_mug
            if use_smoke is None:
                use_smoke = cast(StreamRandom, get_rng("ai")).random_boolean(0.5)
            return self.intentions["smoke_bomb" if use_smoke else "lunge"]
        
        # Turn 4+ (if we got here without smoke bomb somehow): Smoke Bomb then Escape
        return self.intentions["smoke_bomb"]
    
    def execute_intention(self) -> None:
        """Execute the current intention and update turn tracking."""
        if self.current_intention is None:
            return
        if self.current_intention.name == "mug":
            rng = cast(StreamRandom, get_rng("ai"))
            if self._turn_count == 0:
                rng.random_boolean(0.6)
            elif self._turn_count == 1:
                self._use_smoke_after_mug = rng.random_boolean(0.5)
        # Update turn tracking before executing
        self._turn_count += 1
        
        # Track which moves were used
        if self.current_intention.name == "lunge":
            self._used_lunge = True
        elif self.current_intention.name == "smoke_bomb":
            self._used_smoke_bomb = True
        
        # Execute the intention
        super().execute_intention()
    
    def on_death(self) -> None:
        """Called when Looter dies - return stolen gold."""
        actions = []
        
        # Return stolen gold via Thievery power
        thievery = self.get_power("ThieveryPower")
        if thievery and hasattr(thievery, 'on_remove'):
            thievery.on_remove()
        
        from engine.game_state import game_state
        
        add_actions(actions)
        

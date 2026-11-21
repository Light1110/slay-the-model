"""
Mugger - Normal enemy (Act 2)
Thief that steals gold and escapes.
"""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from enemies.base import Enemy
from powers.definitions.thievery import ThieveryPower
from utils.types import EnemyType
from enemies.act2.mugger_intentions import (
    MugIntention, LungeIntention, SmokeBombIntention, EscapeIntention
)


class Mugger(Enemy):
    """Mugger - Thief enemy that steals gold and escapes."""
    
    enemy_type = EnemyType.NORMAL
    roll_fixed_opening_intention = True
    select_intention_after_enemy_turn = True
    
    # Same pattern as Looter (from Act 1)
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        super().__init__(hp_range=(50, 54) if self.ascension >= 7 else (48, 52))
        self._use_smoke_after_mug = False
        
        # Register intentions
        self.add_intention(MugIntention(self))
        self.add_intention(LungeIntention(self))
        self.add_intention(SmokeBombIntention(self))
        self.add_intention(EscapeIntention(self))
        if self.ascension >= 2:
            self.intentions["mug"].base_damage = 11
            self.intentions["lunge"].base_damage = 18
        if self.ascension >= 17:
            self.intentions["smoke_bomb"].base_block = 17
        
    def on_combat_start(self, floor: int = 1) -> None:
        """Called when combat starts - apply Thievery power."""
        super().on_combat_start(floor)
        
        # Apply Thievery power (15 gold on normal, 20 on Ascension 7+)
        thievery_amount = 20 if self.ascension >= 17 else 15
        thievery = ThieveryPower(amount=thievery_amount, owner=self)
        self.add_power(thievery)
        mug_intention = self.intentions.get("mug")
        if mug_intention is not None:
            mug_intention.base_amount = thievery_amount
    
    def execute_intention(self) -> None:
        current = self.current_intention
        if current is not None and current.name in {"mug", "lunge"}:
            rng = cast(StreamRandom, get_rng("ai"))
            # Voice and dialogue choices consume the shared AI stream.
            rng.randint(0, 2)
            if current.name == "mug" and self.history_intentions == ["mug"]:
                rng.random_boolean(0.6)
                self._use_smoke_after_mug = rng.random_boolean(0.5)
        super().execute_intention()

    def determine_next_intention(self, floor: int = 1):
        history = self.history_intentions
        if len(history) < 2:
            move = "mug"
        elif history[-1] == "mug":
            move = "smoke_bomb" if self._use_smoke_after_mug else "lunge"
        elif history[-1] == "lunge":
            move = "smoke_bomb"
        else:
            move = "escape"
        return self.intentions[move]

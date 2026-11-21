"""Writhing Mass enemy for Slay the Model."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng

from enemies.act3.writhing_mass_intentions import (
    MultiHit, DebuffAttackMass, BigHit, BlockAttackMass, ParasiteIntention
)
from enemies.base import Enemy
from utils.types import EnemyType

class WrithingMass(Enemy):
    """Writhing Mass is a normal Enemy found in Act 3.
    
    Special mechanics:
    Changes intention after qualifying attacks and can implant Parasite once.
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        hp = 175 if game_state.ascension >= 7 else 160
        super().__init__(hp_range=(hp, hp))
        self._first_move = True
        
        # Register intentions
        self.add_intention(MultiHit(self))
        self.add_intention(DebuffAttackMass(self))
        self.add_intention(BigHit(self))
        self.add_intention(BlockAttackMass(self))
        self.add_intention(ParasiteIntention(self))
    
    def determine_next_intention(self, floor: int):
        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        history = self.history_intentions
        if self._first_move:
            self._first_move = False
            if roll < 33:
                move = "Multi Hit"
            elif roll < 66:
                move = "Block Attack"
            else:
                move = "Debuff Attack"
            return self.intentions[move]

        last = history[-1] if history else None
        used_parasite = "Parasite" in history
        while True:
            if roll < 10:
                if last != "Big Hit":
                    return self.intentions["Big Hit"]
                roll = rng.randint(10, 99)
            elif roll < 20:
                if not used_parasite:
                    return self.intentions["Parasite"]
                if rng.random_boolean(0.1):
                    return self.intentions["Big Hit"]
                roll = rng.randint(20, 99)
            elif roll < 40:
                if last != "Debuff Attack":
                    return self.intentions["Debuff Attack"]
                bounds = (0, 19) if rng.random_boolean(0.4) else (40, 99)
                roll = rng.randint(*bounds)
            elif roll < 70:
                if last != "Multi Hit":
                    return self.intentions["Multi Hit"]
                if rng.random_boolean(0.3):
                    return self.intentions["Block Attack"]
                roll = rng.randint(0, 39)
            elif last != "Block Attack":
                return self.intentions["Block Attack"]
            else:
                roll = rng.randint(0, 69)

    def on_combat_start(self, floor: int = 1) -> None:
        from powers.definitions.malleable import MalleablePower
        from powers.definitions.reactive import ReactivePower

        self._first_move = True
        super().on_combat_start(floor)
        self.add_power(MalleablePower(amount=3, owner=self))
        self.add_power(ReactivePower(owner=self))

    def on_physical_attack_taken(self, damage: int, source=None, card=None, damage_type: str = "physical") -> None:
        from actions.base import LambdaAction
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        if damage <= 0 or source is None or not self.is_alive or not self.has_power("Reactive"):
            return

        def roll_after_hit():
            if self.is_alive:
                self._select_intention(game_state.current_floor)

        add_action(LambdaAction(func=roll_after_hit))

"""Spire Spear - Act 4 Elite."""
from engine.random_streams import StreamRandom, get_rng

from typing import TYPE_CHECKING, Optional, cast

from enemies.act4.spire_spear_intentions import BurnStrike, Piercer, Skewer
from enemies.base import Enemy
from utils.types import EnemyType

if TYPE_CHECKING:
    from engine.back_attack_manager import BackAttackManager


class SpireSpear(Enemy):
    """Spire Spear is an Elite found in Act 4.

    Pattern:
    - Turn 1: Burn Strike
    - Every 3 turns from turn 2: Skewer
    - Other turns: 50/50 pair order of Burn Strike and Piercer

    Special mechanics (with Spire Shield):
    - BackAttackPower can transfer to Spear when player targets Shield
    - When either enemy dies, BackAttack and Surrounded are removed
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        hp = 180 if self.ascension >= 8 else 160
        super().__init__(hp_range=(hp, hp))
        self.add_intention(BurnStrike(self))
        self.add_intention(Skewer(self))
        self.add_intention(Piercer(self))

        self._back_attack_manager: Optional["BackAttackManager"] = None
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        from powers.definitions.artifact import ArtifactPower

        super().on_combat_start(floor)
        self.add_power(ArtifactPower(amount=2 if self.ascension >= 18 else 1, owner=self))
    
    def on_death(self):
        """Clean up BackAttack mechanics when Spear dies."""
        if self._back_attack_manager is not None:
            self._back_attack_manager.on_enemy_death(self)
            self._back_attack_manager = None
        super().on_death()
    
    def determine_next_intention(self, floor: int) -> str:
        rng = cast(StreamRandom, get_rng("ai"))
        rng.randint(0, 99)
        phase = len(self.history_intentions) % 3
        if phase == 0:
            return "Piercer" if self.history_intentions[-1:] == ["Burn Strike"] else "Burn Strike"
        if phase == 1:
            return "Skewer"
        return "Piercer" if rng.random_boolean() else "Burn Strike"

"""Spire Shield - Act 4 Elite."""
from engine.random_streams import StreamRandom, get_rng

from typing import TYPE_CHECKING, Optional, cast

from enemies.act4.spire_shield_intentions import Bash, Fortify, Smash
from enemies.base import Enemy
from utils.types import EnemyType

if TYPE_CHECKING:
    from engine.back_attack_manager import BackAttackManager


class SpireShield(Enemy):
    """Spire Shield is an Elite found in Act 4.

    Pattern:
    - Every 3 turns starting from turn 3: Smash
    - Otherwise 50/50 pair order of Bash and Fortify

    Special mechanics (with Spire Spear):
    - Player starts with Surrounded debuff
    - Shield starts with BackAttackPower (+50% damage)
    - When player targets Shield, BackAttack transfers to Spear
    - When either enemy dies, BackAttack and Surrounded are removed
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        hp = 125 if self.ascension >= 8 else 110
        super().__init__(hp_range=(hp, hp))
        self.add_intention(Bash(self))
        self.add_intention(Fortify(self))
        self.add_intention(Smash(self))

        self._back_attack_manager: Optional["BackAttackManager"] = None
    
    def on_combat_start(self, floor: int):
        """Initialize combat state and BackAttack mechanics."""
        from powers.definitions.artifact import ArtifactPower

        super().on_combat_start(floor)
        self.add_power(ArtifactPower(amount=2 if self.ascension >= 18 else 1, owner=self))
        
        # Initialize BackAttack manager if Spear is present
        self._init_back_attack_mechanics()
    
    def _init_back_attack_mechanics(self):
        """Set up Surrounded/BackAttack mechanics with Spire Spear."""
        from engine.back_attack_manager import BackAttackManager
        from engine.game_state import game_state
        
        combat = getattr(game_state, "current_combat", None)
        if combat is None:
            return
        
        # Find Spire Spear in combat
        spear = None
        for enemy in combat.enemies:
            if enemy.__class__.__name__ == "SpireSpear" and enemy.is_alive:
                spear = enemy
                break
        
        if spear is None:
            return  # No Spear, no special mechanics
        
        # Initialize manager with both enemies
        manager = BackAttackManager()
        manager.reset()
        manager.initialize(self, spear)
        
        # Give player Surrounded debuff
        player = game_state.player
        from powers.definitions.surrounded import SurroundedPower
        if not player.has_power("Surrounded"):
            player.add_power(SurroundedPower(owner=player))
        
        self._back_attack_manager = manager
        # Also store reference in Spear
        if hasattr(spear, "_back_attack_manager"):
            spear._back_attack_manager = manager
    
    def on_death(self):
        """Clean up BackAttack mechanics when Shield dies."""
        if self._back_attack_manager is not None:
            self._back_attack_manager.on_enemy_death(self)
            self._back_attack_manager = None
        super().on_death()
    
    def determine_next_intention(self, floor: int) -> str:
        rng = cast(StreamRandom, get_rng("ai"))
        rng.randint(0, 99)
        phase = len(self.history_intentions) % 3
        if phase == 0:
            return "Fortify" if rng.random_boolean() else "Bash"
        if phase == 1:
            return "Fortify" if self.history_intentions[-1] == "Bash" else "Bash"
        return "Smash"

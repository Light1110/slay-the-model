"""Gremlin enemy intentions.

Gremlin Gang is a 4-enemy encounter in Act 1. Each gremlin type has
different behavior:
- Fat Gremlin: Small damage + Weak
- Sneaky Gremlin: Medium damage
- Mad Gremlin: Small damage, gains Strength when hit
- Shield Gremlin: Block or damage
- Gremlin Wizard: Charges for big attack
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_actions

from typing import List

from actions.combat import (
    ApplyPowerAction,
    AttackAction,
    GainBlockAction,
)
from enemies.intention import Intention
from enemies.base import Enemy


class FatGremlinSmashIntention(Intention):
    """Fat Gremlin attacks for small damage and applies Weak."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("fat_gremlin_smash", enemy)
        self.base_damage = 4
        self.base_amount = 1  # Weak duration
    
    def execute(self) -> None:
        from engine.game_state import game_state
        from powers.definitions.frail import FrailPower
        from powers.definitions.weak import WeakPower

        player = game_state.player
        actions = [
            AttackAction(self.base_damage, player, self.enemy, "attack"),
            ApplyPowerAction(WeakPower(amount=1, duration=1, owner=player), player, source=self.enemy),
        ]
        if game_state.ascension >= 17:
            actions.append(ApplyPowerAction(FrailPower(amount=1, duration=1, owner=player), player, source=self.enemy))
        add_actions(actions)


class SneakyGremlinStabIntention(Intention):
    """Sneaky Gremlin attacks for medium damage."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("sneaky_gremlin_stab", enemy)
        self.base_damage = 9
    
    def execute(self) -> None:
        """Deal damage to player."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        )


class MadGremlinScratchIntention(Intention):
    """Mad Gremlin attacks for small damage."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("mad_gremlin_scratch", enemy)
        self.base_damage = 5
    
    def execute(self) -> None:
        """Deal damage to player."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        )


class ShieldGremlinProtectIntention(Intention):
    """Shield Gremlin gains block."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("shield_gremlin_protect", enemy)
        self.base_block = 6
    
    def execute(self) -> None:
        from engine.game_state import game_state

        combat = game_state.current_combat
        allies = [
            enemy for enemy in combat.enemies
            if enemy is not self.enemy and enemy.is_alive
            and (enemy.current_intention is None or enemy.current_intention.name != "escape")
        ] if combat is not None else []
        target = get_rng("ai").choice(allies) if allies else self.enemy
        add_actions([GainBlockAction(block=self.base_block, target=target, source=self.enemy)])


class ShieldGremlinBashIntention(Intention):
    """Shield Gremlin attacks for medium damage."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("shield_gremlin_bash", enemy)
        self.base_damage = 6
    
    def execute(self) -> None:
        """Deal damage to player."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        )


class GremlinWizardChargeIntention(Intention):
    """Gremlin Wizard charges up for a big attack."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("gremlin_wizard_charge", enemy)
        self.base_amount = 1  # Charge counter
    
    def execute(self) -> None:
        """Wizard charges - no action taken."""
        # Wizard just charges, no attack or block
class GremlinWizardUltimateBlastIntention(Intention):
    """Gremlin Wizard unleashes a big attack after charging."""
    
    def __init__(self, enemy: Enemy):
        super().__init__("gremlin_wizard_ultimate_blast", enemy)
        self.base_damage = 25
    
    def execute(self) -> None:
        """Deal massive damage to player."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        )

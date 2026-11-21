"""Gremlin enemies for the Gremlin Gang encounter.

Gremlin Gang is a 4-enemy encounter in Act 1 featuring 4 random gremlins
chosen from the 5 types defined here.

HP values based on Slay the Spire Ascension 0:
- Fat Gremlin: 13-17 HP
- Sneaky Gremlin: 9-12 HP
- Mad Gremlin: 9-12 HP
- Shield Gremlin: 12-15 HP
- Gremlin Wizard: 9-12 HP
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action

import random
from typing import Optional

from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.gremlin_intentions import (
    FatGremlinSmashIntention,
    SneakyGremlinStabIntention,
    MadGremlinScratchIntention,
    ShieldGremlinProtectIntention,
    ShieldGremlinBashIntention,
    GremlinWizardChargeIntention,
    GremlinWizardUltimateBlastIntention,
)


class FatGremlin(Enemy):
    """Fat Gremlin - deals damage and applies Weak.
    
    Behavior: Always uses Smash (4 damage + 1 Weak).
    HP: 13-17
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self, hp_range: tuple[int, int] | None = None):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range if hp_range is not None else ((14, 18) if ascension >= 7 else (13, 17)))
        self.add_intention(FatGremlinSmashIntention(self))
        self.intentions["fat_gremlin_smash"].base_damage = 5 if ascension >= 2 else 4
    
    def determine_next_intention(self, current_floor: int = 1):
        """Fat Gremlin always smashes."""
        get_rng("ai").randint(0, 99)
        self.current_intention = self.intentions["fat_gremlin_smash"]


class SneakyGremlin(Enemy):
    """Sneaky Gremlin - deals medium damage.
    
    Behavior: Always uses Stab (9 damage).
    HP: 9-12
    """
    
    enemy_type = EnemyType.NORMAL
    roll_fixed_opening_intention = True
    
    def __init__(self, hp_range: tuple[int, int] = (10, 14)):
        super().__init__(hp_range) # todo: 11-15 a7
        self.add_intention(SneakyGremlinStabIntention(self))
    
    def determine_next_intention(self, current_floor: int = 1):
        """Sneaky Gremlin always stabs."""
        self.current_intention = self.intentions["sneaky_gremlin_stab"]


class MadGremlin(Enemy):
    """Mad Gremlin - deals small damage, gains Strength when hit.
    
    Behavior: Always uses Scratch (5 damage). Gains 1 Strength when
    taking damage from an attack (enraged behavior).
    HP: 9-12
    """
    
    enemy_type = EnemyType.NORMAL
    roll_fixed_opening_intention = True
    
    def __init__(self, hp_range: tuple[int, int] = (8, 15)):
        super().__init__(hp_range)
        self.add_intention(MadGremlinScratchIntention(self))
    
    def determine_next_intention(self, current_floor: int = 1):
        """Mad Gremlin always scratches."""
        self.current_intention = self.intentions["mad_gremlin_scratch"]
    
    def on_take_damage(self, damage: int, source=None):
        """Gain 1 Strength when taking damage from attacks."""
        from engine.game_state import game_state
        from actions.combat import ApplyPowerAction
        
        # Call parent to actually take damage
        result = super().on_take_damage(damage, source)
        
        # Gain Strength when damaged by player attacks
        if damage > 0 and source == game_state.player:
            add_action(
                ApplyPowerAction(
                    power="strength",
                    target=self,
                    amount=1,
                    duration=-1,
                )
            )
        
        return result


class ShieldGremlin(Enemy):
    """Protect allies until left alone."""

    select_intention_after_enemy_turn = True
    roll_fixed_opening_intention = True

    def __init__(self, hp_range: tuple[int, int] | None = None):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range if hp_range is not None else ((13, 17) if ascension >= 7 else (12, 15)))
        self.add_intention(ShieldGremlinProtectIntention(self))
        self.add_intention(ShieldGremlinBashIntention(self))
        self.intentions["shield_gremlin_protect"].base_block = 11 if ascension >= 17 else 8 if ascension >= 7 else 7
        self.intentions["shield_gremlin_bash"].base_damage = 8 if ascension >= 2 else 6

    def determine_next_intention(self, current_floor: int = 1):
        from engine.game_state import game_state

        combat = game_state.current_combat
        has_ally = combat is not None and any(
            ally is not self and ally.is_alive for ally in combat.enemies
        )
        history = self.history_intentions
        protect = not history or (has_ally and history[-1] != "shield_gremlin_bash")
        return self.intentions["shield_gremlin_protect" if protect else "shield_gremlin_bash"]


class GremlinWizard(Enemy):
    """Charge three times before unleashing a blast."""

    select_intention_after_enemy_turn = True
    roll_fixed_opening_intention = True

    def __init__(self, hp_range: tuple[int, int] | None = None):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        super().__init__(hp_range if hp_range is not None else ((22, 26) if self.ascension >= 7 else (21, 25)))
        self.add_intention(GremlinWizardChargeIntention(self))
        self.add_intention(GremlinWizardUltimateBlastIntention(self))
        self.intentions["gremlin_wizard_ultimate_blast"].base_damage = 30 if self.ascension >= 2 else 25

    def determine_next_intention(self, floor: int = 1):
        history = self.history_intentions
        charge = "gremlin_wizard_charge"
        blast = "gremlin_wizard_ultimate_blast"
        ready = history[-3:] == [charge] * 3 or (self.ascension >= 17 and history[-1:] == [blast])
        return self.intentions[blast if ready else charge]


def create_leader_minion(rng_domain: str) -> Enemy:
    """Draw from the weighted pool used for a leader's initial and summoned allies."""
    pool = (
        MadGremlin, MadGremlin, SneakyGremlin, SneakyGremlin,
        FatGremlin, FatGremlin, ShieldGremlin, GremlinWizard,
    )
    enemy = pool[get_rng(rng_domain).randint(0, len(pool) - 1)]()
    enemy.is_minion = True
    return enemy

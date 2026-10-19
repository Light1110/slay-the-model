"""Writhing Mass enemy intentions for Slay the Model."""
from engine.runtime_api import add_action, add_actions

import random
from typing import List

from actions.combat import AttackAction, ApplyPowerAction, GainBlockAction
from enemies.intention import Intention
class MultiHit(Intention):
    """Writhing Mass Multi Hit intention - 7x3 damage."""
    
    def __init__(self, enemy):
        super().__init__("Multi Hit", enemy)
        from engine.game_state import game_state

        self.base_damage = 8 if game_state.ascension >= 17 else 7
        self.base_times = 3
    
    def execute(self) -> None:
        """Execute Multi Hit intention."""
        damage = self.base_damage
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            damage,
            game_state.player,
            self.enemy,
            "attack"
        ) for _ in range(self.base_times)]
        )


class DebuffAttackMass(Intention):
    """Writhing Mass Debuff Attack intention - damage + Weak + Vulnerable."""
    
    def __init__(self, enemy):
        super().__init__("Debuff Attack", enemy)
        from engine.game_state import game_state

        self.base_damage = 11 if game_state.ascension >= 17 else 10
    
    def execute(self) -> None:
        """Execute Debuff Attack intention."""
        damage = self.base_damage
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage,
                game_state.player,
                self.enemy,
                "attack"
            ),
            ApplyPowerAction("weak", game_state.player, 2, 2),
            ApplyPowerAction("vulnerable", game_state.player, 2, 2)
        ]
        )


class BigHit(Intention):
    """Writhing Mass Big Hit intention - 32 damage."""
    
    def __init__(self, enemy):
        super().__init__("Big Hit", enemy)
        from engine.game_state import game_state

        self.base_damage = 35 if game_state.ascension >= 17 else 32
    
    def execute(self) -> None:
        """Execute Big Hit intention."""
        damage = self.base_damage
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            damage,
            game_state.player,
            self.enemy,
            "attack"
        )]
        )


class BlockAttackMass(Intention):
    """Writhing Mass Block Attack intention - damage + block."""
    
    def __init__(self, enemy):
        super().__init__("Block Attack", enemy)
        from engine.game_state import game_state

        self.base_damage = 16 if game_state.ascension >= 17 else 15
        self.base_block = 16
    
    def execute(self) -> None:
        """Execute Block Attack intention."""
        damage = self.base_damage
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage,
                game_state.player,
                self.enemy,
                "attack"
            ),
            GainBlockAction(self.base_block, self.enemy)
        ]
        )


class ParasiteIntention(Intention):
    """Writhing Mass Parasite intention - adds Parasite to deck."""
    
    def __init__(self, enemy):
        super().__init__("Parasite", enemy)
    
    def execute(self) -> None:
        """Execute Parasite intention - permanently adds Parasite to deck."""
        from actions.card import AddCardAction
        from cards.colorless.parasite import Parasite
        
        from engine.game_state import game_state
        
        add_actions([AddCardAction(card=Parasite(), dest_pile="deck", source="enemy")])
        

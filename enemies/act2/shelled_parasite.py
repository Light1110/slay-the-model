"""
Shelled Parasite - Normal enemy (Act 2)
Armored parasite that heals itself.
"""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_actions
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.shelled_parasite_intentions import (
    DoubleStrikeIntention, LifeSuckIntention, FeltIntention, StunnedIntention
)


class ShelledParasite(Enemy):
    """Shelled Parasite - Armored parasite enemy."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(68, 72) # todo: 70-75 a7
        )
        
        # Track stun state (can only happen once)
        self._has_been_stunned = False
        
        # Life Suck heal flag (set by intention, consumed by on_damage_dealt)
        self.pending_life_suck_heal = False
        
        # Register intentions
        self.add_intention(DoubleStrikeIntention(self))
        self.add_intention(LifeSuckIntention(self))
        self.add_intention(FeltIntention(self))
        self.add_intention(StunnedIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        self._has_been_stunned = False
        super().on_combat_start(floor)
        
        # Add Plated Armor x 14
        from powers.definitions.plated_armor import PlatedArmorPower
        self.add_power(PlatedArmorPower(amount=14, owner=self))
        self.gain_block(14)
    
    def remove_power(self, power_or_name) -> None:
        had_armor = self.has_power("Plated Armor")
        super().remove_power(power_or_name)
        if had_armor and not self._has_been_stunned and self.is_alive and not self.has_power("Plated Armor"):
            self._has_been_stunned = True
            self.current_intention = self.intentions["stunned"]

    def on_damage_dealt(self, damage: int, target=None, source=None, card=None, damage_type: str = "direct"):
        """Handle Life Suck healing when damage is dealt."""
        from typing import List
        from actions.base import Action
        
        if self.pending_life_suck_heal and damage > 0:
            from actions.combat import HealAction
            self.pending_life_suck_heal = False
            from engine.game_state import game_state
            add_actions([HealAction(amount=damage, target=self)])
            return
        return

    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        history = self.history_intentions
        if not history:
            if game_state.ascension >= 17:
                return self.intentions["felt"]
            return self.intentions["double_strike" if rng.random_boolean() else "life_suck"]

        if roll < 20:
            if history[-1] != "felt":
                return self.intentions["felt"]
            roll = rng.randint(20, 99)

        if roll < 60:
            move = "life_suck" if history[-2:] == ["double_strike", "double_strike"] else "double_strike"
        else:
            move = "double_strike" if history[-2:] == ["life_suck", "life_suck"] else "life_suck"
        return self.intentions[move]

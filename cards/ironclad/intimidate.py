"""
Ironclad Uncommon Skill card - Intimidate
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Intimidate(Card):
    """Apply Weak to ALL enemies"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"weak": 1}

    upgrade_magic = {"weak": 2}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Apply weak debuff to all enemies
        weak_amount = self.get_magic_value("weak")
        assert game_state.current_combat is not None
        for enemy in game_state.current_combat.enemies:
            if enemy.hp > 0:
                actions.append(ApplyPowerAction(target=enemy, power="weak", amount=weak_amount))

        return actions

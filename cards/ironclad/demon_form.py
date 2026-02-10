"""
Ironclad Rare Power card - Demon Form
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DemonForm(Card):
    """At the end of your turn, gain 2 Strength"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    base_magic = {"strength_per_turn": 2}

    upgrade_magic = {"strength_per_turn": 3}
    
    # todo: ApplyPowerAction: DemonFormPower

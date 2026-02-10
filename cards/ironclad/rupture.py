"""
Ironclad Uncommon Power card - Rupture
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Rupture(Card):
    """Whenever you lose HP from a card, gain 1/2 Strength"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"strength_gain": 1}

    upgrade_magic = {"strength_gain": 2}
    
    # todo: ApplyPowerAction: JuggernautPower

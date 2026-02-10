"""
Ironclad Uncommon Power card - Feel No Pain
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FeelNoPain(Card):
    """Whenever you exhaust one card, gain 3/4 Block"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"block_per_exhaust": 3}

    upgrade_magic = {"block_per_exhaust": 4}
    
    # todo: ApplyPowerAction: DarkEmbracePower

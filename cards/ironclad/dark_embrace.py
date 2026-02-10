"""
Ironclad Uncommon Power card - Dark Embrace
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DarkEmbrace(Card):
    """Whenever a card is Exhausted, draw 1"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 2
    upgrade_cost = 1
    
    # todo: ApplyPowerAction: DarkEmbracePower

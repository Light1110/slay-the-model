"""
Ironclad Uncommon Power card - Metallicize
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Metallicize(Card):
    """Gain 3/4 block at the end of your turn"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"auto_block": 3}
    upgrade_magic = {"auto_block": 4}

    # todo: ApplyPowerAction: JuggernautPower

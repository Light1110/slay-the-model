"""
Ironclad Rare Power card - Juggernaut
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Juggernaut(Card):
    """Whenever you gain Block, deal 5 damage to ALL enemies"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"damage_per_block": 5}

    upgrade_magic = {"damage_per_block": 7}

    # todo: ApplyPowerAction: JuggernautPower

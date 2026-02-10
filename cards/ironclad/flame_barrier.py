"""
Ironclad Uncommon Power card - Flame Barrier
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FlameBarrier(Card):
    """Gain block, deal damage to enemies that attack"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_block = 12

    upgrade_block = 16
    
    # todo: ApplyPowerAction: FlameBarrierPower

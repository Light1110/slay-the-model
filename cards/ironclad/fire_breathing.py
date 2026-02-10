"""
Ironclad Uncommon Power card - Fire Breathing
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class FireBreathing(Card):
    """Whenever you draw a status card, deal 7/10 damage to ALL enemies"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"damage_on_status": 7}
    upgrade_magic = {"damage_on_status": 10}
    
    # todo: ApplyPowerAction: FireBreathingPower

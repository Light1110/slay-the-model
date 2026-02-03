"""
Ironclad's Strike card
"""
from cards.base import Card
from utils.registry import register
from utils.types import RarityType

@register("card")
class Strike(Card):
    """Deal damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = RarityType.STARTER
    
    # Card values
    base_cost = 1
    base_damage = 6
    base_attack_times = 1
    
    # Upgrade values
    upgrade_damage = 9
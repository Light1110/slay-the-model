"""
Ironclad's Strike card
"""
from cards.base import Card
from cards.registry import register


@register("ironclad")
class Strike(Card):
    """Deal damage"""
    
    # Card attributes
    card_type = "Attack"
    rarity = "Starter"
    
    # Card values
    base_cost = 1
    base_damage = 6
    base_attack_times = 1
    
    # Upgrade values
    upgrade_damage = 9
    
    # Description
    description_template = "Deal {damage} damage."
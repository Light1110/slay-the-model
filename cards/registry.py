"""
Card registry and creation system.

This module handles card registration and instantiation with namespace support.
"""

from typing import Dict, Type, Optional
from cards.namespaces import register_card, get_card_class, CARD_NAMESPACES
from cards.base import Card


# Global registry decorator
def register(namespace: str = None):
    """Decorator to register a card class to a namespace."""
    def decorator(card_class: Type[Card]):
        card_id = register_card(card_class, namespace)
        card_class.card_id = card_id  # Store the full ID on the class
        return card_class
    return decorator


def create_card(card_id: str, card_name: str = None, upgrade_level: int = 0) -> Optional[Card]:
    """Create a card instance by its ID.
    
    Args:
        card_id: Full card ID (namespace.card_name) or just card_name
        card_name: Optional display name override
        upgrade_level: Initial upgrade level
        
    Returns:
        Card instance or None if not found
    """
    card_class = get_card_class(card_id)
    if not card_class:
        return None
    
    # Create card instance
    card = card_class.__new__(card_class)
    
    # Initialize with custom name if provided
    if card_name:
        card.__init__(card_name=card_name)
    else:
        card.__init__()
    
    # Apply upgrades if needed
    if upgrade_level > 0:
        for _ in range(upgrade_level):
            if not card.upgrade():
                break
    
    return card


def get_all_card_ids() -> list:
    """Get all registered card IDs."""
    all_ids = []
    for namespace_cards in CARD_NAMESPACES.values():
        all_ids.extend(namespace_cards.keys())
    return all_ids


def get_cards_by_namespace(namespace: str) -> Dict[str, Type[Card]]:
    """Get all card classes in a namespace."""
    return CARD_NAMESPACES.get(namespace, {}).copy()
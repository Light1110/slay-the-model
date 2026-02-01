"""
Card namespaces and color definitions.

Each namespace corresponds to a character's card set and has an associated color
for command-line display purposes.
"""

# Namespace to color mapping
NAMESPACE_COLORS = {
    "ironclad": "Red",
    "silent": "Green", 
    "defect": "Blue",
    "watcher": "Purple",
    "colorless": "Colorless",
    "curse": "Colorless",
    "status": "Colorless",
}

# Character to namespace mapping
CHARACTER_NAMESPACES = {
    "Ironclad": "ironclad",
    "Silent": "silent",
    "Defect": "defect",
    "Watcher": "watcher",
}

# Registry of cards by namespace
CARD_NAMESPACES = {namespace: {} for namespace in NAMESPACE_COLORS.keys()}


def get_namespace_for_character(character: str) -> str:
    """Get the namespace for a given character."""
    return CHARACTER_NAMESPACES.get(character, "colorless")


def get_color_for_namespace(namespace: str) -> str:
    """Get the color for a given namespace."""
    return NAMESPACE_COLORS.get(namespace, "Colorless")


def register_card(card_class, namespace: str = None):
    """Register a card class to a namespace."""
    if namespace is None:
        # Try to infer namespace from module path
        namespace = _namespace_from_module(card_class.__module__)
    
    if namespace not in CARD_NAMESPACES:
        raise ValueError(f"Unknown namespace: {namespace}")
    
    card_name = card_class.__name__
    card_id = f"{namespace}.{card_name}"
    
    # Store the card class with its full ID
    CARD_NAMESPACES[namespace][card_id] = card_class
    
    return card_id


def get_card_class(card_id: str):
    """Get a card class by its full ID (namespace.card_name)."""
    if "." not in card_id:
        # Try to find card in any namespace
        for namespace_cards in CARD_NAMESPACES.values():
            for full_id, card_class in namespace_cards.items():
                if full_id.endswith(f".{card_id}"):
                    return card_class
        return None
    
    namespace, card_name = card_id.split(".", 1)
    if namespace not in CARD_NAMESPACES:
        return None
    
    return CARD_NAMESPACES[namespace].get(card_id)


def list_cards_in_namespace(namespace: str):
    """List all card IDs in a namespace."""
    if namespace not in CARD_NAMESPACES:
        return []
    
    return list(CARD_NAMESPACES[namespace].keys())


def _namespace_from_module(module_path):
    """Extract namespace from module path.
    
    Expected module structure: cards.{namespace}.{filename}
    
    Args:
        module_path: Module path string or None
    """
    if not module_path:
        return "colorless"
    
    parts = module_path.split(".")
    if len(parts) >= 2 and parts[0] == "cards":
        # Check if the second part is a known namespace
        if len(parts) > 1 and parts[1] in NAMESPACE_COLORS:
            return parts[1]
    
    # Try to infer from folder structure
    import os
    module_file = module_path.replace(".", "/") + ".py"
    if os.path.exists(module_file):
        # Check parent directory
        parent_dir = os.path.dirname(module_file)
        if parent_dir and os.path.basename(parent_dir) in NAMESPACE_COLORS:
            return os.path.basename(parent_dir)
    
    return "colorless"
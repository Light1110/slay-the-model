# PROJECT KNOWLEDGE BASE - UTILS MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Utility functions for random selection, option management, and type safety.

## STRUCTURE
```
utils/
├── registry.py        # Registration system (@register decorator)
├── types.py          # Type enums (RoomType, CardType, RarityType, etc.)
├── option.py         # Option dataclass (name, actions)
└── random.py         # Random generation utilities
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Registration | utils/registry.py | Decorator for registering components |
| Type enums | utils/types.py | RoomType, CardType, RarityType, etc. |
| Options | utils/option.py | Option(name, actions) dataclass |
| Random utils | utils/random.py | get_random_card, get_random_relic, etc. |

## CODE MAP

### Registry System (utils/registry.py: 80 lines)

```python
# Registration decorator
def register(type_name: str):
    """Decorator to register a component"""
    def decorator(component_class):
        _registry[type_name][component_class.__name__] = component_class
        return component_class

# Global registries
_registry = {
    "room": {},      # Room types
    "event": {},     # Event types
    "card": {},      # Card types (by namespace)
    "enemy": {},     # Enemy types
    "relic": {},     # Relic types
    "potion": {},    # Potion types
}
```

### Type Enums (utils/types.py: 100 lines)

```python
# RoomType enum
class RoomType(Enum):
    MONSTER = "Monster"
    ELITE = "Elite"
    REST_SITE = "Rest Site"
    MERCHANT = "Merchant"
    UNKNOWN = "Unknown"
    TREASURE = "Treasure"
    BOSS = "Boss"
    EVENT = "Event"

# RarityType enum
class RarityType(Enum):
    COMMON = "Common"
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    SHOP = "Shop"  # Special shop-only rarity

# CardType enum
class CardType(Enum):
    ATTACK = "Attack"
    SKILL = "Skill"
    POWER = "Power"
    STATUS = "Status"
    CURSE = "Curse"
```

### Option Dataclass (utils/option.py: 35 lines)

```python
@dataclass
class Option:
    name: str
    actions: List Union[Action, List[Action]]  # Can be single action or list
```

### Random Utils (utils/random.py: 50 lines)

```python
def get_random_card(card_types, rarities, namespaces, excluded_ids):
    """Get random card matching criteria"""
    # Searches registered cards by namespace
    # Filters by card_type and rarity
    # Returns None if no match found

def get_random_relic(rarities, excluded_ids):
    """Get random relic matching criteria"""
    # Searches registered relics
    # Filters by rarity and excluded IDs
    # Returns None if no match found

def get_random_potion(rarities):
    """Get random potion matching rarity"""
    # Searches registered potions
    # Returns None if no match found
```

## CONVENTIONS

**Registration Pattern:**
- Components use @register("type") decorator
- Stored in global _registry dict by type
- Type-based lookup (e.g., _registry["room"])

**Namespace System:**
- Cards are registered with namespace prefix (e.g., cards.ironclad.Strike)
- Allows character-specific decks
- Namespace cards appear in namespace lookup

**Type Safety:**
- Strongly typed enums (RoomType, RarityType, CardType)
- Prevents string typos at registration time

**Anti-Patterns (THIS PROJECT):**
- NEVER: utils/types.py:100 - Use string literals for types (e.g., "Monster" vs RoomType.MONSTER.value)
- NEVER: Register components without @register decorator
- NEVER: Bypass namespace system for cards

## COMMANDS
```bash
# Run game (utils are imported throughout)
python __main__.py

# Run tests
pytest tests/test_rooms.py -v              # Utils used in tests
```

## NOTES
- Registry provides centralized component lookup
- Namespace system enables character-specific card sets
- Random utilities respect filtering and exclusion parameters
- Option class is a dataclass for type safety

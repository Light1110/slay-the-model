# PROJECT KNOWLEDGE BASE - CARDS MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Card system with namespace support and three-tier value system (base, combat, temp).

## STRUCTURE
```
cards/
├── base.py            # Base Card class with value system
├── ironclad/          # Ironclad character cards
├── silent/             # Silent character cards
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Card base | cards/base.py | Three-tier values (base, combat, temp) |
| Namespace | cards/*_character/ | Character-specific card definitions |
| Card types | cards/base.py | Attack, Skill, Power, Status, Curse |
| Value system | cards/base.py | base/base/temp for buffs, combat for damage |
| Upgrading | cards/base.py | can_upgrade(), upgrade() method |

## CODE MAP

### Base Card Class (cards/base.py: 200 lines)
```python
class Card(Localizable):
    def __init__(self, name: str, card_type: str, rarity: str = "Common"):
        self.name = name
        self.card_type = card_type  # Attack, Skill, Power, Status, Curse
        self.rarity = rarity  # Common, Uncommon, Rare
        
        # Three-tier value system
        self.base_value = 0
        self.combat_value = 0
        self.temp_value = 0
        
        # Cost
        self.energy_cost = 1
        self.block_value = 0
        self.vulnerable = 0
        
        # Other properties
        self.description = ""
        self.upgraded = False
        self.relics_required = []
    
    @property
    def value(self) -> int:
        """Get current value (base + combat + temp)"""
        return self.base_value + self.combat_value + self.temp_value
    
    def is_playable(self, energy: int, max_block: int) -> bool:
        """Check if card can be played"""
        if energy < self.energy_cost:
            return False
        if max_block > 0 and energy >= self.block_value:
            return False
        if self.vulnerable > 0 and max_block < self.vulnerable:
            return False
        return True
    
    def can_upgrade(self) -> bool:
        """Check if card can be upgraded"""
        return not self.upgraded and self.rarity != "Common"
```

### Card Types

```python
# CardType enum (utils/types.py)
ATTACK = "Attack"    # Deals damage
SKILL = "Skill"      # Provides effect without cost
POWER = "Power"      # Permanent effect (stat modifier)
STATUS = "Status"    # Temporary modifier (debuff/buff)
CURSE = "Curse"     # Negative permanent effect
```

### Namespace System

Cards are organized by character namespace:
```
cards/ironclad/    # Ironclad character cards
cards/silent/       # Silent character cards
```

Each namespace contains character-specific card definitions using @register("card") decorator.

### Value System

Three-tier value system for card modifications:
```python
# Base values: Permanent stat increases/decreases
# Combat values: Temporary modifications that reset each combat
# Temp values: Temporary modifications that reset when card leaves play

# Total value = base_value + combat_value + temp_value
```

### Upgrading System

```python
# Upgrade method (cards/base.py:210-230)
def upgrade(self) -> Card:
    """Upgrade card to its next tier"""
    if self.rarity == "Common":
        self.rarity = "Uncommon"
    elif self.rarity == "Uncommon":
        self.rarity = "Rare"
    self.upgraded = True
    self.description = f"{self.name}+"  # Updated automatically
```

### Card Playability

```python
# is_playable() checks (cards/base.py:140-155)
1. energy >= energy_cost
2. Enough block vs opponent's block (if vulnerable)
3. energy_cost not exceeded when vulnerable

# Vulnerable check: If self.vulnerable > 0 and max_block < self.vulnerable, can't play
```

## CONVENTIONS

**Card Registration:**
- All cards use @register("card") decorator in character namespace
- Namespace system supports character-specific decks
- CardManager loads cards by namespace via cards namespace

**Card Rarity:**
- Common: Can be upgraded to Uncommon → Rare
- Uncommon: Can be upgraded to Rare
- Rare: Cannot be upgraded further

**Cost System:**
- energy_cost: Energy required to play card
- block_value: Block value card provides
- vulnerable: Opponent damage multiplier
- Vulnerable check: Can't play if vulnerable and insufficient block

**Anti-Patterns (THIS PROJECT):**
- NEVER: cards/base.py:150-155 - if self.upgraded: self.description = f"{self.name}+" (manual)
- NEVER: Direct string access to card data - use card.name
- NEVER: Bypass is_playable() checks
- ALWAYS: cards/base.py:210-230 - upgrade() method updates rarity

## COMMANDS
```bash
# Run game
python __main__.py

# Run tests
pytest tests/test_cards.py -v               # Card system tests
```

## NOTES
- Value system allows flexible card modifications (buffs/debuffs)
- Combat values reset each new combat turn
- Temp values reset when card leaves play
- Namespace system enables character-specific decks

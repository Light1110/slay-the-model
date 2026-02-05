# POTIONS MODULE

## Overview
Potion system with targetable effects and rarity-based generation for combat consumables.

## Structure
```
potions/
├── base.py       # Potion base class (19 lines)
├── definations.py # Potion definitions (23KB)
└── __init__.py   # Namespace package
```

## Core Components

### `base.py` - Potion (19 lines)
**Base Potion Class:**
- `Localizable` mixin for localization
- `localization_prefix`: "potions"
- `rarity`: RarityType.COMMON (default)
- `category`: "Global" (potion category)
- `amount`: None (effect magnitude)

**Required Methods:**
- `on_use(target: Creature) -> List[Action]` - Apply potion effect, return actions

**Usage:**
- Potions used from inventory in combat
- Target可以是玩家或敌人，取决于类别
- Return list of actions to execute

### `definations.py` (23KB)
- Extensive potion definitions
- Contains all potion implementations
- Uses `on_use()` for effects

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Create potion | Inherit from `Potion` | Set `rarity` and `category` |
| Apply effect | Override `on_use(target)` | Return list of actions |
| Targeting | Use `target` parameter | Can be player or enemy |
| Localization | Use `self.local("name")` | Key: `potions.{ClassName}.name` |

## Conventions

**Potion Implementation:**
- Override `on_use(target)` to define effect
- Return `List[Action]` to execute (e.g., DealDamage, Heal)
- Set `category`: "Global" for self-target, "Enemy" for enemies
- Set `rarity` for loot pool weighting

**Target Types:**
- `Global`: Potions used on self (e.g., healing potions)
- `Enemy`: Potions used on enemies (e.g., damage potions)

## Anti-Patterns

**NEVER:**
- Return empty list from `on_use()` - potion does nothing
- Ignore target parameter - effect depends on who it's used on
- Mix combat and out-of-combat effects in same potion

**ALWAYS:**
- Return `List[Action]` from `on_use()`
- Check target type if needed (player vs enemy)
- Use `Localizable` mixin for all potions

## Code Map

```python
class FirePotion(Potion):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Enemy"
    
    def on_use(self, target: Creature) -> List[Action]:
        # Deal 20 damage to target
        return [actions.DealDamage(20, target=target)]
```

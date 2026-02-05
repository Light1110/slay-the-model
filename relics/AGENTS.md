# RELICS MODULE

## Overview
Relic system with event hooks for turn-based effects, damage modification, and combat triggers.

## Structure
```
relics/
├── base.py           # Relic base class (53 lines)
├── __init__.py       # Namespace package
├── global/            # Global relics
└── ironclad/         # Ironclad-specific relics
```

## Core Components

### `base.py` - Relic (53 lines)
**Base Relic Class:**
- `Localizable` mixin for localization
- `localization_prefix`: "relics"
- `rarity`: RarityType.COMMON (default)

**Event Hooks (empty by default, override in subclasses):**
- `on_player_turn_start(player, entities)` - Start of player turn
- `on_player_turn_end(player, entities)` - End of player turn
- `on_enemy_turn_start(enemy, player, entities)` - Start of enemy turn
- `on_enemy_turn_end(enemy, player, entities)` - End of enemy turn
- `on_card_play(card, player, entities)` - When card played
- `on_damage_dealt(damage, target, player, entities) -> int` - Modify outgoing damage
- `on_damage_taken(damage, source, player, entities)` - Handle incoming damage
- `on_heal(heal_amount, player, entities)` - When healing occurs
- `on_combat_start(player, entities)` - Combat begins
- `on_combat_end(player, entities)` - Combat ends
- `on_rest_site_enter(player, entities)` - Enter rest site

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Create relic | Inherit from `Relic` | Set `rarity` attribute |
| Add effect | Override event hook methods | Use `entities` to access game state |
| Localization | Use `self.local("name")` | Key: `relics.{ClassName}.name` |
| Mod damage | Return modified value from `on_damage_dealt()` | Original damage passed in |

## Conventions

**Relic Implementation:**
- Subclass `Relic` in character subdirs (ironclad, etc.)
- Override only relevant hooks
- Use `localization_prefix = "relics"` for consistent keys
- Set `rarity` class attribute (COMMON/UNCOMMON/RARE)

**Event Flow:**
- Hooks called by combat/room systems
- Use `entities` parameter to access game objects
- Damage modifiers return `int` (modified damage)

## Anti-Patterns

**NEVER:**
- Override all hooks - only implement needed ones
- Modify damage without returning value - return the modified damage
- Ignore `entities` parameter - may need player/enemies

**ALWAYS:**
- Use `Localizable` mixin for all relics
- Return damage modifiers from `on_damage_dealt()`/`on_damage_taken()`
- Use appropriate hooks (turn start/end, combat, etc.)

## Code Map

```python
class BurningBlood(Relic):
    localization_prefix = "relics"
    rarity = RarityType.COMMON
    
    def on_combat_end(self, player, entities):
        # Heal 6 HP at combat end
        player.heal(6)
```

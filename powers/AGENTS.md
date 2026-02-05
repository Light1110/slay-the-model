# POWERS MODULE

## Overview
Power system for temporary and permanent combat effects with duration tracking and damage modification.

## Structure
```
powers/
├── base.py       # Power base class (144 lines)
├── __init__.py   # Namespace package
└── ironclad/     # Character-specific powers
```

## Core Components

### `base.py` - Power (144 lines)
**Base Power Class:**
- `Localizable` mixin for localization
- `localization_prefix`: "powers"
- `amount`: Effect magnitude (0 default)
- `duration`: Turns until expiry (0 = permanent)
- `trigger_timing`: When power activates (turn_start, turn_end, damage_dealt, etc.)
- `target_type`: TargetType.SELF (default)
- `stackable`: True (multiple instances can stack)
- `duration_equals_amount`: False (sync duration with amount on apply)

**Lifecycle Methods:**
- `apply(owner=None)` - Apply power to creature
- `remove()` - Remove power from creature
- `tick()` - Decrease duration, returns True if expired

**Event Hooks:**
- `on_player_turn_start(player, entities)` - Start of player turn
- `on_player_turn_end(player, entities)` - End of player turn
- `on_enemy_turn_start(enemy, player, entities)` - Start of enemy turn
- `on_enemy_turn_end(enemy, player, entities)` - End of enemy turn
- `on_card_play(card, player, entities)` - When card played
- `on_damage_dealt(damage, target, source, card) -> int` - Modify outgoing damage
- `on_damage_taken(damage, source, card, player, damage_type) -> int` - Modify incoming damage
- `on_gain_block(amount, player, source, card)` - When block gained
- `on_combat_end(owner, entities)` - Combat ends

**Implementation Methods:**
- `_apply_amount()` - Modify owner's stats when applied
- `_remove_amount()` - Reverse stat modification when removed

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Create power | Inherit from `Power` | Set `trigger_timing`, `target_type` |
| Apply effect | Override `_apply_amount()` | Modify owner stats directly |
| Remove effect | Override `_remove_amount()` | Reverse stat changes |
| Duration | Override `tick()` | Returns True when expired |
| Mod damage | Override `on_damage_dealt()`/`on_damage_taken()` | Return modified damage |

## Conventions

**Power Implementation:**
- Override `_apply_amount()` to modify stats (e.g., player.block += 5)
- Override `_remove_amount()` to reverse (e.g., player.block -= 5)
- Override `tick()` for duration logic (returns True when expired)
- Use `stackable = False` for unique powers
- Use `duration_equals_amount = True` to sync duration with amount

**Damage Modification:**
- `on_damage_dealt()`: Modify damage you deal
- `on_damage_taken()`: Modify damage you receive
- Both return modified `int` (damage value)

## Anti-Patterns

**NEVER:**
- Modify owner stats in event hooks - use `_apply_amount()`/`_remove_amount()`
- Forget to reverse changes in `_remove_amount()`
- Ignore return value in damage hooks - return the modified damage
- Set permanent duration as 0 - use `None` or large number

**ALWAYS:**
- Implement `_apply_amount()` and `_remove_amount()` for stat effects
- Return modified damage from damage hooks
- Use `Localizable` mixin for all powers
- Call `owner.remove_power(self.name)` when expired (or use `remove()`)

## Code Map

```python
class Vulnerable(Power):
    localization_prefix = "powers"
    name = "Vulnerable"
    amount = 1
    duration = 0  # Permanent
    stackable = False  # Only one instance
    
    def on_damage_taken(self, damage, source, card, player, damage_type) -> int:
        # Take 50% more damage
        return damage * 1.5
```

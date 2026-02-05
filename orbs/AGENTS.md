# ORBS MODULE

## Overview
Orb system with passive triggers and evoke effects for elemental damage and channeling.

## Structure
```
orbs/
├── base.py       # Orb base class (25 lines)
└── __init__.py   # Namespace package
```

## Core Components

### `base.py` - Orb (25 lines)
**Base Orb Class:**
- `Localizable` mixin for localization
- `localization_prefix`: "orbs"
- `passive_timing`: "turn_end" (when passive activates)
- `target_type`: TargetType.SELF (default target)

**Required Methods (raise NotImplementedError):**
- `passive()` - Passive effect (e.g., deal damage at end of turn)
- `evoke()` - Evoke orb for immediate effect

**State:**
- Orbs are channeled and stored in player state
- Passive triggers based on `passive_timing`
- Evoke can be triggered by cards

## Where to Look

| Task | Location | Notes |
|-------|-----------|--------|
| Create orb | Inherit from `Orb` | Set `passive_timing` and `target_type` |
| Passive effect | Override `passive()` | Called based on timing (e.g., turn_end) |
| Evoke effect | Override `evoke()` | Immediate one-time effect |
| Localization | Use `self.local("name")` | Key: `orbs.{ClassName}.name` |

## Conventions

**Orb Implementation:**
- Override `passive()` for recurring effects
- Override `evoke()` for immediate channel completion
- Set `passive_timing`: "turn_end", "turn_start", etc.
- Use `target_type` for AI targeting logic

**Evoke vs Passive:**
- `passive()`: Automatic effect every turn
- `evoke()`: Manual or card-triggered completion

## Anti-Patterns

**NEVER:**
- Leave `passive()` or `evoke()` unimplemented (raise NotImplementedError)
- Set wrong `target_type` - affects AI decision making
- Ignore `passive_timing` - orb won't trigger automatically

**ALWAYS:**
- Implement both `passive()` and `evoke()`
- Use `Localizable` mixin for all orbs
- Use `get_game_state()` or `get_player()` helpers

## Code Map

```python
class Plasma(Orb):
    localization_prefix = "orbs"
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY
    
    def passive(self):
        # Evoke all orbs and deal 20 damage
        for orb in get_player().orbs:
            orb.evoke()
        return [actions.DealDamage(20)]
    
    def evoke(self):
        # Evoke effect
        return [actions.DealDamage(9)]
```

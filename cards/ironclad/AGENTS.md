# IRONCLAD CARDS KNOWLEDGE BASE

## OVERVIEW
Ironclad character-specific cards (22 total) - warrior deck cards with attack, skill, and power types.

## CARD DEFINITION PATTERN

```python
@register("card")
class CardName(Card):
    card_type = CardType.ATTACK | "Skill" | "Power"
    rarity = RarityType.STARTER | COMMON | UNCOMMON | RARE
    base_cost = int               # Energy cost (0-3)
    base_damage = int             # For attacks
    base_block = int              # For defense
    base_magic = {key: value}     # Special effects
    upgrade_damage = int           # Optional overrides
    upgrade_block = int
    upgrade_cost = int
```

### Magic Effect Keys
- `"vulnerable"`: Apply debuff (duration)
- `"strength"`: Permanent Strength
- `"temp_strength"`: Lost at end of turn
- `"damage_equals_block"`: Damage equals current block
- `"upgrade_hand"`: 0=all, 1=select one

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Find all cards | `__init__.py` (grouped by rarity) |
| Add new card | New file `card_name.py`, export in `__init__.py` |
| Card base class | `cards.base.Card` |
| Rarity types | `utils.types.RarityType` |
| Registration | `@register("card")` decorator |

## CONVENTIONS

**File Naming:**
- One card per file, snake_case: `body_slam.py`
- Class name matches file: `BodySlam`

**Card Types:**
- `Attack`: Deal damage, apply debuffs
- `Skill`: Block, draw, manipulate hand
- `Power`: Ongoing effects (Strength, etc.)

**Rarity:** STARTER (deck), COMMON (rewards), UNCOMMON (mid-game), RARE (game-changers)

**Upgrade Pattern:** Increase base values (damage/block), reduce cost, or change magic behavior

## ANTI-PATTERNS

**NEVER:**
- Mix multiple cards in one file
- Add execution logic (keep data-only, logic in actions/)
- Hardcode English strings (use localization)
- Skip `__init__.py` import

**ALWAYS:**
- Import from `cards.base.Card`
- Use `@register("card")` decorator
- Keep files under 30 lines

## NOTES

Card files are data-only definitions. Logic handled by `actions/combat.py`. Magic effects map to action handlers via string keys, enabling AI modding and balance patches.

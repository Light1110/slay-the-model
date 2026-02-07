# ENEMIES SYSTEM

**Purpose:** Combat encounter definitions with stat-based enemy classes.

## STRUCTURE
```
enemies/
├── __init__.py          # Exports organized by category
├── jaw_worm.py          # Common enemy
├── cultist.py           # Common enemy
├── fungi_beast.py       # Elite enemy
├── the_guardian.py      # Boss (floor 3)
├── slime_boss.py        # Boss (floor 8)
├── the_hexaghost.py     # Final boss (floor 16)
└── louse_slaver.py      # Elite enemy
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Base enemy class | `entities/enemy.py` | HP, damage, status modifiers |
| All enemy classes | `enemies/` | Simple data containers |
| Enemy imports | `enemies/__init__.py` | Organized by Common/Elite/Boss |
| Damage calculation | `Enemy.take_damage()` | Handles weak, vulnerable, artifact |

## CONVENTIONS

### Enemy Class Definition
```python
class EnemyName(Enemy):
    """One-line docstring describing enemy type"""
    
    def __init__(self):
        super().__init__(
            name="Enemy Name",
            max_hp=XX,
            damage=YY,
            is_elite=False,  # or True
            is_boss=False    # or True
        )
```

### File Naming
- Snake case: `jaw_worm.py`, `the_guardian.py`
- Class names PascalCase matching name: `JawWorm`, `TheGuardian`
- Boss names include "The": `TheGuardian`, `TheHexaghost`

### Status Modifiers (inherited from Enemy)
- `strength`: Attack bonus
- `weak`: 25% damage reduction
- `vulnerable`: 50% extra damage taken
- `artifact`: Reduces debuff duration

## ANTI-PATTERNS

**NEVER do these:**
- Add AI behavior/patterns in enemy files (not implemented yet)
- Override `take_damage()` in individual enemies (use base class)
- Create complex `__init__()` logic beyond super().__init__()
- Add enemy-specific methods not in base Enemy class

**ALWAYS do these:**
- Import from `entities.enemy` (not `enemies.enemy`)
- Keep enemy files simple (stat containers only)
- Set `is_elite=True` OR `is_boss=True` (mutually exclusive)
- Follow file naming convention: `the_boss_name.py` for "The Boss Name"

## PATTERNS

### Enemy Stats Scaling
- **Common**: HP 40-50, damage 6-10
- **Elite**: HP 80-90, damage 15-20
- **Boss**: HP 140-250, damage 25-35

### Boss Placement
- Floor 3: The Guardian (200 HP, 25 dmg)
- Floor 8: Slime Boss (140 HP, 8 dmg)
- Floor 16: The Hexaghost (250 HP, 35 dmg)

# PROJECT KNOWLEDGE BASE - ENTITIES MODULE

**Generated:** 2026-02-05 03:05:00
**Commit:** 8593596
**Branch:** main

## OVERVIEW
Creature and entity system with base Creature class and enemy implementations.

## STRUCTURE
```
entities/
├── creature.py         # Base Creature class with HP, damage, combat stats
├── enemy.py           # Enemy subclass with modifiers (strength, weak, artifact)
├── enemies.py          # 5 concrete enemy implementations
└── __init__.py         # Module initialization
```

## WHERE TO LOOK

| Task | Location | Notes |
|-------|-----------|--------|
| Base creature | entities/creature.py:76 lines | HP, damage, max_hp, take_damage() |
| Enemy class | entities/enemy.py:76 lines | Combat modifiers, is_dead property |
| Enemy impl | entities/enemies.py:86 lines | Cultist, JawWorm, FungalBeast, Sentry, Slaver |
| Weak enemies | entities/enemies.py | weak=True reduces damage by 25% |
| Strong enemies | entities/enemies.py | strength increases damage dealt |
| Boss enemies | entities/enemies.py | artifact reduces incoming damage |

## CODE MAP

### Base Creature Class
```python
# entities/creature.py (76 lines)
class Creature(Localizable):
    def __init__(self, name: str, max_hp: int, damage: int):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.damage = damage
        # Combat modifiers (can be modified by relics/status effects)
        self.strength = 0
        self.weak = False
        self.vulnerable = False
        self.artifact = 0
        self.block = 0
        
    def take_damage(self, amount: int, source, damage_type: str = "attack") -> int:
        """Take damage with modifiers"""
        # Apply weak modifier (25% less damage)
        if self.weak:
            amount = int(amount * 0.75)
        
        # Apply artifact (reduce damage)
        if self.artifact > 0:
            amount = max(0, amount - self.artifact)
        
        actual_damage = max(1, amount)
        self.current_hp -= actual_damage
        
        # Check for death (clamp HP to 0)
        if self.current_hp <= 0:
            self.current_hp = 0
        
        return actual_damage
    
    @property
    def is_dead(self) -> bool:
        """Check if creature is dead"""
        return self.current_hp <= 0
    
    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"
```

### Enemy Class
```python
# entities/enemy.py (76 lines)
class Enemy(Creature):
    def __init__(self, name: str, max_hp: int, damage: int, 
                 is_elite: bool = False, is_boss: bool = False):
        super().__init__(name, max_hp, damage)
        self.is_elite = is_elite
        self.is_boss = is_boss
        self._is_dead = False  # Private backing for is_dead property
        
    @property
    def is_dead(self) -> bool:
        """Check if enemy is dead"""
        return self._is_dead or self.current_hp <= 0
    
    def reset_for_combat(self):
        """Reset enemy state for new combat"""
        self.current_hp = self.max_hp
        self._is_dead = False
```

### Enemy Implementations (entities/enemies.py:86 lines)

**Cultist** (lines 10-22):
- Weak enemy (weak=True)
- HP: 24
- Damage: 6
- Not elite, not boss

**JawWorm** (lines 30-40):
- Weak but fast enemy (weak=True)
- HP: 28
- Damage: 5
- Not elite, not boss

**FungalBeast** (lines 46-54):
- Medium enemy (no weak modifier)
- HP: 42
- Damage: 8
- Not elite, not boss

**Sentry** (lines 62-70):
- Elite enemy (is_elite=True)
- HP: 82
- Damage: 12
- strength: 2 (increases damage dealt)
- Not boss

**Slaver** (lines 78-86):
- Boss enemy (is_boss=True)
- HP: 250
- Damage: 18
- strength: 4 (increases damage dealt)
- artifact: 3 (reduces incoming damage)

## CONVENTIONS

**Combat Modifiers:**
- weak: Reduces damage dealt by 25% (multiply by 0.75)
- strength: Increases damage dealt by value amount
- artifact: Reduces incoming damage by value amount
- vulnerable: Increases damage taken (not used yet)

**Enemy Types:**
- Weak enemies: weak=True, lower stats
- Elite enemies: is_elite=True, higher stats, optional strength
- Boss enemies: is_boss=True, highest stats, strength + artifact

**HP Management:**
- HP is clamped to 0 when taking damage (prevents negative HP)
- reset_for_combat() restores max_hp and resets death state

**is_dead Property:**
- Read-only property checking _is_dead flag or current_hp <= 0
- Cannot be set directly (property, not attribute)

**Registration:**
- All enemies use @register("enemy") decorator
- Enemies are not directly instantiated, created via MapManager or Combat

## ANTI-PATTERNS (THIS PROJECT)
- NEVER: entities/enemy.py:60-64 - if self.current_hp <= 0: self._is_dead = True (redundant)
- NEVER: entities/enemy.py:72 - return max(1, amount) (prevents death, use max(1, amount))
- NEVER: Set is_dead in take_damage() - let property handle it
- ALWAYS: entities/enemies.py:65 - is_dead = @property, not attribute

## COMMANDS
```bash
# Run game
python __main__.py

# Run tests
pytest tests/test_enemies.py -v             # Enemy implementation tests
```

## NOTES
- Creature.take_damage() returns actual damage taken (after modifiers)
- Enemy resets maintain both HP and death state
- HP never goes negative (clamped at 0)
- Modifiers are instance variables that can be modified by relics/status effects

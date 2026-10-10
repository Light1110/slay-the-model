"""
Damage modification phase enumeration.

Defines the order in which damage modifiers are applied:
1. ADDITIVE: Addition/subtraction modifiers (e.g., Strength +3)
2. MULTIPLICATIVE: Multiplication/division modifiers (e.g., Weak 0.75x, Pen Nib)
3. FINAL: After incoming multipliers (e.g., Flying)
4. CAPPING: Limit/cap modifiers (e.g., Intangible caps at 1)

Within each phase, powers are applied before relics.
"""

from enum import Enum, auto


class DamagePhase(Enum):
    """Defines when a damage modifier is applied in the calculation pipeline."""
    
    ADDITIVE = auto()        # Addition/subtraction (Strength, Dexterity)
    MULTIPLICATIVE = auto()  # Multiplication/division (Weak, Pen Nib)
    FINAL = auto()           # After incoming multipliers (Flying)
    CAPPING = auto()         # Limit/cap damage (Intangible)
"""
Back Attack power for Act 4 elite fight.
Deals 50% more damage when attacking from behind.
"""
from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register


@register("power")
class BackAttackPower(Power):
    """50% extra damage from behind (Spire Shield/Spear elite fight)."""
    
    name = "Back Attack"
    description = "从背后攻击时，造成50%额外伤害"
    stack_type = StackType.PRESENCE
    is_buff = True
    is_back_attack = True
    modify_phase = DamagePhase.FINAL
    
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Multiplier tier (not used, always 1.5x)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def modify_damage_dealt(self, base_damage: int) -> float:
        """50% more damage from behind. The pipeline rounds this after incoming multipliers."""
        return base_damage * 1.5

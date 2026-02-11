"""
Thorns power for combat effects.
Deal damage back when attacked.
"""
from typing import Any, List
from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power
from utils.registry import register

@register("power")
class ThornsPower(Power):
    """Deal damage back when attacked."""
    
    name = "Thorns"
    description = "When attacked, deal damage back."
    stackable = True
    amount_equals_duration = False
    is_buff = True  # Beneficial effect - reflects damage
    
    def __init__(self, amount: int = 3, duration: int = 0, owner=None):
        """
        Args:
            amount: Thorns damage to deal (default 3)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None, player: Any = None, damage_type: str = "direct") -> List[Action]:
        if damage_type == "attack" and source is not None:
            return [DealDamageAction(damage=self.amount, target=source, damage_type="direct")]

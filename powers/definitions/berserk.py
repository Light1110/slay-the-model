"""
Berserk power - At the start of your turn, gain 1 Energy and apply 1 Vulnerable.
"""
from typing import Any, List
from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class BerserkPower(Power):
    """At the start of your turn, gain 1 Energy and apply 1 Vulnerable."""
    
    name = "Berserk"
    description = "At the start of your turn, gain 1 Energy and apply 1 Vulnerable."
    stackable = False
    is_buff = False
    
    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_turn_start(self) -> List[Action]:
        """Gain 1 Energy and apply Vulnerable at start of turn."""
        from powers.definitions.vulnerable import VulnerablePower
        
        # Gain 1 Energy directly
        if self.owner and hasattr(self.owner, 'gain_energy'):
            self.owner.gain_energy(1)
        
        # Apply 1 Vulnerable to self directly
        if self.owner:
            self.owner.add_power(VulnerablePower(amount=1, owner=self.owner))
        
        return []
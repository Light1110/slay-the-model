"""Focus Power - Increases orb effectiveness for Defect."""
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class FocusPower(Power):
    """Focus increases the effectiveness of Orbs.
    
    Each point of Focus adds to the passive/active effects of orbs.
    This is a Defect-specific power.
    """
    
    def __init__(self, amount: int = 0, owner=None):
        super().__init__(amount=amount, owner=owner)
        self.name = "Focus"
        self.is_buff = amount >= 0
        self.is_debuff = amount < 0
        self.stack_type = StackType.INTENSITY
    
    def get_description(self) -> str:
        if self.amount >= 0:
            return f"Orbs deal {self.amount} additional damage/effect."
        return f"Orbs deal {abs(self.amount)} less damage/effect."
    
    def at_end_of_turn(self, owner, enemies=None) -> None:
        """Focus doesn't have end of turn effects."""

"""
Rupture power for Ironclad.
Whenever you lose HP from a card, gain Strength.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import ApplyPowerAction
from utils.registry import register


@register("power")
class RupturePower(Power):
    """Whenever you lose HP from a card, gain 1/2 Strength."""

    name = "Rupture"
    description = "Whenever you lose HP from a card, gain Strength."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Strength to gain when HP is lost (default 1)
            duration: -1 for permanent
        """
        super().__init__(amount=amount, duration=-1, owner=owner)

    def on_lose_hp(self, amount: int, source: Any = None, card: Any = None) -> List[Action]:
        """Gain Strength when HP is lost from a card.
        
        Rupture triggers on any HP loss (not damage), such as from
        self-damage cards like Bloodletting or Burning Blood.
        
        Args:
            amount: Amount of HP lost
            source: Source of the HP loss
            card: Card that caused HP loss (if applicable)
            
        Returns:
            List of actions to gain Strength
        """
        from engine.game_state import game_state

        actions = []

        # Only trigger if HP loss is from a card
        if card is not None:
            actions.append(ApplyPowerAction(
                power="Strength",
                target=game_state.player,
                amount=self.amount
            ))

        return actions

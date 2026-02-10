"""
Confused power for SneckoEye relic.
Randomizes card costs whenever a card is drawn.
"""
from typing import List, Optional
from powers.base import Power
from actions.base import Action, LambdaAction
from utils.registry import register

@register("power")
class ConfusedPower(Power):
    """Randomize card costs whenever a card is drawn."""

    name = "Confused"
    description = "Randomize the cost of cards whenever they are drawn."
    stackable = False  # Only one instance needed
    is_buff = False  # Technically not a buff (unpredictable costs)

    def __init__(self, amount: int = 0, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used for confused (effect is independent of amount)
            duration: 0 for permanent (lasts entire combat)
            owner: The creature that has this power
        """
        super().__init__(amount=0, duration=duration, owner=owner)

    def on_card_draw(self, card) -> List[Action]:
        """Randomize cost of a card when it is drawn.
        
        Args:
            card: The card that was just drawn
            
        Returns:
            List of actions to execute (empty list, effect is immediate)
        """
        import random as rd
        # Randomize between 0 and 3 (like original Slay the Spire)
        # Use LambdaAction to modify card cost via action pattern
        return [LambdaAction(func=lambda: setattr(card, 'cost', rd.randint(0, 3)))]

"""
Confused power for SneckoEye relic.
Randomizes card costs each turn.
"""
from typing import List
from powers.base import Power
from actions.base import LambdaAction
from utils.registry import register

@register("power")
class ConfusedPower(Power):
    """Randomize card costs each turn."""

    name = "Confused"
    description = "Randomize card costs at start of turn."
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

    def on_turn_start(self) -> List:
        """Randomize costs of all cards in hand at start of turn."""
        from engine.game_state import game_state
        import random as rd

        def randomize_costs():
            hand = game_state.player.card_manager.get_pile("hand")
            for card in hand:
                # Randomize between 0 and 3 (like original Slay the Spire)
                card._cost = rd.randint(0, 3)

        return [LambdaAction(randomize_costs)]

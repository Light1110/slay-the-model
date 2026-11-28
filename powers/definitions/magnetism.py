"""
Magnetism power for combat effects.
Add random colorless card to hand at start of turn.
"""
from engine.runtime_api import add_actions
from actions.card import AddCardAction
from powers.base import Power, StackType
from utils.random import get_random_card
from utils.registry import register


@register("power")
class MagnetismPower(Power):
    """Add random colorless card to hand at start of turn."""

    name = "Magnetism"
    description = "At the start of your turn, add {amount} random Colorless card(s) to your hand."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_start(self):
        """Add random colorless card to hand at start of turn."""
        from engine.game_state import game_state

        combat = game_state.current_combat
        if combat is None or combat.combat_ended or not any(
            not enemy.is_dead() and not getattr(enemy, "is_dying", False)
            and not getattr(enemy, "is_escaping", False)
            for enemy in combat.enemies
        ):
            return

        actions = []
        for _ in range(self.amount):
            card = get_random_card(namespaces=["colorless"], pool_kind="combat")
            if card is not None:
                actions.append(AddCardAction(card=card, dest_pile="hand"))
        add_actions(actions)

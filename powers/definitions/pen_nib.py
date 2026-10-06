"""
PenNib power for double damage on every 10th attack.
"""
from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import CardType


@register("power")
class PenNibPower(Power):
    """Next attack deals double damage."""

    name = "PenNib"
    description = "Next attack deals double damage."
    stack_type = StackType.DURATION
    is_buff = True
    modify_phase = DamagePhase.MULTIPLICATIVE
    damage_priority = 6

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> float:
        """Double the next attack. Removal happens after the card's damage resolves."""
        if getattr(card, "card_type", None) == CardType.ATTACK:
            return base_damage * 2
        return base_damage

    def on_card_play(self, card, targets):
        if getattr(card, "card_type", None) != CardType.ATTACK or self.owner is None:
            return
        from actions.combat_status import RemovePowerAction
        from engine.runtime_api import add_actions

        add_actions([RemovePowerAction(self.name, self.owner)])

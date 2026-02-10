"""
Ironclad Rare Power card - Berserk
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction, LoseHPAction, GainEnergyAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Berserk(Card):
    """Gain 2 (1) Vulnerable. At the start of your turn, gain 1 Energy."""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 0

    # todo: ApplyPowerAction (VulnerablePower + BerserkPower)

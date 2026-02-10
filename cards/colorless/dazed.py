from typing import Optional
from actions.base import Action
from cards.base import COST_UNPLAYABLE, Card
from actions.card import DrawCardsAction
from utils.result_types import List
from utils.types import CardType


class Dazed(Card):
    """Dazed card - unplayable, draws replacement"""
    base_cost = COST_UNPLAYABLE
    card_type = CardType.STATUS
    upgradeable = False
    base_ethereal = True
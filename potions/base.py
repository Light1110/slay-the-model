import random
from typing import List
from actions.base import Action
from engine.game_state import game_state
from entities.creature import Creature

class Potion:
    rarity = "Common"
    category = "Global"
    amount = None
    # todo: localized display_name and description

    def __init__(self):
        pass

    def on_use(self, target: Creature) -> List[Action]:
        """Base use method to be overridden by specific potions"""
        return []
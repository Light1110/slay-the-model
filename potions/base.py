import random
from typing import List
from actions.base import Action
from engine.game_state import game_state
from entities.creature import Creature
from localization import Localizable
from utils.types import RarityType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"
    amount = None

    def __init__(self):
        pass

    def on_use(self, target: Creature) -> List[Action]:
        """Base use method to be overridden by specific potions"""
        return []
from engine.game_state import game_state
from player.player import Player
from utils.types import TargetType


class Orb:
    passive_timing = "turn_end"
    target_type = TargetType.SELF
    
    # todo: localized display_name and description
    
    def __init__(self):
        pass

    def passive(self):
        raise NotImplementedError

    def evoke(self):
        raise NotImplementedError
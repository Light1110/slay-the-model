from enum import Enum


class TargetType(str, Enum):
    SELF = "self"
    ENEMY_SELECT = "enemy_select"
    ENEMY_RANDOM = "enemy_random"
    ENEMY_LOWEST_HP = "enemy_lowest_hp"
    ENEMY_ALL = "enemy_all"


target_type = TargetType

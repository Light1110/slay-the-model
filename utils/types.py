from enum import Enum


class TargetType(str, Enum):
    SELF = "self"
    ENEMY_SELECT = "enemy_select"
    ENEMY_RANDOM = "enemy_random"
    ENEMY_LOWEST_HP = "enemy_lowest_hp"
    ENEMY_ALL = "enemy_all"

class PilePosType(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    RANDOM = "random"

class StatusType(str, Enum):
    NEUTRAL = "Neutral"
    CALM = "Calm"
    WRATH = "Wrath"
    DIVINITY = "Divinity"
    
"""Enemy intention system - defines what an enemy plans to do."""

from typing import List, TYPE_CHECKING, Optional
from abc import ABC, abstractmethod
from localization import Localizable, BaseLocalStr

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class Intention(ABC, Localizable):
    """Base class for enemy intentions.
    
    Each intention defines what an enemy plans to do and returns a list of Actions
    to execute when triggered.
    """
    
    # 本地化
    localization_prefix = "enemies.intentions"
    localizable_fields = ("name", "description")
    
    def __init__(self, name: str, enemy: 'Enemy'):
        self.name = name
        self.enemy = enemy
        
        # 基础数值（子类在__init__中设置）
        self.base_damage = 0
        self.base_block = 0
        self.base_strength_gain = 0
        self.base_heal = 0
    
    @abstractmethod
    def execute(self) -> List['Action']:
        """Execute this intention and return list of actions to perform.

        Returns:
            List of Action objects to queue for execution
        """
        pass
    
    @property
    def description(self) -> 'BaseLocalStr':
        """获取意图描述（动态替换{damage}等变量）"""    
        # 动态替换变量
        variables = {}
        
        # 伤害值
        if self.base_damage > 0:
            from utils.dynamic_values import resolve_potential_damage
            from engine.game_state import game_state
            player = game_state.player
            variables['damage'] = resolve_potential_damage(self.base_damage, self.enemy, player, None)
        
        # 其他数值
        if self.base_block > 0:
            variables['block'] = self.base_block
        if self.base_strength_gain > 0:
            variables['strength_gain'] = self.base_strength_gain
        if self.base_heal > 0:
            variables['heal'] = self.base_heal
        
        # 返回带变量的LocalStr对象
        return self.local("description", **variables)

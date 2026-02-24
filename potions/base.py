import random
from typing import List, Optional
from actions.base import Action
from entities.creature import Creature
from localization import Localizable, t
from utils.types import RarityType, TargetType

class Potion(Localizable):
    localization_prefix = "potions"
    rarity = RarityType.COMMON
    category = "Global"
    can_be_used_actively = True  # Default: can be used actively, override if passive only
    target_type = TargetType.SELF  # Default: targets the player

    def __init__(self):
        self._amount= 0
    
    @property
    def amount(self) -> int:
        """If player has relic: Sacred Bark, potion effects are doubled"""
        from engine.game_state import game_state
        if game_state.player and any(relic.idstr == "SacredBark" for relic in game_state.player.relics):
            return self._amount * 2
        return self._amount

    def on_use(self, targets: List[Creature]) -> List[Action]:
        """Base use method to be overridden by specific potions.
        
        Args:
            targets: List of resolved targets (single or multiple based on target_type)
        
        Returns:
            List of actions to execute
        """
        return []
    
    def info(self):
        """
        获取药水的完整信息显示
        
        返回格式：
        PotionName
        Description text
        """
        result = self.local("name") + f"\n{t('ui.rarity_label', 'Rarity: {rarity}', rarity=self.rarity.name.title())}"
        if hasattr(self, 'category') and self.category:
            result += f"\n{t('ui.category_label', 'Category: {category}', category=self.category)}"
        result += "\n" + self.local("description")
        return result

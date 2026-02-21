# -*- coding: utf-8 -*-
"""
SlowPower - Giant Head enemy ability
Makes card costs increase as player plays more cards.
"""
from powers.base import Power
from localization import LocalStr
from utils.registry import register


@register("power")
class SlowPower(Power):
    """
    Slow power for Giant Head elite enemy.
    
    Each time the player plays a card, all cards in hand cost 1 more for 
    the rest of the combat (cumulative). This is a permanent debuff that
    stacks infinitely.
    
    In the original game, this makes the combat progressively harder as
    the player must balance dealing damage vs. the increasing cost of cards.
    """
    
    def __init__(self, amount: int = 0, owner=None):
        super().__init__()
        self.amount = amount  # Tracks how many cards have been played
        self.owner = owner
        self.name = "Slow"
        self.power_type = "ability"
        self.localization_key = "powers.slow"
        self.is_buff = False  # This is a debuff from player's perspective
        
    def on_card_play(self, card, player, entities) -> list:
        """
        Called when player plays a card.
        Increases the cost accumulator.
        
        Args:
            card: The card being played
            player: The player
            entities: Combat entities
            
        Returns:
            Empty list (no actions needed)
        """
        # Increment the slow counter each time a card is played
        self.amount += 1
        return []
    
    def get_cost_increase(self) -> int:
        """Get the current cost increase for cards.
        
        Returns:
            Amount to add to card costs
        """
        return self.amount
        
    def local(self, field: str, **kwargs) -> LocalStr:
        """Get localized string for this power.
        
        Args:
            field: The localization field ('name' or 'description')
            **kwargs: Optional arguments
        """
        if field == "name":
            return LocalStr(f"{self.localization_key}.name", default=self.name)
        elif field == "description":
            amount = kwargs.get('amount', self.amount)
            return LocalStr(
                f"{self.localization_key}.description", 
                default=f"Player's cards cost +{amount} this combat (stacks with each card played).",
                amount=amount
            )
        return super().local(field)
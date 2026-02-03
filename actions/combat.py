from actions.base import Action
from localization import t
from utils.registry import register

@register("action")
class ModifyMaxHpAction(Action):
    """Modify player's max HP
    
    Required:
        amount (int): HP change amount
        
    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount
    
    def execute(self):
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.max_hp += self.amount
            print(t("ui.max_hp_changed", default=f"Max HP changed by {self.amount}!", amount=self.amount))
            
@register("action")
class LoseHpAction(Action):
    """Modify player's HP
    
    Required:
        amount (int): HP change amount
        
    Optional:
        None
    """
    def __init__(self, amount: int):
        self.amount = amount
    
    def execute(self):
        from engine.game_state import game_state
        if game_state.player:
            game_state.player.hp -= self.amount
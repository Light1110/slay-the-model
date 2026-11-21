"""
Fungi Beast - Common enemy
Gains strength over time. Applies Vulnerable on death.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.fungi_beast_intentions import BiteIntention, GrowIntention

if TYPE_CHECKING:
    from actions.base import Action


class FungiBeast(Enemy):
    """Fungi Beast - Gains strength and applies Vulnerable on death."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(22, 28) # todo: 24-28 a7
        )
        
        # Register intentions
        self.add_intention(BiteIntention(self))
        self.add_intention(GrowIntention(self))
        
        # Spore Cloud: On death, applies 2 Vulnerable
        self._spore_cloud_stacks = 2
    
    def determine_next_intention(self, floor: int = 1):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if roll < 60:
            move = "grow" if history[-2:] == ["bite", "bite"] else "bite"
        else:
            move = "bite" if history[-1:] == ["grow"] else "grow"
        return self.intentions[move]

    def on_death(self) -> None:
        """Apply Spore Cloud on death: applies 2 Vulnerable to player."""
        from actions.combat import ApplyPowerAction
        from powers.definitions.vulnerable import VulnerablePower
        from engine.game_state import game_state
        
        super().on_death()
        
        actions = []
        if game_state and game_state.player:
            actions.append(
                ApplyPowerAction(
                    VulnerablePower(amount=self._spore_cloud_stacks, duration=self._spore_cloud_stacks, owner=game_state.player),
                    game_state.player,
                    source=self,
                )
            )
        
        from engine.game_state import game_state
        
        add_actions(actions)
        

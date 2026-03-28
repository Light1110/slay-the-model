"""Book of Stabbing intentions - Act 2 Elite enemy."""
from engine.runtime_api import add_action, add_actions

import random
from typing import TYPE_CHECKING, List

from actions.combat import AttackAction
from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.act2.book_of_stabbing import BookOfStabbing


class MultiStab(Intention):
    """Deals 6×N damage where N increases each use."""
    
    def __init__(self, enemy: "BookOfStabbing"):
        super().__init__("Multi Stab", enemy)
        self.base_damage = 6  # Per hit
        self._hits_base = 2  # Base number of hits
    
    def execute(self) -> None:
        """Execute multi-stab attack."""
        from engine.game_state import game_state
        
        actions = []
        # Number of hits = times used + 2
        num_hits = self.enemy.multi_stab_count + self._hits_base
        
        for _ in range(num_hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
class BigStab(Intention):
    """Deals 21 damage."""
    
    def __init__(self, enemy: "BookOfStabbing"):
        super().__init__("Big Stab", enemy)
        self.base_damage = 21
    
    def execute(self) -> None:
        """Execute big stab attack."""
        from engine.game_state import game_state
        
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            damage=self.base_damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]
        )

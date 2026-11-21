"""Spike Slime specific intentions."""
from engine.runtime_api import add_action, add_actions

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class LickIntention(Intention):
    """Lick - Applies the configured amount of Frail.
    
    According to doc, Spike Slime (S) applies Frail.
    """
    
    def __init__(self, enemy: 'Enemy', frail_amount: int = 2):
        super().__init__("lick", enemy)
        self._frail_amount = frail_amount
        self.base_amount = frail_amount  # For description variable {amount}
    
    def execute(self) -> None:
        """Execute Lick with matching displayed and applied duration."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        add_actions(
        [
            ApplyPowerAction(
                power="Frail",
                target=game_state.player,
                amount=self._frail_amount,
                duration=self._frail_amount
            )
        ]
        )


class TackleIntention(Intention):
    """Deal damage and add the configured number of Slimed cards."""

    def __init__(self, enemy: 'Enemy', damage: int, slimed_count: int = 0):
        super().__init__("tackle", enemy)
        self.slimed_count = slimed_count
        self.base_damage = damage

    def execute(self) -> None:
        """Execute Tackle: deals damage to player."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from cards.colorless.slimed import Slimed
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            ),
        ]
        actions.extend(
            AddCardAction(Slimed(), dest_pile="discard_pile", source="enemy")
            for _ in range(self.slimed_count)
        )
        add_actions(actions)


class SplitIntention(Intention):
    """Split - Disappears and spawns 2 Spike Slimes (M) with current HP.
    
    Only used by Spike Slime (L).
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)
    
    def execute(self) -> None:
        from actions.combat import AddEnemyAction, RemoveEnemyAction, RollEnemyIntentionAction
        from enemies.act1.spike_slime import SpikeSlimeM

        current_hp = self.enemy.hp
        add_actions([
            RemoveEnemyAction(enemy=self.enemy),
            AddEnemyAction(enemy=SpikeSlimeM(max_hp=current_hp)),
            AddEnemyAction(enemy=SpikeSlimeM(max_hp=current_hp)),
            RollEnemyIntentionAction(self.enemy),
        ])

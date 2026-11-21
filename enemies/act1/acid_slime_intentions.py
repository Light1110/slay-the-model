"""Acid Slime specific intentions."""
from engine.runtime_api import add_action, add_actions

from typing import List, TYPE_CHECKING
import random

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class CorrosiveSpitIntention(Intention):
    """Corrosive Spit - Deals damage and adds Slimed cards to discard pile.
    
    Acid Slime (L): 11 damage, 2 Slimed cards (12 damage on A7+)
    Acid Slime (M): 7 damage, 1 Slimed card (8 damage on A3+)
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("corrosive_spit", enemy)
        # Determine damage based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self.base_damage = 11
                self._slimed_count = 2
            elif enemy_class == 'AcidSlimeM':
                self.base_damage = 7
                self._slimed_count = 1
            else:
                self.base_damage = 7
                self._slimed_count = 1
        else:
            self.base_damage = 7
            self._slimed_count = 1
        self.base_cards = self._slimed_count  # For description variable {cards}
    
    def execute(self) -> None:
        """Execute Corrosive Spit: deals damage and adds Slimed cards."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from engine.game_state import game_state
        from utils.registry import get_registered
        
        if not game_state or not game_state.player:
            return
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
        
        # Add Slimed cards to discard pile
        try:
            SlimedCard = get_registered("card", "Slimed")
            if SlimedCard:
                for _ in range(self._slimed_count):
                    actions.append(AddCardAction(
                        card=SlimedCard(), 
                        dest_pile="discard_pile", 
                        source="enemy"
                    ))
        except Exception:
            pass
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
class LickIntention(Intention):
    """Lick - Applies Weak to player.
    
    Acid Slime (L): 2 Weak
    Acid Slime (M): 1 Weak
    Acid Slime (S): 1 Weak
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("lick", enemy)
        # Determine Weak amount based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self.weak_stacks = 2
            else:
                self.weak_stacks = 1
        else:
            self.weak_stacks = 1
    
    def execute(self) -> None:
        """Execute Lick: applies Weak to player."""
        from actions.combat import ApplyPowerAction
        from powers.definitions.weak import WeakPower
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        add_actions(
        [
            ApplyPowerAction(
                WeakPower(amount=self.weak_stacks, duration=2, owner=game_state.player),
                game_state.player,
                source=self.enemy,
            )
        ]
        )


class TackleIntention(Intention):
    """Tackle - Deals damage to player.
    
    Acid Slime (L): 16 damage (18 on A3+)
    Acid Slime (M): 10 damage (12 on A3+)
    Acid Slime (S): 3 damage (4 on A3+)
    """
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("tackle", enemy)
        # Determine damage based on enemy type
        if hasattr(enemy, '__class__'):
            enemy_class = enemy.__class__.__name__
            if enemy_class == 'AcidSlimeL':
                self.base_damage = 16
            elif enemy_class == 'AcidSlimeM':
                self.base_damage = 10
            else:  # AcidSlimeS
                self.base_damage = 3
        else:
            self.base_damage = 10
    
    def execute(self) -> None:
        """Execute Tackle: deals damage to player."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return
        from engine.game_state import game_state
        add_actions(
        [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
        )


class SplitIntention(Intention):
    """Replace the large slime with two medium acid slimes at its current HP."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("split", enemy)

    def execute(self) -> None:
        from actions.combat import AddEnemyAction, RemoveEnemyAction
        from enemies.act1.acid_slime import AcidSlimeM

        current_hp = self.enemy.hp
        add_actions([
            RemoveEnemyAction(enemy=self.enemy),
            AddEnemyAction(enemy=AcidSlimeM(max_hp=current_hp)),
            AddEnemyAction(enemy=AcidSlimeM(max_hp=current_hp)),
        ])

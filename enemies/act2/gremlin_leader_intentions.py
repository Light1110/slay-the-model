"""Gremlin Leader intentions - Act 2 Elite enemy."""
from engine.runtime_api import add_action, add_actions

from typing import TYPE_CHECKING, List

from actions.combat import AttackAction, GainBlockAction, ApplyPowerAction
from enemies.intention import Intention
from powers.definitions.strength import StrengthPower

if TYPE_CHECKING:
    from enemies.act2.gremlin_leader import GremlinLeader

GREMLIN_POSITIONS = (-366, -170, -532)


class Encourage(Intention):
    """All enemies gain 3 Strength. Other enemies gain 6 Block."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Encourage", enemy)
        self.base_strength_gain = 3
        self.base_block = 6
    
    def execute(self) -> None:
        """Execute encourage - buff all allies."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )
        
        actions = []
        
        # Apply strength to all enemies (including self)
        for enemy in enemies:
            if enemy.is_alive:
                actions.append(ApplyPowerAction(StrengthPower(amount=self.base_strength_gain, owner=enemy), enemy))


                
                # Give block to OTHER enemies (not self)
                if enemy != self.enemy:
                    actions.append(GainBlockAction(
                        block=self.base_block,
                        target=enemy
                    ))
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
class Stab(Intention):
    """Deals 6×3 damage."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Stab", enemy)
        self.base_damage = 6
        self._hits = 3
    
    def execute(self) -> None:
        """Execute stab attack."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self._hits):
            actions.append(AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack"
            ))
        
        from engine.game_state import game_state
        
        add_actions(actions)
        
class Rally(Intention):
    """Summon 2 random Gremlins."""
    
    def __init__(self, enemy: "GremlinLeader"):
        super().__init__("Rally!", enemy)
    
    def execute(self) -> None:
        from actions.combat import AddEnemyAction
        from enemies.act1.gremlin import create_leader_minion
        from engine.game_state import game_state

        combat = game_state.current_combat
        if combat is None:
            return
        positions = combat.open_formation_positions(GREMLIN_POSITIONS)[:2]
        add_actions([
            AddEnemyAction(create_leader_minion("ai"), position=position)
            for position in positions
        ])

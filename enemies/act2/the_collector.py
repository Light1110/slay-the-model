"""The Collector - Act 2 Elite enemy."""
from engine.random_streams import get_rng

from enemies.act2.the_collector_intentions import Buff, Fireball, MegaDebuff, Spawn
from enemies.base import Enemy
from utils.types import EnemyType


class TorchHead(Enemy):
    """Minion spawned by The Collector.
    
    Simple enemy that only uses Tackle.
    This is a summoned minion and should not trigger on_fatal effects.
    """
    
    enemy_type = EnemyType.NORMAL
    roll_fixed_opening_intention = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        super().__init__(
            hp_range=(40, 45) if ascension >= 7 else (38, 40),
            is_minion=True,
        )
        
        # Register intentions
        from enemies.act2.the_collector_intentions import Tackle
        self.add_intention(Tackle(self))
    
    def determine_next_intention(self, floor: int) -> None:
        """Torch Head only has one attack."""
        self.current_intention = self.intentions["Tackle"]


class TheCollector(Enemy):
    """Boss enemy found in Act 2.
    
    Summons Torch Head minions and buffs them.
    Always starts with Spawn.
    Always uses Mega Debuff on turn 4.
    Cannot use Buff twice in a row.
    Cannot use Fireball 3 times in a row.
    """
    
    enemy_type = EnemyType.BOSS
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        hp = 300 if ascension >= 9 else 282
        super().__init__(hp_range=(hp, hp))
        
        # Register intentions
        self.add_intention(Spawn(self))
        self.add_intention(Fireball(self))
        self.add_intention(Buff(self))
        self.add_intention(MegaDebuff(self))
    
    def _count_torch_heads(self) -> int:
        """Count alive Torch Heads in battle."""
        from engine.game_state import game_state
        enemies = (
            game_state.current_combat.enemies
            if game_state.current_combat is not None
            else []
        )

        count = 0
        for enemy in enemies:
            if enemy.is_alive and isinstance(enemy, TorchHead):
                count += 1
        return count
    
    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if not history:
            move = "Spawn"
        elif len(history) >= 3 and "Mega Debuff" not in history:
            move = "Mega Debuff"
        elif roll <= 25 and self._count_torch_heads() < 2 and history[-1] != "Spawn":
            move = "Spawn"
        elif roll <= 70 and history[-2:] != ["Fireball", "Fireball"]:
            move = "Fireball"
        else:
            move = "Fireball" if history[-1] == "Buff" else "Buff"
        return self.intentions[move]

    def on_death(self) -> None:
        from actions.combat import RemoveEnemyAction
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        super().on_death()
        combat = game_state.current_combat
        if combat is not None:
            add_actions([
                RemoveEnemyAction(enemy) for enemy in combat.enemies
                if isinstance(enemy, TorchHead) and enemy.is_alive
            ])

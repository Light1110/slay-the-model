from actions.combat import AddEnemyAction
from engine.runtime_api import add_action
from enemies.act2.the_collector import TheCollector, TorchHead
from enemies.base import Enemy
from enemies.intention import Intention
from engine.combat import Combat
from engine.game_state import game_state
from player.player_factory import create_player


class RecordedIntention(Intention):
    def execute(self):
        pass


class ProbeEnemy(Enemy):
    def __init__(self):
        super().__init__(hp_range=(10, 10))
        self.add_intention(RecordedIntention("wait", self))
        self.selections = 0

    def determine_next_intention(self, floor=1):
        self.selections += 1
        return self.intentions["wait"]


class SummonIntention(Intention):
    def __init__(self, owner, summon):
        super().__init__("summon", owner)
        self.summon = summon

    def execute(self):
        add_action(AddEnemyAction(self.summon))


def test_add_enemy_action_accepts_enemy_class_and_spawns_instance():
    combat = Combat(enemies=[TheCollector()])
    game_state.current_combat = combat

    action = AddEnemyAction(TorchHead)
    result = action.execute()

    assert result is None
    assert any(isinstance(enemy, TorchHead) for enemy in combat.enemies)


def test_spawned_intention_is_only_selected_once_before_first_action():
    game_state.current_combat = Combat(enemies=[])
    enemy = ProbeEnemy()
    action = AddEnemyAction(enemy)
    action.execute()
    action.execute()
    enemy.on_player_turn_start()

    assert game_state.current_combat.enemies == [enemy]
    assert enemy.current_intention is enemy.intentions["wait"]
    assert enemy.selections == 1

    enemy.execute_intention()
    enemy.on_player_turn_start()
    assert enemy.history_intentions == ["wait"]
    assert enemy.selections == 2


def test_enemy_spawned_during_enemy_phase_acts_in_next_phase():
    game_state.player = create_player("ironclad")
    owner, spawned = ProbeEnemy(), ProbeEnemy()
    owner.current_intention = SummonIntention(owner, spawned)
    combat = Combat(enemies=[owner])
    game_state.current_combat = combat

    assert combat.execute_enemy_phase() is None
    assert spawned in combat.enemies
    assert spawned.selections == 1
    assert spawned.history_intentions == []

    assert combat.execute_enemy_phase() is None
    assert spawned.history_intentions == ["wait"]

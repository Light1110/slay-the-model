"""Act healing must occur after rewards and only when another act is entered."""
import pytest

from actions.combat import HealAction
from actions.base import LambdaAction
from engine.combat import Combat
from engine.game_flow import GameFlow
from engine.game_state import game_state
from relics.character.ironclad import MagicFlower
from relics.base import Relic
from powers.base import Power
from relics.global_relics.event import MarkOfBloom
from relics.global_relics.special import RedKey, BlueKey, GreenKey
from utils.result_types import GameTerminalState


@pytest.mark.parametrize(('ascension', 'missing', 'healed'), [
    (0, 30, 30), (4, 30, 30), (5, 30, 23), (20, 30, 23),
    (5, 1, 1), (5, 2, 2), (5, 3, 2), (5, 6, 5), (5, 0, 0),
])
def test_transition_healing_rounding(ascension: int, missing: int, healed: int):
    game_state.current_act = 2
    game_state.ascension = ascension
    player = game_state.player
    player.hp = player.max_hp - missing
    before = player.hp
    assert game_state.advance_act() is False
    assert player.hp == before + healed
    assert game_state.action_queue.is_empty()


@pytest.mark.parametrize(('next_act', 'keys', 'continues'), [
    (2, False, True), (3, False, True), (4, True, True),
    (4, False, False), (5, True, False),
])
def test_flow_heals_only_on_actual_transition(next_act: int, keys: bool, continues: bool):
    game_state.current_act = next_act
    player = game_state.player
    player.hp = 10
    if keys:
        player.relics.extend([RedKey(), BlueKey(), GreenKey()])
    flow = GameFlow()
    flow._execute_complete_act_phase(game_state)
    assert player.hp == (player.max_hp if continues else 10)
    assert flow.flow_phase == ('init_act' if continues else 'finished')


def test_transition_uses_final_reward_health_and_bloom():
    game_state.current_act = 2
    game_state.ascension = 5
    player = game_state.player
    # Model a boss reward that has already increased max HP.
    player.max_hp = 120
    player.hp = 40
    assert not game_state.advance_act()
    assert player.hp == 100
    player.relics.append(MarkOfBloom())
    game_state.current_act = 3
    assert not game_state.advance_act()
    assert player.hp == 100


def test_map_initialization_does_not_heal():
    game_state.current_act = 2
    game_state.player.hp = 10
    game_state.initialize_map()
    game_state.initialize_map()
    assert game_state.player.hp == 10


def test_transition_applies_power_hooks_and_drains_healing_reactions():
    reactions: list[int] = []

    class HealingPower(Power):
        def modify_heal(self, amount: int) -> int:
            return amount // 2

    class HealingObserver(Relic):
        def on_heal(self, amount, source=None):
            return [LambdaAction(reactions.append, args=[amount])]

    game_state.current_act = 2
    game_state.ascension = 5
    player = game_state.player
    player.relics = [HealingObserver()]
    player.powers = [HealingPower(owner=player)]
    player.hp = player.max_hp - 20
    assert not game_state.advance_act()
    assert player.hp == player.max_hp - 13
    assert reactions == [7]
    assert game_state.action_queue.is_empty()


def test_magic_flower_only_applies_during_combat(monkeypatch):
    player = game_state.player
    player.relics = [MagicFlower()]
    player.hp = 10
    HealAction(amount=10).execute()
    assert player.hp == 20
    combat = Combat([])
    game_state.current_combat = combat
    HealAction(amount=10).execute()
    assert player.hp == 35

    # Victory hooks still run with combat healing; later rewards do not.
    monkeypatch.setattr(combat, '_init_combat', lambda: None)
    def finish():
        HealAction(amount=10).execute()
        return GameTerminalState.COMBAT_WIN
    monkeypatch.setattr(combat, '_execute_next_phase', finish)
    assert combat.start() == GameTerminalState.COMBAT_WIN
    assert player.hp == 50
    assert combat.combat_ended
    HealAction(amount=10).execute()
    assert player.hp == 60
    game_state.current_act = 2
    game_state.ascension = 5
    player.hp = player.max_hp - 20
    assert not game_state.advance_act()
    assert player.hp == player.max_hp - 5


def test_combat_exception_closes_healing_window(monkeypatch):
    combat = Combat([])
    monkeypatch.setattr(combat, '_init_combat', lambda: None)
    def fail():
        raise RuntimeError('test interruption')
    monkeypatch.setattr(combat, '_execute_next_phase', fail)
    with pytest.raises(RuntimeError, match='test interruption'):
        combat.start()
    assert combat.combat_ended

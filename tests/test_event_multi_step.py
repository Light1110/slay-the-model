"""Multi-step flow for the colosseum, dead adventurer, and scrap ooze."""
from engine.random_streams import get_rng, StreamRandom

from typing import cast

from actions.base import LambdaAction
from actions.card import AddRandomCardAction
from actions.combat import LoseHPAction, StartFightAction
from actions.display import InputRequestAction
from actions.reward import AddGoldAction, AddRandomRelicAction, AddRelicAction
from engine.game_state import game_state
from events.dead_adventurer import DeadAdventurer
from events.scrap_ooze import ScrapOoze
from events.the_colosseum import TheColosseum
from tests.test_combat_utils import create_test_helper
from utils.types import RarityType


def _requests() -> list[InputRequestAction]:
    return [
        cast(InputRequestAction, action)
        for action in game_state.action_queue.queue
        if isinstance(action, InputRequestAction)
    ]


def _options(event) -> list:
    game_state.action_queue.clear()
    event.trigger()
    return list(_requests()[-1].options)


def _run_lambdas(option) -> None:
    for action in option.actions:
        if isinstance(action, LambdaAction):
            action.execute()


def test_colosseum_fights_slavers_then_offers_victory_or_cowardice():
    helper = create_test_helper()
    helper.create_player()
    event = TheColosseum()
    game_state.action_queue.clear()

    event.trigger()

    assert event.event_ended is False
    requests = _requests()
    assert len(requests) == 1
    assert len(requests[0].options) == 1
    opening = requests[0].options[0]
    fight = next(action for action in opening.actions if isinstance(action, StartFightAction))
    fight = cast(StartFightAction, fight)
    assert [type(enemy).__name__ for enemy in fight.enemies] == ["BlueSlaver", "RedSlaver"]

    for action in fight.victory_actions:
        action.execute()

    assert event.first_fight_done is True
    assert event.event_ended is False
    options = list(_requests()[-1].options)
    victory, cowardice = options
    assert game_state.relic_pools.remaining["RARE"] is None
    assert game_state.relic_pools.remaining["UNCOMMON"] is None
    _run_lambdas(victory)
    second = cast(StartFightAction, game_state.action_queue.queue[0])
    assert [type(enemy).__name__ for enemy in second.enemies] == ["Taskmaster", "GremlinNob"]
    rewards = second.victory_actions
    assert any(isinstance(action, AddGoldAction) and action.amount == 100 for action in rewards)
    assert any(isinstance(action, AddRandomCardAction) for action in rewards)
    relics = [action.relic for action in rewards if isinstance(action, AddRelicAction)]
    assert [relic.rarity for relic in relics] == [RarityType.RARE, RarityType.UNCOMMON]
    assert all(relic not in game_state.player.relics for relic in relics)

    _run_lambdas(cowardice)
    assert event.event_ended is True


def test_dead_adventurer_rolls_the_current_search_and_counts_it_afterward(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 0
    event = DeadAdventurer()
    rolls = iter([25, 50, 75])
    shown = []

    def roll(low, high):
        assert (low, high) == (0, 99)
        return next(rolls)

    def choose(request):
        if len(request.options) == 1:
            assert event.search_count == 3
        else:
            shown.append(request.options[0].detail.kwargs["chance"])
        return [0]

    monkeypatch.setattr(get_rng("misc"), "randint", roll)
    monkeypatch.setattr(game_state, "_resolve_debug_selection", choose)
    options = _options(event)
    assert event.search_count == 0
    assert len(options) == 2
    game_state.drive_actions()
    assert shown == [25, 50, 75]
    assert event.search_count == 3
    assert event.rewards == []
    assert event.event_ended is True


def test_dead_adventurer_ascension_15_confirms_ambush_at_first_search(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 15
    event = DeadAdventurer()
    rolls = []

    def roll(low, high):
        rolls.append((low, high))
        return 34 if high == 99 else 30

    monkeypatch.setattr(get_rng("misc"), "randint", roll)
    options = _options(event)
    assert options[0].detail.kwargs["chance"] == 35
    assert rolls == []
    game_state.action_queue.clear()
    _run_lambdas(options[0])
    assert rolls == [(0, 99), (25, 35)]
    assert event.search_count == 0
    (fight_option,) = _requests()[-1].options
    _run_lambdas(fight_option)
    assert isinstance(game_state.action_queue.queue[0], StartFightAction)
    assert event.search_count == 1
    assert rolls == [(0, 99), (25, 35)]


def test_scrap_ooze_loses_hp_and_then_rolls(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = 0
    monkeypatch.setattr(get_rng("misc"), "random", lambda: 0.0)

    event = ScrapOoze()
    options = _options(event)

    assert event.attempt_count == 0
    assert event.relic_obtained is False
    assert event.event_ended is False
    reach = next(
        option
        for option in options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    hp_loss = next(action for action in reach.actions if isinstance(action, LoseHPAction))
    assert hp_loss.amount == 3
    assert not any(isinstance(action, AddRandomRelicAction) for action in reach.actions)

    for action in reach.actions:
        action.execute()

    assert player.hp == player.max_hp - 3
    assert event.relic_obtained is True
    assert event.attempt_count == 0
    queue = game_state.action_queue.queue
    relic_index = next(
        index
        for index, action in enumerate(queue)
        if isinstance(action, AddRandomRelicAction)
    )
    end = queue[relic_index + 1]
    assert isinstance(end, LambdaAction)
    end.execute()
    assert event.event_ended is True


def test_scrap_ooze_can_reach_again_after_a_failure(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = 15
    monkeypatch.setattr(get_rng("misc"), "random", lambda: 0.99)

    event = ScrapOoze()
    options = _options(event)
    reach = next(
        option
        for option in options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert next(action.amount for action in reach.actions if isinstance(action, LoseHPAction)) == 5
    assert event.event_ended is False

    for action in reach.actions:
        action.execute()

    assert player.hp == player.max_hp - 5
    assert event.attempt_count == 1
    assert event.relic_obtained is False
    assert event.event_ended is False
    again = next(
        option
        for option in _requests()[-1].options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert next(action.amount for action in again.actions if isinstance(action, LoseHPAction)) == 6

    leave = next(
        option
        for option in _requests()[-1].options
        if all(isinstance(action, LambdaAction) for action in option.actions)
    )
    _run_lambdas(leave)
    assert event.event_ended is True

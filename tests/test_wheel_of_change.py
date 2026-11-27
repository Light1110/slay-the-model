from typing import cast

from actions.display import DisplayTextAction, InputRequestAction
from actions.reward import AddGoldAction
from events.wheel_of_change import WheelOfChange
from engine.game_state import game_state
from rooms.event import EventRoom


def test_wheel_of_change_draws_when_player_spins_and_reveals_before_reward():
    game_state.current_act = 1
    rng = game_state.random_streams["misc"]
    rng.seed(3)
    before = rng.export_state()
    room = EventRoom()
    event = WheelOfChange()
    game_state.current_room = room
    room.selected_event = event
    room.enter()

    queue = game_state.action_queue
    menu = cast(InputRequestAction, queue.queue[-1])
    assert isinstance(menu, InputRequestAction)
    assert rng.export_state() == before
    assert not room.should_leave

    queue.clear()
    submission = game_state.resolve_input_request(menu.request)
    queue.add_actions(submission.actions)
    queue.execute_next()

    assert room.should_leave
    reveal, reward = queue.queue
    assert isinstance(reveal, DisplayTextAction)
    assert isinstance(reward, AddGoldAction) and cast(AddGoldAction, reward).amount == 100
    assert (rng.counter, rng.randint(0, 999)) == (1, 489)

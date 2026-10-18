"""Event: Secret Portal - Act 3 Shrine Event.

Skip to boss if 800+ seconds elapsed.
"""

from actions.display import DisplayTextAction, InputRequestAction
from actions.misc import SkipToBossAction
from engine.game_state import game_state
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(category='special', event_id="secret_portal", acts=[3], weight=100)
class SecretPortal(Event):
    """Secret Portal - skip to boss."""

    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if 800+ seconds (13:20) elapsed."""
        return game_state.current_act == 3 and game_state.elapsed_time >= 800

    def trigger(self) -> None:
        actions = []

        actions.append(DisplayTextAction(text_key="events.secret_portal.description"))

        options = [
            Option(
                name=LocalStr("events.secret_portal.enter"),
                detail=LocalStr('events.secret_portal.enter_detail'),
                actions=[SkipToBossAction()],
            ),
            Option(
                name=LocalStr("events.secret_portal.leave"),
                detail=LocalStr('events.no_effect'),
                actions=[],
            ),
        ]

        actions.append(
            InputRequestAction(
                title=LocalStr("events.secret_portal.title"),
                options=options,
            )
        )

        self.end_event()
        add_actions(actions)

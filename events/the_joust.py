"""The Joust settles both bets from one seeded race result."""
from typing import cast

from actions.base import LambdaAction
from actions.display import DisplayTextAction, InputRequestAction
from actions.reward import AddGoldAction, LoseGoldAction
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(category="special", event_id="the_joust", acts=[2], weight=100)
class TheJoust(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bet_for_owner: bool | None = None
        self._owner_wins: bool | None = None
        self._settled = False

    @classmethod
    def can_appear(cls) -> bool:
        return game_state.player.gold >= 50

    def trigger(self) -> None:
        if self._bet_for_owner is not None:
            return
        can_pay = self.can_appear()
        options = [
            Option(
                name=LocalStr(f"events.the_joust.{side}"),
                disabled_reason=LocalStr("events.require_gold", gold=50),
                detail=LocalStr(f"events.the_joust.{side}_detail"),
                actions=[LambdaAction(self._place_bet, args=(for_owner,))],
                enabled=can_pay,
            )
            for side, for_owner in (("murderer", False), ("owner", True))
        ]
        if not can_pay:
            options.append(Option(LocalStr("events.the_joust.leave"), [LambdaAction(self.end_event)]))
        add_actions([
            DisplayTextAction(text_key="events.the_joust.description"),
            InputRequestAction(title=LocalStr("events.the_joust.title"), options=options),
        ])

    def _place_bet(self, for_owner: bool) -> None:
        if self._bet_for_owner is not None or not self.can_appear() or self.event_ended:
            return
        self._bet_for_owner = for_owner
        add_actions([
            LoseGoldAction(amount=50),
            InputRequestAction(options=[
                Option(LocalStr("events.the_joust.start"), [LambdaAction(self._start_joust)]),
            ]),
        ], to_front=True)

    def _start_joust(self) -> None:
        if self._bet_for_owner is None or self._owner_wins is not None:
            return
        self._owner_wins = cast(StreamRandom, get_rng("misc")).random_boolean(0.3)
        add_actions([
            InputRequestAction(options=[
                Option(LocalStr("events.the_joust.reveal"), [LambdaAction(self._settle)]),
            ]),
        ], to_front=True)

    def _settle(self) -> None:
        if self._owner_wins is None or self._settled:
            return
        self._settled = True
        outcome = "owner_wins" if self._owner_wins else "murderer_wins"
        actions = [DisplayTextAction(text_key=f"events.the_joust.{outcome}")]
        if self._bet_for_owner == self._owner_wins:
            actions.append(AddGoldAction(amount=250 if self._owner_wins else 100))
        actions.append(InputRequestAction(options=[
            Option(LocalStr("events.the_joust.leave"), [LambdaAction(self.end_event)]),
        ]))
        add_actions(actions, to_front=True)

"""Event: Mysterious Sphere - Act 3 Event

Fight 2 Orb Walkers for relic reward.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.base import LambdaAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseObtainCardAction
from actions.reward import AddGoldAction, AddRelicAction
from actions.combat import StartFightAction
from enemies.act3.orb_walker import OrbWalker
from engine.game_state import game_state
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType


@register_event(category='event', event_id='mysterious_sphere', acts=[3], weight=100)
class MysteriousSphere(Event):
    """Mysterious Sphere - fight for relic."""

    def __init__(self):
        super().__init__()
        self.orb_walkers = [OrbWalker(), OrbWalker()]
        for enemy, position in zip(self.orb_walkers, (-250, 150)):
            enemy.formation_position = position

    def _gold_range(self) -> tuple[int, int]:
        return (0, 50) if game_state.config.daily_run else (45, 55)

    def trigger(self) -> None:
        minimum, maximum = self._gold_range()
        options = [
            Option(
                name=LocalStr('events.mysterious_sphere.open_sphere'),
                detail=LocalStr('events.mysterious_sphere.open_sphere_detail',
                                minimum=minimum, maximum=maximum),
                actions=[LambdaAction(self._open)],
            ),
            Option(
                name=LocalStr('events.mysterious_sphere.leave'),
                detail=LocalStr('events.no_effect'),
                actions=[LambdaAction(self.end_event)],
            )
        ]
        add_actions([
            DisplayTextAction(text_key='events.mysterious_sphere.description'),
            InputRequestAction(title=LocalStr('events.mysterious_sphere.title'), options=options),
        ])

    def _open(self) -> None:
        add_action(InputRequestAction(
            title=LocalStr("events.mysterious_sphere.title"),
            options=[Option(name=LocalStr("events.mysterious_sphere.fight"),
                            actions=[LambdaAction(self._fight)])],
        ), to_front=True)

    def _fight(self) -> None:
        gold = AddGoldAction(amount=get_rng("misc").randint(*self._gold_range()), source="event_combat")
        pool = game_state.relic_pools
        relic = pool.draw(RarityType.RARE)
        while relic.idstr in {"BottledFlame", "BottledLightning", "BottledTornado", "Whetstone"}:
            relic = pool.draw(RarityType.RARE)
        add_action(StartFightAction(
            enemies=self.orb_walkers,
            victory_actions=[
                gold,
                AddRelicAction(relic),
                ChooseObtainCardAction(
                    namespace=game_state.player.namespace, pile="deck", can_skip=True,
                    encounter_type="normal", use_rolling_offset=True, allow_upgraded=True,
                ),
                LambdaAction(self.end_event),
            ],
            escape_actions=[LambdaAction(self.end_event)],
        ), to_front=True)

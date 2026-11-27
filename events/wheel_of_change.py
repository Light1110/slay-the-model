"""Event: Wheel of Change - Shrine Event (All Acts)

Spin a wheel for random outcomes: gold, relic, heal, curse, remove card, or damage.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.base import LambdaAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.card import ChooseRemoveCardAction, AddCardAction
from actions.combat import HealAction, LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Decay


@register_event(category='shrine', event_id='wheel_of_change', acts='shared', weight=100)
class WheelOfChange(Event):
    """Wheel of Change - random outcome wheel."""

    @staticmethod
    def _build_result_actions(result_key: str, outcome_action, **fmt):
        return [DisplayTextAction(text_key=result_key, **fmt), outcome_action]
    
    def trigger(self) -> None:
        act_gold = {1: 100, 2: 200, 3: 300, 4: 300}
        gold_amount = act_gold.get(game_state.current_act, 100)
        hp_loss_percent = 0.15 if game_state.ascension >= 15 else 0.10

        add_actions([
            DisplayTextAction(text_key="events.wheel_of_change.description"),
            InputRequestAction(title=LocalStr("events.wheel_of_change.title"), options=[
                Option(
                    name=LocalStr("events.wheel_of_change.play"),
                    detail=LocalStr(
                        "events.wheel_of_change.play_detail",
                        gold=gold_amount,
                        hp=int(game_state.player.max_hp * hp_loss_percent),
                    ),
                    actions=[LambdaAction(self._spin, args=(gold_amount, hp_loss_percent))],
                )
            ]),
        ])

    def _spin(self, gold_amount: int, hp_loss_percent: float) -> None:
        excluded_relics = ["BottledFlame", "BottledLightning", "BottledTornado", "Whetstone"]
        outcomes = [
            self._build_result_actions(
                "events.wheel_of_change.result_gold",
                AddGoldAction(amount=gold_amount),
                amount=gold_amount,
            ),
            self._build_result_actions(
                "events.wheel_of_change.result_relic",
                AddRandomRelicAction(exclude_relics=excluded_relics),
            ),
            self._build_result_actions(
                "events.wheel_of_change.result_heal",
                HealAction(percent=1.0),
            ),
            self._build_result_actions(
                "events.wheel_of_change.result_decay",
                AddCardAction(card=Decay()),
            ),
            self._build_result_actions(
                "events.wheel_of_change.result_remove",
                ChooseRemoveCardAction(),
            ),
            self._build_result_actions(
                "events.wheel_of_change.result_damage",
                LoseHPAction(percent=hp_loss_percent),
                percent=int(hp_loss_percent * 100),
            ),
        ]
        add_actions(get_rng("misc").choice(outcomes), to_front=True)
        self.end_event()

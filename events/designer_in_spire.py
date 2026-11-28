"""Designer In-Spire offers fixed, seeded deck services."""
from typing import cast

from actions.base import Action, LambdaAction
from actions.card import (
    ChooseUpgradeCardAction, RemoveCardAction, TransformCardAction, UpgradeRandomCardAction,
)
from actions.combat import LoseHPAction
from actions.display import DisplayTextAction, InputRequestAction
from actions.reward import LoseGoldAction
from engine.card_pools import original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(category="special", event_id="designer_in_spire", acts=[2, 3], weight=100)
class DesignerInSpire(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rng = cast(StreamRandom, get_rng("misc"))
        self.adjustment_upgrades_one = rng.random_boolean()
        self.cleanup_removes_one = rng.random_boolean()
        self._service_selected = False

    @classmethod
    def can_appear(cls) -> bool:
        return game_state.player.gold >= 75

    def trigger(self) -> None:
        if self._service_selected:
            return
        player = game_state.player
        adjust_cost, clean_cost, full_cost, punch_hp = (
            (50, 75, 110, 5) if game_state.ascension >= 15 else (40, 60, 90, 3)
        )
        upgradable = any(card.can_upgrade() for card in player.deck)
        bottled = {id(getattr(relic, "selected_card", None)) for relic in player.relics}
        protected = {"Necronomicurse", "CurseOfTheBell", "AscendersBane"}
        purgeable = [
            card for card in player.deck
            if not card.bottled and id(card) not in bottled and original_id(card) not in protected
        ]
        if self.adjustment_upgrades_one:
            adjustment = ChooseUpgradeCardAction(pile="deck")
            adjustment_detail = "adjust_one_detail"
        else:
            adjustment = UpgradeRandomCardAction(count=2, selection_kind="shuffle")
            adjustment_detail = "adjust_random_detail"

        remove = InputRequestAction(
            title=LocalStr("ui.choose_cards_to_remove"),
            options=[Option(card.info(), [RemoveCardAction(card=card, src_pile="deck")])
                     for card in purgeable],
        )
        if self.cleanup_removes_one:
            cleanup = remove
            cleanup_detail = "clean_remove_detail"
            cleanup_count = 1
        else:
            cleanup = InputRequestAction(
                title=LocalStr("ui.choose_cards_to_transform"),
                options=[Option(card.info(), [TransformCardAction(card=card, pile="deck")])
                         for card in purgeable],
                max_select=2,
            )
            cleanup_detail = "clean_transform_detail"
            cleanup_count = 2

        options = [
            self._service_option("adjustments", adjustment_detail, adjust_cost, upgradable, [adjustment]),
            self._service_option("clean_up", cleanup_detail, clean_cost, len(purgeable) >= cleanup_count, [cleanup]),
            self._service_option("full_service", "full_service_detail", full_cost, bool(purgeable),
                                 [remove, UpgradeRandomCardAction(selection_kind="shuffle")]),
            Option(
                name=LocalStr("events.designer_in_spire.punch"),
                detail=LocalStr("events.designer_in_spire.punch_detail", hp=punch_hp),
                actions=[LambdaAction(self._purchase, args=(0, [LoseHPAction(amount=punch_hp)]))],
            ),
        ]
        add_actions([
            DisplayTextAction(text_key="events.designer_in_spire.description"),
            InputRequestAction(title=LocalStr("events.designer_in_spire.title"), options=options),
        ])

    def _service_option(self, name: str, detail: str, cost: int, has_cards: bool, effects: list[Action]) -> Option:
        can_pay = game_state.player.gold >= cost
        return Option(
            name=LocalStr(f"events.designer_in_spire.{name}"),
            detail=LocalStr(f"events.designer_in_spire.{detail}", gold=cost),
            disabled_reason=(LocalStr("events.require_gold", gold=cost) if not can_pay
                             else LocalStr("events.designer_in_spire.not_enough_cards")),
            enabled=can_pay and has_cards,
            actions=[LambdaAction(self._purchase, args=(cost, effects))],
        )

    def _purchase(self, cost: int, effects: list[Action]) -> None:
        if self._service_selected or game_state.player.gold < cost:
            return
        self._service_selected = True
        payment = [LoseGoldAction(amount=cost)] if cost else []
        add_actions([*payment, *effects, LambdaAction(self.end_event)], to_front=True)

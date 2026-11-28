"""Falling offers one preselected loss per eligible card type."""
from actions.base import LambdaAction
from actions.card import RemoveCardAction
from actions.display import DisplayTextAction, InputRequestAction
from cards.base import Card
from engine.game_state import game_state
from engine.random_streams import get_rng
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import CardType


@register_event(category="event", event_id="falling", acts=[3], weight=100)
class Falling(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._presented = False
        self._targets: dict[CardType, Card] = {}
        player = game_state.player
        if player is None:
            return

        bound = {id(getattr(relic, "selected_card", None)) for relic in player.relics}
        deck = [card for card in player.deck if not card.bottled and id(card) not in bound]
        rng = get_rng("misc")
        for card_type in (CardType.ATTACK, CardType.SKILL, CardType.POWER):
            candidates = [card for card in deck if card.card_type == card_type]
            if candidates:
                self._targets[card_type] = rng.choice(candidates)

    def trigger(self) -> None:
        if self._presented:
            return
        self._presented = True

        if self._targets:
            options = [
                self._loss_option("land", CardType.SKILL),
                self._loss_option("channel", CardType.POWER),
                self._loss_option("strike", CardType.ATTACK),
            ]
        else:
            options = [Option(
                name=LocalStr("events.falling.leave"),
                detail=LocalStr("events.no_effect"),
                actions=[LambdaAction(self.end_event)],
            )]
        add_actions([
            DisplayTextAction(text_key="events.falling.description"),
            InputRequestAction(title=LocalStr("events.falling.title"), options=options),
        ])

    def _loss_option(self, name: str, card_type: CardType) -> Option:
        card = self._targets.get(card_type)
        if card is None:
            return Option(
                LocalStr(f"events.falling.{name}"), [], enabled=False,
                detail=LocalStr("events.falling.no_eligible_card"),
            )
        return Option(
            name=LocalStr(f"events.falling.{name}_with_card", card=card.display_name),
            detail=card.info(),
            actions=[LambdaAction(self._resolve_loss, args=(card,))],
        )

    def _resolve_loss(self, card: Card) -> None:
        if self.event_ended:
            return
        RemoveCardAction(card, "deck").execute()
        self.end_event()

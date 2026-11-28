"""Trade a preselected potion, amount of gold, or card for a relic."""
from actions.base import Action, LambdaAction
from actions.card import RemoveCardAction
from actions.display import DisplayTextAction, InputRequestAction
from actions.reward import AddRandomRelicAction, LoseGoldAction, LosePotionAction
from engine.card_pools import original_rarity
from engine.game_state import game_state
from engine.random_streams import get_rng
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import CardType, RarityType


@register_event(category="special", event_id="we_meet_again", acts="shared", weight=100)
class WeMeetAgain(Event):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        player = game_state.player
        rng = get_rng("misc")
        potions = [potion for potion in player.potions if potion is not None]
        if potions:
            rng.shuffle(potions)
        self.potion_option = potions[0] if potions else None
        self.gold_amount = rng.randint(50, min(150, player.gold)) if player.gold >= 50 else 0
        cards = [card for card in player.deck
                 if original_rarity(card) != RarityType.STARTER and card.card_type != CardType.CURSE]
        if cards:
            rng.shuffle(cards)
        self.card_option = cards[0] if cards else None
        self._exchange_done = False

    def trigger(self) -> None:
        if self.event_ended or self._exchange_done:
            return
        potion = self.potion_option
        card = self.card_option
        if potion is not None and self._payment_for("potion") is not None:
            potion.event_locked = True

        potion_name = LocalStr("events.we_meet_again.give_potion")
        if potion is not None:
            potion_name += "  " + potion.local("name")
        card_name = LocalStr("events.we_meet_again.give_card")
        if card is not None:
            card_name += "  " + card.display_name

        options = [
            Option(
                name=potion_name + "  " + LocalStr("events.we_meet_again.give_potion_effect"),
                enabled=self._payment_for("potion") is not None,
                actions=[LambdaAction(self._trade, args=("potion",))],
            ),
            Option(
                name=LocalStr("events.we_meet_again.give_gold")
                     + "  " + LocalStr("events.we_meet_again.give_gold_effect", amount=self.gold_amount),
                enabled=self._payment_for("gold") is not None,
                actions=[LambdaAction(self._trade, args=("gold",))],
            ),
            Option(
                name=card_name + "  " + LocalStr("events.we_meet_again.give_card_effect"),
                enabled=self._payment_for("card") is not None,
                actions=[LambdaAction(self._trade, args=("card",))],
            ),
            Option(
                name=LocalStr("events.we_meet_again.attack")
                     + "  " + LocalStr("events.we_meet_again.attack_effect"),
                actions=[LambdaAction(self.end_event)],
            ),
        ]
        add_actions([
            DisplayTextAction(text_key="events.we_meet_again.description"),
            InputRequestAction(title=LocalStr("events.we_meet_again.title"), options=options),
        ])

    def _payment_for(self, kind: str) -> Action | None:
        player = game_state.player
        if kind == "potion":
            potion = self.potion_option
            if potion is not None and any(item is potion for item in player.potions):
                return LosePotionAction(potion=potion)
        elif kind == "gold":
            if 0 < self.gold_amount <= player.gold:
                return LoseGoldAction(amount=self.gold_amount)
        elif kind == "card":
            card = self.card_option
            if card is not None and any(item is card for item in player.deck):
                return RemoveCardAction(card=card, src_pile="deck")
        return None

    def _trade(self, kind: str) -> None:
        if self.event_ended or self._exchange_done:
            return
        payment = self._payment_for(kind)
        if payment is None:
            self.trigger()
            return
        self._exchange_done = True
        add_actions([payment, AddRandomRelicAction(), LambdaAction(self.end_event)], to_front=True)

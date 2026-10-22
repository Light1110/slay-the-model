"""Knowing Skull: independent, repeatable HP costs for each reward."""
from actions.base import LambdaAction
from actions.card import AddRandomCardAction
from actions.combat import LoseHPAction
from actions.display import DisplayTextAction, InputRequestAction
from actions.reward import AddGoldAction, AddRandomPotionAction
from engine.game_state import game_state
from engine.runtime_api import add_actions
from events.base_event import Event
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType


@register_event(category='special', event_id='knowing_skull', acts=[2], weight=100)
class KnowingSkull(Event):
    """Each reward starts at 6 HP and increases only its own cost; leaving costs 6."""

    @classmethod
    def can_appear(cls) -> bool:
        return game_state.player is not None and game_state.player.hp >= 13

    def __init__(self):
        super().__init__()
        self.potion_cost = 6
        self.gold_cost = 6
        self.card_cost = 6
        self.leave_cost = 6
        self._intro_shown = False

    def _payment_actions(self, choice: str, cost: int):
        return [LoseHPAction(amount=cost), LambdaAction(self._after_payment, args=[choice])]

    def trigger(self) -> None:
        actions = []
        if not self._intro_shown:
            actions.append(DisplayTextAction(text_key='events.knowing_skull.description'))
            self._intro_shown = True
        options = [
            Option(
                name=LocalStr('events.knowing_skull.potion'),
                detail=LocalStr('events.knowing_skull.potion_detail', hp=self.potion_cost),
                actions=self._payment_actions('potion', self.potion_cost),
            ),
            Option(
                name=LocalStr('events.knowing_skull.riches'),
                detail=LocalStr('events.knowing_skull.riches_detail', hp=self.gold_cost, gold=90),
                actions=self._payment_actions('gold', self.gold_cost),
            ),
            Option(
                name=LocalStr('events.knowing_skull.success'),
                detail=LocalStr('events.knowing_skull.success_detail', hp=self.card_cost),
                actions=self._payment_actions('card', self.card_cost),
            ),
            Option(
                name=LocalStr('events.knowing_skull.leave'),
                detail=LocalStr('events.lose_hp', hp=self.leave_cost),
                actions=self._payment_actions('leave', self.leave_cost),
            ),
        ]
        actions.append(InputRequestAction(title=LocalStr('events.knowing_skull.title'), options=options))
        add_actions(actions)

    def _after_payment(self, choice: str) -> None:
        """Do not grant rewards or open another menu after a lethal HP payment."""
        player = game_state.player
        if player is None:
            return
        if player.is_dead():
            self.end_event()
            # LoseHPAction has already queued the formal death action. Let it
            # finish after this callback instead of leaving it behind a second
            # terminal result from the event.
            return
        if choice == 'leave':
            self.end_event()
            return
        if choice == 'potion':
            reward = AddRandomPotionAction(character=player.character)
        elif choice == 'gold':
            reward = AddGoldAction(amount=90)
        else:
            reward = AddRandomCardAction(pile='deck', namespace='colorless', rarity=RarityType.UNCOMMON)
        add_actions([
            reward,
            LambdaAction(self._increment_cost, args=[choice]),
            LambdaAction(self._continue_or_end),
        ], to_front=True)

    def _increment_cost(self, choice: str) -> None:
        field = {'potion': 'potion_cost', 'gold': 'gold_cost', 'card': 'card_cost'}[choice]
        setattr(self, field, getattr(self, field) + 1)

    def _continue_or_end(self) -> None:
        if bool(getattr(game_state.config, 'auto_select', False)):
            # Keep automatic runs bounded, but use the same paid exit as the menu.
            add_actions(self._payment_actions('leave', self.leave_cost), to_front=True)
        else:
            self.trigger()

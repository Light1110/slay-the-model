"""Event: The Divine Fountain - Shrine Event (All Acts)

Remove all curses from the deck. Only appears if deck has at least one curse.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import RemoveCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from utils.types import CardType
from cards.colorless.ascenders_bane import AscendersBane
from cards.colorless.curse_of_the_bell import CurseOfTheBell
from cards.colorless.necronomicurse import Necronomicurse


def _eligible_curse(card) -> bool:
    return card.card_type == CardType.CURSE and not isinstance(
        card, (AscendersBane, CurseOfTheBell, Necronomicurse),
    )


@register_event(event_id='divine_fountain', acts='shared', weight=100)
class DivineFountain(Event):
    """Divine Fountain - remove all curses."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if deck has at least one curse."""
        player = game_state.player
        if player is None:
            return False
        return any(_eligible_curse(card) for card in player.deck)
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.divine_fountain.description'
        ))
        
        # Get all curse cards and create remove actions
        curse_cards = [
            card for card in game_state.player.deck
            if _eligible_curse(card) and not card.bottled
        ]
        remove_actions = [RemoveCardAction(card=card, src_pile='deck') for card in curse_cards]
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.divine_fountain.drink'),
                detail=LocalStr('events.divine_fountain.drink_detail', count=len(remove_actions)),
                actions=remove_actions
            ),
            Option(
                name=LocalStr('events.divine_fountain.leave'),
                detail=LocalStr('events.no_effect'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.divine_fountain.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)

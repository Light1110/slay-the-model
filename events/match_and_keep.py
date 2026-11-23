"""Event: Match and Keep - Shrine Event (All Acts)

A card matching minigame where you flip cards and match pairs to add them to your deck.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from typing import List, Tuple
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.base import Action
from utils.registry import register
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from engine.card_pools import CURSE_TRANSFORM_IDS, current_pools, definitions
from engine.card_previews import preview_deck_card
from cards.base import Card
from utils.random import get_random_card
from utils.types import RarityType


# Global state for the matching minigame (per event instance)
_matching_state = {}
_STARTER_BY_CHARACTER = {
    "ironclad": "Bash",
    "silent": "Neutralize",
    "defect": "Zap",
    "watcher": "Eruption",
}


def _generate_card_pairs() -> List[Tuple[Card, Card]]:
    """Generate pairs in their pre-shuffle slot order."""
    cards: list[Card] = []
    namespace = game_state.player.namespace
    catalog = definitions()
    rng = get_rng("card")
    for rarity in (RarityType.RARE, RarityType.UNCOMMON, RarityType.COMMON):
        selected = get_random_card(
            namespaces=[namespace], rarities=[rarity], rng=rng, pool_kind="current",
        )
        if selected is not None:
            cards.append(selected)

    high_ascension = game_state.ascension >= 15
    if not high_ascension:
        colorless = current_pools().current[("colorless", None)]
        get_rng("shuffle").shuffle(colorless)
        colorless_id = next(
            (card_id for card_id in colorless if catalog[card_id].rarity == "UNCOMMON"),
            "Swift Strike",
        )
        cards.append(catalog[colorless_id].make_card())

    for _ in range(2 if high_ascension else 1):
        curse_id = CURSE_TRANSFORM_IDS[rng.randint(0, len(CURSE_TRANSFORM_IDS) - 1)]
        cards.append(catalog[curse_id].make_card())

    starter_id = _STARTER_BY_CHARACTER.get(namespace)
    if starter_id is not None:
        cards.append(catalog[starter_id].make_card())
    pairs = []
    for card in cards:
        preview_deck_card(card, game_state.player.relics)
        pairs.append((card, card.copy()))
    return pairs


def _create_shuffled_deck(pairs: List[Tuple[Card, Card]]) -> List[dict]:
    """Create a shuffled deck of 12 cards from 6 pairs."""
    cards = []
    for member in (0, 1):
        for pair in pairs:
            card = pair[member]
            cards.append({
                'card': card,
                'idstr': card.idstr,
                'revealed': False,
                'matched': False,
            })
    get_rng("misc").shuffle(cards)
    return cards


@register_event(category='shrine', event_id='match_and_keep', acts='shared', weight=100)
class MatchAndKeep(Event):
    """Match and Keep - card matching minigame."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._board = _create_shuffled_deck(_generate_card_pairs())

    @classmethod
    def can_appear(cls) -> bool:
        """Can appear in any act."""
        return True
    
    def trigger(self) -> None:
        global _matching_state
        
        # Older saved event instances did not have a prepared board.
        if not hasattr(self, "_board"):
            self._board = _create_shuffled_deck(_generate_card_pairs())

        _matching_state = {
            'deck': [entry.copy() for entry in self._board],
            'tries_remaining': 5,
            'matched_cards': [],
            'first_selection': None,
            'phase': 'select_first',  # 'select_first', 'select_second', 'game_over'
        }
        
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.match_and_keep.description'
        ))
        
        # Start the minigame
        actions.append(MatchAndKeepAction())
        
        self.end_event()
        add_actions(actions)


@register("action")
class MatchAndKeepAction(Action):
    """Interactive matching minigame action."""
    
    def execute(self) -> None:
        global _matching_state
        
        if not _matching_state:
            return
        
        # Check if game is over
        if _matching_state['tries_remaining'] <= 0:
            add_actions(self._end_game(), to_front=True)
            return
        
        # Check if all cards matched
        unmatched = [c for c in _matching_state['deck'] if not c['matched']]
        if not unmatched:
            add_actions(self._end_game(), to_front=True)
            return
        
        # Build selection options for face-down cards
        options = []
        for i, card_data in enumerate(_matching_state['deck']):
            if card_data['matched']:
                # Show matched card
                options.append(Option(
                    name=LocalStr('events.match_and_keep.matched', card=card_data['card'].info()),
                    detail=LocalStr('events.match_and_keep.matched_detail'),
                    actions=[],
                    enabled=False
                ))
            elif card_data['revealed']:
                # Show revealed but not matched
                options.append(Option(
                    name=LocalStr('events.match_and_keep.face_up', card=card_data['card'].info()),
                    detail=LocalStr('events.match_and_keep.face_up_detail'),
                    actions=[],
                    enabled=False
                ))
            else:
                # Face-down card - can be selected
                options.append(Option(
                    name=LocalStr('events.match_and_keep.face_down', number=i + 1),
                    detail=LocalStr('events.match_and_keep.flip_detail'),
                    actions=[FlipCardAction(card_index=i)]
                ))
        
        # Show tries remaining
        tries_text = f"Tries remaining: {_matching_state['tries_remaining']}"
        
        add_action(
            InputRequestAction(
                title=LocalStr(
                    'events.match_and_keep.select_card',
                    default=f"Select a card to flip. {tries_text}",
                    tries=_matching_state['tries_remaining'],
                ),
                options=options,
                max_select=1,
                must_select=True,
            ),
            to_front=True,
        )
    
    def _end_game(self) -> list:
        """End the minigame and add matched cards to deck."""
        global _matching_state
        
        actions = []
        
        # Add all matched cards to player's deck
        for card in _matching_state['matched_cards']:
            actions.append(AddCardAction(card=card, dest_pile='deck'))
        
        # Display results
        if _matching_state['matched_cards']:
            card_names = ', '.join(str(c.info()) for c in _matching_state['matched_cards'])
            actions.append(DisplayTextAction(
                text_key='events.match_and_keep.won_cards',
                default=f"You matched: {card_names}",
                cards=card_names,
            ))
        else:
            actions.append(DisplayTextAction(
                text_key='events.match_and_keep.no_matches',
                default="You didn't match any cards.",
            ))
        
        # Clear state
        _matching_state = {}
        
        return actions


@register("action")
class FlipCardAction(Action):
    """Flip a card in the matching minigame."""
    
    def __init__(self, card_index: int):
        self.card_index = card_index
    
    def execute(self) -> None:
        global _matching_state
        
        if not _matching_state:
            return
        
        deck = _matching_state['deck']
        
        if self.card_index < 0 or self.card_index >= len(deck):
            return
        
        card_data = deck[self.card_index]
        
        # Can't flip matched or already revealed cards
        if card_data['matched'] or card_data['revealed']:
            return
        
        # Flip the card
        card_data['revealed'] = True
        
        first_index = _matching_state['first_selection']
        if first_index is None:
            # First card of the pair
            _matching_state['first_selection'] = self.card_index
            # Continue selecting
            add_action(MatchAndKeepAction(), to_front=True)
            return

        first_card = deck[first_index]
        if first_card['idstr'] == card_data['idstr']:
            first_card['matched'] = True
            card_data['matched'] = True
            _matching_state['matched_cards'].append(card_data['card'])
        else:
            first_card['revealed'] = False
            card_data['revealed'] = False

        _matching_state['tries_remaining'] -= 1
        _matching_state['first_selection'] = None
        add_action(MatchAndKeepAction(), to_front=True)

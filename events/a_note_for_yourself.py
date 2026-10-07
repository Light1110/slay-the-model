"""Event: A Note For Yourself - Shrine Event (All Acts, disabled A15+)

Cross-run card storage event that allows receiving a card from previous run
and storing a card for future runs.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

import json
from pathlib import Path
from typing import Optional

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.base import Action
from actions.card import AddCardAction, RemoveCardAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.base import Card
from cards.namespaces import namespace_from_module
from utils.registry import register
from utils.types import CardType, RarityType

# Path for storing cross-run data
STORAGE_FILE = Path(__file__).parent.parent / "save_data" / "note_storage.json"


def _load_stored_card() -> Optional[dict]:
    """Load stored card data from previous run."""
    try:
        if STORAGE_FILE.exists():
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('stored_card')
    except (json.JSONDecodeError, IOError):
        pass
    return None


def _save_stored_card(card_data: Optional[dict]):
    """Save card data for future runs."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'stored_card': card_data}, f)
    except IOError:
        pass


def _card_to_dict(card: Card) -> dict:
    """Convert card to storable dictionary."""
    return {
        'namespace': card.namespace,
        'name': card.__class__.__name__,
        'upgrade_level': int(card.upgrade_level),
    }


def _find_card_class(namespace: str, name: str):
    """Find a card class by character namespace and class name."""
    import importlib
    import pkgutil

    try:
        package = importlib.import_module(f"cards.{namespace}")
    except ModuleNotFoundError:
        return None
    prefix = package.__name__ + "."
    for _, module_name, _ in pkgutil.walk_packages(package.__path__, prefix):
        module = importlib.import_module(module_name)
        card_cls = getattr(module, name, None)
        if isinstance(card_cls, type) and card_cls.__name__ == name:
            if namespace_from_module(card_cls.__module__) == namespace:
                return card_cls
    return None


def _dict_to_card(data: dict) -> Optional[Card]:
    """Recreate card from stored dictionary."""
    namespace = data.get('namespace') if data else None
    name = data.get('name') if data else None
    if not namespace or not name:
        return None

    card_cls = _find_card_class(namespace, name)
    if card_cls is None:
        return None
    card = card_cls()
    for _ in range(int(data.get('upgrade_level', 0) or 0)):
        card.upgrade()
    return card


def _received_card() -> Card:
    """The card on the note. An unupgraded Iron Wave is the default."""
    stored = _dict_to_card(_load_stored_card() or {})
    if stored is not None:
        return stored
    from cards.ironclad.iron_wave import IronWave
    return IronWave()


def _can_leave(card: Card) -> bool:
    return card.rarity != RarityType.CURSE and card.card_type != CardType.CURSE


def _leave_choice(deck_cards: list, received: Card) -> InputRequestAction:
    options = []
    for card in deck_cards:
        if not _can_leave(card):
            continue
        options.append(Option(
            name=str(card.display_name),
            actions=[
                RemoveCardAction(card=card, src_pile='deck'),
                StoreCardForFutureAction(card),
                AddCardAction(card=received, dest_pile='deck'),
            ],
        ))
    return InputRequestAction(
        title=LocalStr('events.a_note_for_yourself.take_and_give'),
        options=options,
    )


@register_event(event_id='a_note_for_yourself', acts='shared', weight=100)
class ANoteForYourself(Event):
    """A Note For Yourself - cross-run card storage."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Disabled on Ascension 15+ and Daily Climb."""
        if game_state.ascension >= 15:
            return False
        # Also disabled in Daily Climb (not implemented yet)
        return True
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.a_note_for_yourself.description'
        ))
        
        # The note always holds a card. With no save, that card is Iron Wave.
        received = _received_card()
        deck_cards = list(game_state.player.deck) if game_state.player is not None else []
        leave_choice = _leave_choice(deck_cards, received)

        options = []
        if leave_choice.options:
            options.append(Option(
                name=LocalStr('events.a_note_for_yourself.take_and_give'),
                actions=[leave_choice],
            ))

        options.append(Option(
            name=LocalStr('events.a_note_for_yourself.ignore'),
            actions=[]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.a_note_for_yourself.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)


@register("action")
class StoreCardForFutureAction(Action):
    """Store one chosen card for a future run."""

    def __init__(self, card: Card):
        self.card = card

    def execute(self) -> None:
        _save_stored_card(_card_to_dict(self.card))

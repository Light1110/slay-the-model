"""Event: The Mausoleum - Act 2 Event

Relic with 50% (100% A15+) Writhe curse chance.
"""
from typing import cast
from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.base import Action, LambdaAction
from actions.card_lifecycle import AddCardAction, try_block_curse_with_omamori
from actions.reward import AddRandomRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Writhe


@register_event(category='event', event_id='the_mausoleum', acts=[2], weight=100)
class TheMausoleum(Event):
    """The Mausoleum - relic with curse risk."""
    
    def trigger(self) -> None:
        curse_chance = 100 if game_state.ascension >= 15 else 50
        options = [
            Option(
                name=LocalStr('events.the_mausoleum.open_coffin'),
                detail=LocalStr('events.the_mausoleum.open_coffin_detail', chance=curse_chance),
                actions=[LambdaAction(self._open_coffin)],
            ),
            Option(
                name=LocalStr('events.the_mausoleum.leave'),
                detail=LocalStr('events.no_effect'),
                actions=[LambdaAction(self.end_event)],
            )
        ]
        
        add_actions([
            DisplayTextAction(text_key='events.the_mausoleum.description'),
            InputRequestAction(title=LocalStr('events.the_mausoleum.title'), options=options),
        ])

    def _open_coffin(self) -> None:
        cursed = cast(StreamRandom, get_rng("misc")).random_boolean()
        actions: list[Action] = [AddRandomRelicAction()]
        if cursed or game_state.ascension >= 15:
            curse = Writhe()
            if not try_block_curse_with_omamori(game_state.player, curse):
                # The awarded relic can react to the card, but cannot block it.
                actions.append(AddCardAction(curse, omamori_checked=True))
        actions.append(LambdaAction(self.end_event))
        add_actions(actions, to_front=True)

"""Event: Bonfire Spirits - Shrine Event (All Acts)

Sacrifice a card to the spirits for rewards based on card rarity.
- Basic: Nothing
- Common: Heal 5 HP
- Uncommon: Full heal
- Rare: +10 Max HP + Full heal
- Curse: Receive Spirit Poop relic (TODO: implement relic)
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.combat import HealAction, ModifyMaxHpAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='bonfire_spirits', acts='shared', weight=100)
class BonfireSpirits(Event):
    """Bonfire Spirits - sacrifice card for reward by rarity."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.bonfire_spirits.description'
        ))
        
        # Build options
        # TODO: Implement proper card sacrifice with rarity-based rewards
        """
        You happen upon what looks like a group of purple fire spirits dancing around a large bonfire.
Before selecting [Offer]

The spirits toss small bones and fragments into the fire, which brilliantly erupts each time.
As you approach, the spirits all turn to you, expectantly...

[Offer]

You toss an offering into the bonfire.
When offering a Basic card

Nothing happens...
The spirits seem to be ignoring you now. Disappointing...

When offering a Common card

The flames grow slightly brighter.
The spirits continue dancing. You feel slightly warmer from their presence..
You heal 5 HP.

When offering an Uncommon card

The flames erupt, growing significantly stronger!
The spirits dance around you excitedly, filling you with a sense of warmth.
You are healed to full HP.

When offering a Rare card

The flames burst, nearly knocking you off your feet, as the fire doubles in strength.
The spirits dance around you excitedly before merging into your form, filling you with warmth and strength.
Your Max HP increases by 10 and you are healed to full HP.

When offering a Curse

However, the spirits aren't happy you offered a Curse...
The card fizzles a meek black smoke. You receive a... something in return.
(Gives 🧪 Spirit Poop)

        """
        # For now, use ChooseRemoveCardAction with heal reward
        options = [
            Option(
                name=LocalStr('events.bonfire_spirits.offer'),
                actions=[
                    ChooseRemoveCardAction(),
                    HealAction(amount=5)  # Simplified reward
                ]
            ),
            Option(
                name=LocalStr('events.bonfire_spirits.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.bonfire_spirits.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)

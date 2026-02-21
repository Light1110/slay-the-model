"""Event: Dead Adventurer - Act 1 Event (Floor 7+)

A risk/reward event where you search for loot with increasing chance of elite ambush.
Note: Elite fight mechanic simplified - TODO: implement StartEliteFightAction
"""

import random
from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType
from engine.game_state import game_state

@register_event(event_id='dead_adventurer', acts=[1], weight=100)
class DeadAdventurer(Event):
    """Dead Adventurer - search for loot with elite risk."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+."""
        return game_state.current_floor >= 7
    
    def __init__(self):
        super().__init__()
        self.search_count = 0
        self.found_gold = False
        self.found_relic = False
        self.found_nothing = False
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.dead_adventurer.description'
        ))
        
        # Build options
        options = []
        
        # Option to continue searching (max 3 times)
        # Note: Elite fight mechanic simplified - just provides loot
        # todo: 应当有概率碰到精英！
        """
        # Options ⚜️

Numbers in parentheses are for Ascension 15 or higher.

- [Search] Find Loot. 25% (35%) that an Elite will return to fight you.
  - [Search] can yield:
    - 30 Gold.
    - A random Relic.
    - Nothing.
  - Each reward only occurs once - if the player's first search found nothing and the second search found the Relic, the third search will either reward 30 Gold or start a battle.
  - Each subsequent [Search] increases the chance to encounter an Elite by 25%.
  - If the player successfully [Search] three times without encountering an Elite, the event will end with a short dialogue detailing the success.
- [Escape] End the search and resume your journey.
  - There is no penalty for choosing [Escaping] - the player keeps whatever they obtained from [Search] and resume their journey.

The Event has a text at the beginning, describing how the unfortunate adventurer was killed. It gives a hint about which Elite you will fight:

- "...eviscerated and chopped by giant claws.": Lagavulin
  - Unlike its usual Elite battle, Lagavulin doesn't begin Asleep. It instead starts the fight with Siphon Soul.
- "...scoured by flames.": 3 Sentries
- "...gouged and trampled by a horned beast.": Gremlin Nob

Defeating the Elite grants whatever rewards not yet found by [Search], in addition to 25-35 gold.

- Note that the Elite itself doesn't reward an additional Relic if you had already found one from [Search].

Relics that triggers on Elites combat - 🐛 Preserved Insect, 🏹 Sling of Courage, and 🐺 Slaver's Collar - also works on Elite combat of this event. The only exception is ⭐ Black Star, which has no effect whatsoever in this fight.

        """
        if self.search_count < 3:
            # Determine what can be found (in order)
            if not self.found_gold:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[AddGoldAction(amount=30)]
                ))
            elif not self.found_relic:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[AddRandomRelicAction(rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE])]
                ))
            elif not self.found_nothing:
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    actions=[DisplayTextAction(text_key='events.dead_adventurer.nothing')]
                ))
        
        # Leave option
        options.append(Option(
            name=LocalStr('events.dead_adventurer.leave'),
            actions=[]
        ))
        
        actions.append(SelectAction(
            title=LocalStr('events.dead_adventurer.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)

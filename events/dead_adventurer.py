"""Event: Dead Adventurer - Act 1 Event (Floor 7+)

A risk/reward event where you search for loot with increasing chance of elite ambush.
Elite encounter probability: 25% -> 50% -> 75% per search (A15+: 35% -> 60% -> 85%).
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction, AddRelicAction
from actions.combat import StartFightAction
from actions.base import Action, LambdaAction
from localization import LocalStr
from utils.option import Option
from utils.random import get_random_relic
from utils.types import RarityType
from engine.game_state import game_state


@register_event(category='event', event_id='dead_adventurer', acts=[1], weight=100)
class DeadAdventurer(Event):
    """Dead Adventurer - search for loot with elite risk."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ within Act 1."""
        return game_state.floor_in_act >= 7
    
    def __init__(self):
        super().__init__()
        self.search_count = 0
        self.rewards = ["gold", "nothing", "relic"]
        rng = get_rng("misc")
        rng.shuffle(self.rewards)
        self.elite_type = ("sentries", "gremlin_nob", "lagavulin")[rng.randint(0, 2)]
    
    def _get_elite_chance(self) -> int:
        """Get elite encounter chance based on search count."""
        initial_chance = 35 if game_state.ascension >= 15 else 25
        return initial_chance + 25 * self.search_count
    
    def _get_elite_enemies(self) -> list:
        """Build the event encounter using actual classes and position-aware factories."""
        from enemies.act1.gremlin_nob import GremlinNob
        from enemies.act1.lagavulin import Lagavulin
        from map.encounter_pool import _create_sentries

        if self.elite_type == "gremlin_nob":
            return [GremlinNob()]
        if self.elite_type == "lagavulin":
            return [Lagavulin(start_awake=True)]
        if self.elite_type == "sentries":
            return _create_sentries()
        raise ValueError(f"Unknown Dead Adventurer encounter: {self.elite_type}")

    @staticmethod
    def _reward_action(reward: str, source: str = "direct") -> Action:
        if reward == "gold":
            return AddGoldAction(amount=30, source=source)
        if reward == "relic":
            return AddRandomRelicAction(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]
            )
        return DisplayTextAction(text_key="events.dead_adventurer.nothing")

    def _search(self) -> None:
        rng = get_rng("misc")
        if rng.randint(0, 99) < self._get_elite_chance():
            bounds = (0, 30) if game_state.config.daily_run else (25, 35)
            gold = AddGoldAction(amount=rng.randint(*bounds), source="event_combat")
            enemies = self._get_elite_enemies()
            add_actions([
                DisplayTextAction(text_key="events.dead_adventurer.elite_appears"),
                InputRequestAction(
                    title=LocalStr("events.dead_adventurer.title"),
                    options=[Option(
                        name=LocalStr("events.dead_adventurer.fight"),
                        detail=LocalStr("events.dead_adventurer.elite_appears"),
                        actions=[LambdaAction(self._fight, args=[enemies, gold])],
                    )],
                ),
            ], to_front=True)
            return

        reward = self.rewards.pop(0)
        self._count_search()
        add_actions([self._reward_action(reward), LambdaAction(self.trigger)], to_front=True)

    def _count_search(self) -> None:
        self.search_count += 1

    def _fight(self, enemies: list, gold: AddGoldAction) -> None:
        self._count_search()
        victory_rewards: list[Action] = [gold]
        for reward in self.rewards:
            if reward == "gold":
                victory_rewards.append(self._reward_action(reward, source="event_combat"))
            elif reward == "relic":
                victory_rewards.append(AddRelicAction(get_random_relic()))
        victory_rewards.append(LambdaAction(self.end_event))
        add_action(StartFightAction(
            enemies=enemies,
            escape_actions=[LambdaAction(self.end_event)],
            victory_actions=victory_rewards,
        ), to_front=True)

    def trigger(self) -> None:
        options = []
        if self.rewards:
            options.append(Option(
                name=LocalStr("events.dead_adventurer.search"),
                detail=LocalStr("events.dead_adventurer.search_detail", chance=self._get_elite_chance()),
                actions=[LambdaAction(self._search)],
            ))
        options.append(Option(
            name=LocalStr("events.dead_adventurer.leave"),
            detail=LocalStr("events.no_effect"),
            actions=[LambdaAction(self.end_event)],
        ))
        add_actions([
            DisplayTextAction(text_key="events.dead_adventurer.description"),
            InputRequestAction(title=LocalStr("events.dead_adventurer.title"), options=options),
        ])

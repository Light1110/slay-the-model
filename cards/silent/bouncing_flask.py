"""Silent uncommon skill card - Bouncing Flask."""
from typing import List

from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions
from entities.creature import Creature
from powers.definitions.poison import PoisonPower
from utils.combat import living_enemies
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("action")
class BouncingFlaskBounceAction(Action):
    """Resolve one bounce using the target chosen by the preceding step."""

    def __init__(self, target: Creature, poison: int, remaining: int):
        self.target = target
        self.poison = poison
        self.remaining = remaining

    def execute(self) -> None:
        enemies = living_enemies()
        if not enemies:
            return

        actions = []
        # Commit the next target before applying this bounce's poison.
        if self.remaining > 1:
            next_target = get_rng("card_random").choice(enemies)
            actions.append(BouncingFlaskBounceAction(next_target, self.poison, self.remaining - 1))
        if self.target in enemies:
            poison = PoisonPower(amount=self.poison, duration=self.poison, owner=self.target)
            actions.insert(0, ApplyPowerAction(poison, self.target))
        add_actions(actions, to_front=True)


@register("card")
class BouncingFlask(Card):
    """Apply Poison to random enemies multiple times."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_magic = {"hits": 3, "poison": 3}

    upgrade_magic = {"hits": 4, "poison": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        enemies = living_enemies()
        hits = self.get_magic_value("hits")
        if enemies and hits > 0:
            target = get_rng("card_random").choice(enemies)
            add_action(BouncingFlaskBounceAction(target, self.get_magic_value("poison"), hits))

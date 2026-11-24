"""Silent uncommon attack card - All Out Attack."""
from typing import List

from actions.base import Action
from actions.card import DiscardCardAction
from cards.base import Card
from engine.random_streams import get_rng
from engine.runtime_api import add_action
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("action")
class AllOutAttackDiscardAction(Action):
    """Resolve the discard after the attack and its reactions."""

    def execute(self) -> None:
        from engine.game_state import game_state

        player = game_state.player
        combat = game_state.current_combat
        if player is None or player.is_dead() or combat is None or combat.combat_ended:
            return
        if not any(not enemy.is_dead() or enemy.half_dead for enemy in combat.enemies):
            return

        hand = player.card_manager.get_pile("hand")
        if not hand:
            return
        card = hand[0] if len(hand) == 1 else get_rng("card_random").choice(hand)
        DiscardCardAction(card=card, source_pile="hand").execute()


@register("card")
class AllOutAttack(Card):
    """Deal damage to all enemies and discard a random card."""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 10

    upgrade_damage = 14

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        add_action(AllOutAttackDiscardAction())

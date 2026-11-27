"""Silent-specific relics."""
from engine.messages import EnemyDefeatedMessage
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions
from engine.subscriptions import MessagePriority, subscribe

from actions.base import LambdaAction
from actions.card import AddCardAction, DrawCardsAction
from actions.combat import ApplyPowerAction, GainBlockAction, GainEnergyAction
from actions.random_damage import DamageRandomEnemyAction
from cards.colorless.shiv import Shiv
from powers.definitions.poison import PoisonPower
from relics.base import Relic
from utils.combat import living_enemies
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import RarityType, CardType


@register("relic")
class RingOfTheSnake(Relic):
    """At the start of each combat, draw 2 additional cards."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.STARTER

    def on_combat_start(self, floor: int):
        add_actions([DrawCardsAction(count=2)])
        return


@register("relic")
class SneckoSkull(Relic):
    """Whenever you apply Poison, apply an additional 1 Poison."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_apply_power(self, power, target):
        if isinstance(power, PoisonPower):
            applied_poison = target.get_power("Poison")
            if applied_poison is not None:
                applied_poison.amount += 1
        return


@register("relic")
class NinjaScroll(Relic):
    """Start each combat with 3 Shivs in hand."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_combat_start(self, floor: int):
        add_actions([
            AddCardAction(card=Shiv(), dest_pile="hand")
            for _ in range(3)
        ])
        return


@register("relic")
class PaperKrane(Relic):
    """Enemies with Weak deal 50% less damage rather than 25%."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.modify_phase = DamagePhase.MULTIPLICATIVE

    def modify_damage_taken(self, base_damage: int, source=None, damage_type: str = "direct") -> int:
        if source and hasattr(source, "powers"):
            for power in source.powers:
                if getattr(power, "name", "") == "Weak":
                    return int(base_damage * 4 / 5)
        return base_damage


@register("relic")
class TheSpecimen(Relic):
    """Whenever an enemy dies, transfer any Poison it has to a random enemy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    @subscribe(EnemyDefeatedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_enemy_defeated(self, target):
        if not target.is_dead():
            return
        poison = target.get_power("Poison")
        if poison is not None and poison.amount > 0 and living_enemies():
            add_action(LambdaAction(self.transfer_poison, args=(poison.amount,)))

    def transfer_poison(self, amount: int) -> None:
        from engine.game_state import game_state

        enemies = living_enemies()
        if enemies:
            target = get_rng("card_random").choice(enemies)
            add_action(ApplyPowerAction(
                power=PoisonPower(amount=amount, duration=amount),
                target=target,
                source=game_state.player,
            ), to_front=True)


@register("relic")
class Tingsha(Relic):
    """Whenever you discard a card during your turn, deal 3 damage to a random enemy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card):
        from engine.game_state import game_state

        add_action(DamageRandomEnemyAction(3, source=game_state.player))


@register("relic")
class ToughBandages(Relic):
    """Whenever you discard a card during your turn, gain 3 Block."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card):
        from engine.game_state import game_state
        player = game_state.player
        if player is None:
            return
        add_actions([GainBlockAction(block=3, target=player)])
        return


@register("relic")
class HoveringKite(Relic):
    """The first time you discard a card each turn, gain 1 Energy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.discarded_this_turn = False

    def on_combat_start(self, floor: int):
        add_actions([LambdaAction(func=lambda: setattr(self, "discarded_this_turn", False))])
        return

    def on_card_discard(self, card):
        if not self.discarded_this_turn:
            self.discarded_this_turn = True
            add_actions([GainEnergyAction(energy=1)])
        return


@register("relic")
class RingOfTheSerpent(Relic):
    """Replaces Ring of the Snake. Draw 1 additional card each turn."""
    replaces_relic = "RingOfTheSnake"


    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self._draw_bonus_applied = False

    def on_obtain(self):
        from engine.game_state import game_state

        player = getattr(game_state, "player", None)
        if player is None or self._draw_bonus_applied:
            return
        player.base_draw_count += 1
        self._draw_bonus_applied = True

    def on_combat_start(self, floor: int):
        from engine.game_state import game_state

        if self._draw_bonus_applied:
            return
        player = getattr(game_state, "player", None)
        if player is None:
            return
        player.base_draw_count += 1
        self._draw_bonus_applied = True


@register("relic")
class WristBlade(Relic):
    """Attacks that cost 0 Energy deal 4 additional damage."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        if card and getattr(card, "card_type", None) == CardType.ATTACK and getattr(card, "cost", None) == 0:
            return base_damage + 4
        return base_damage


@register("relic")
class TwistedFunnel(Relic):
    """At the start of each combat, apply 4 Poison to all enemies."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_combat_start(self, floor: int):
        add_actions([
            ApplyPowerAction(PoisonPower(amount=4, duration=4, owner=enemy), enemy)
            for enemy in self.combat_enemies()
        ])
        return

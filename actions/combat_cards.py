from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from typing import TYPE_CHECKING, List, Optional

from actions.base import Action
from actions.combat_damage import DealDamageAction, LoseHPAction
from entities.creature import Creature
from localization import LocalStr
from utils.registry import register
from utils.types import DamageType, TargetType

if TYPE_CHECKING:
    from cards.base import Card


def _build_enemy_target_option_name(card: "Card", enemy: Creature) -> LocalStr:
    enemy_name = getattr(enemy, "name", getattr(enemy, "character", "Unknown"))
    if isinstance(enemy_name, LocalStr):
        enemy_name = enemy_name.resolve()

    preview_parts = [f"HP: {enemy.hp}/{enemy.max_hp}"]
    if getattr(enemy, "block", 0) > 0:
        preview_parts.append(f"Block: {enemy.block}")
    preview_text = card.get_combat_description(target=enemy).resolve()

    return LocalStr(
        "combat.select_enemy_option",
        default=f"{enemy_name} ({', '.join(preview_parts)})\n  -> {preview_text}",
    )


@register("action")
class AttackAction(Action):
    """Publish attack hooks before dealing damage."""

    def __init__(self, damage: int, target: Creature, source: Creature, damage_type: str | DamageType = DamageType.PHYSICAL, card=None, *, cancel_on_source_death: bool | None = None):
        self.damage = damage
        self.target = target
        self.damage_type = damage_type
        self.card = card
        self.source = source
        self.cancel_on_source_death = cancel_on_source_death
        self.damage_is_calculated = card is not None and damage_type in (DamageType.PHYSICAL, "attack")
        if self.damage_is_calculated:
            from utils.dynamic_values import resolve_potential_damage
            self.damage = resolve_potential_damage(
                damage, source, target, card=card, damage_type=damage_type,
                for_card_snapshot=True,
            )

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import AttackPerformedMessage

        damage_action = DealDamageAction(
            self.damage,
            target=self.target,
            damage_type=self.damage_type,
            card=self.card,
            source=self.source,
            cancel_on_source_death=getattr(self, "cancel_on_source_death", None),
            damage_is_calculated=getattr(self, "damage_is_calculated", False),
        )
        # DamageAction's guard also precedes attack side effects such as theft.
        # Check again inside the damage action if the source changes meanwhile.
        if damage_action.should_cancel_source():
            return

        publish_message(
            AttackPerformedMessage(
                target=self.target,
                source=self.source,
                card=self.card,
                damage_type=self.damage_type,
            )
        )

        add_action(damage_action, to_front=True)


@register("action")
class RandomCardAttackAction(Action):
    """Select a living target and recalculate the card for this hit only."""

    def __init__(self, card: "Card", source: Creature):
        self.card = card
        self.source = source

    def execute(self) -> None:
        import random
        from engine.game_state import game_state
        from utils.dynamic_values import attack_base_damage

        if self.source.is_dead() or getattr(self.source, "half_dead", False):
            return
        combat = game_state.current_combat
        if combat is None:
            return
        enemies = [enemy for enemy in combat.enemies
                   if enemy.is_alive and not enemy.half_dead]
        if not enemies:
            return
        target = random.choice(enemies)
        add_action(AttackAction(
            attack_base_damage(self.card), target=target,
            source=self.source, card=self.card,
        ), to_front=True)


@register("action")
class PlayCardAction(Action):
    """Resolve targets and prepare a card play."""

    def __init__(self, card: "Card", is_auto: bool = False, ignore_energy: bool = False):
        self.card = card
        self.is_auto = is_auto
        self.ignore_energy = ignore_energy

    def execute(self) -> None:
        from actions.display import InputRequestAction
        from engine.game_state import game_state
        from localization import LocalStr
        from utils.combat import resolve_target
        from utils.option import Option

        if not self.card:
            return

        can_play, reason = self.card.can_play(self.ignore_energy)
        if not can_play:
            print(f"Cannot play card: {reason}")
            return

        if self.card.target_type == TargetType.ENEMY_SELECT and self.is_auto:
            targets = resolve_target(TargetType.ENEMY_RANDOM)
            add_action(
                PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy),
                to_front=True,
            )
            return

        assert self.card.target_type is not None
        # Random card attacks choose per hit; resolving here consumes an extra
        # random choice and incorrectly binds the whole card to one enemy.
        targets = ([] if self.card.target_type == TargetType.ENEMY_RANDOM else
                   [target for target in resolve_target(self.card.target_type) if target is not None])
        if self.card.target_type == TargetType.ENEMY_SELECT and targets:
            options = []
            for enemy in targets:
                options.append(
                    Option(
                        name=_build_enemy_target_option_name(self.card, enemy),
                        actions=[
                            PlayCardBHAction(
                                card=self.card,
                                targets=[enemy],
                                ignore_energy=self.ignore_energy,
                            )
                        ],
                    )
                )
            options.append(
                Option(
                    name=LocalStr("ui.cancel_target_selection", default="Cancel"),
                    actions=[],
                    commands=["cancel", "back"],
                )
            )
            add_action(
                InputRequestAction(
                    title=LocalStr("combat.select_target", default="Select Target"),
                    options=options,
                ),
                to_front=True,
            )
            return
        add_action(
            PlayCardBHAction(card=self.card, targets=targets, ignore_energy=self.ignore_energy),
            to_front=True,
        )


@register("action")
class PlayCardBHAction(Action):
    """Finish playing a card once targets are resolved."""

    def __init__(self, card: "Card", targets: List[Optional[Creature]], ignore_energy: bool = False):
        self.card = card
        self.targets = targets
        self.ignore_energy = ignore_energy

    def execute(self) -> None:
        from actions.card import DiscardCardAction, ExhaustCardAction
        from cards.base import COST_X
        from engine.game_state import game_state
        from engine.messages import CardPlayedMessage
        from localization import t
        from utils.types import CardType

        player = game_state.player
        current_combat = game_state.current_combat
        if player is None or current_combat is None:
            return
        enemies = current_combat.enemies
        resolved_targets = [target for target in self.targets if target is not None]
        message_targets: List[Optional[Creature]] = list(resolved_targets)
        if self.card.target_type == TargetType.ENEMY_RANDOM:
            # Enemy card-play observers still see the play even though its
            # actual attack targets will only be selected by the hit actions.
            message_targets = [enemy for enemy in enemies if enemy.is_alive and not enemy.half_dead]
        current_combat.combat_state.last_card_targets = list(resolved_targets)

        cost = self.card.cost
        if getattr(self.card, "_cost", None) == COST_X:
            cost = player.energy
            setattr(self.card, "_x_cost_energy", cost)
        if cost > 0 and not self.ignore_energy:
            player.gain_energy(-cost)
            current_combat.combat_state.player_energy_spent_this_turn += cost
        self.card.cost_until_played = None

        if len(resolved_targets) == 1:
            target = resolved_targets[0]
            from enemies.base import Enemy
            if isinstance(target, Enemy):
                from engine.back_attack_manager import BackAttackManager
                manager = BackAttackManager()
                manager.maybe_transfer_on_target(target)

        play_actions = self.card.on_play(targets=resolved_targets)
        if play_actions:
            add_actions(play_actions)
        current_combat.combat_state.last_played_card = self.card

        publish_message(
            CardPlayedMessage(
                card=self.card,
                owner=player,
                targets=message_targets,
            )
        )

        current_combat.combat_state.turn_cards_played += 1
        if self.card.card_type == CardType.ATTACK:
            current_combat.combat_state.turn_attack_cards_played += 1
        if self.card.card_type == CardType.POWER:
            current_combat.combat_state.power_cards_played += 1
        current_combat.combat_state.player_actions_this_turn += 1

        card_name = self.card.display_name.resolve() if hasattr(self.card, "display_name") else str(self.card)
        print(t("combat.play_card", card=card_name))

        has_medical_kit = any(getattr(relic, "idstr", None) == "MedicalKit" for relic in player.relics)
        should_exhaust_status = has_medical_kit and self.card.card_type == CardType.STATUS
        has_blue_candle = any(getattr(relic, "idstr", None) == "BlueCandle" for relic in player.relics)
        should_exhaust_curse = has_blue_candle and self.card.card_type == CardType.CURSE
        has_corruption = (
            self.card.card_type == CardType.SKILL
            and player.get_power("Corruption") is not None
        )
        will_exhaust = (
            self.card.get_value("exhaust") is True
            or should_exhaust_status
            or should_exhaust_curse
            or has_corruption
        )

        prevent_exhaust = False
        if will_exhaust:
            for relic in player.relics:
                hook = getattr(relic, "should_prevent_exhaust", None)
                if not hook:
                    continue
                if hook(card=self.card):
                    prevent_exhaust = True
                    break

        is_power_card = self.card.card_type == CardType.POWER

        if will_exhaust and prevent_exhaust:
            add_action(DiscardCardAction(card=self.card, trigger_effects=False))
        elif will_exhaust:
            add_action(ExhaustCardAction(card=self.card))
        else:
            if is_power_card:
                player.card_manager.remove_from_pile(self.card, "hand")
            else:
                add_action(DiscardCardAction(card=self.card, trigger_effects=False))

        if should_exhaust_curse:
            hp_loss = 1
            for relic in player.relics:
                if getattr(relic, "idstr", None) == "BlueCandle":
                    hook = getattr(relic, "curse_play_hp_loss", None)
                    if hook:
                        hp_loss = hook()
                    break
            add_action(LoseHPAction(amount=hp_loss, target=player, source=self.card))



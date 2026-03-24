"""Class-level message subscriber dispatch."""
from __future__ import annotations

from typing import List

from engine.messages import (
    AttackPerformedMessage,
    BlockGainedMessage,
    CardAddedToPileMessage,
    CardExhaustedMessage,
    CardPlayedMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CombatEndedMessage,
    CombatStartedMessage,
    CreatureDiedMessage,
    DamageResolvedMessage,
    EliteVictoryMessage,
    GameMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    RelicObtainedMessage,
    ShuffleMessage,
    ShopEnteredMessage,
)
from engine.message_helpers import alive_entities_from_game_state, as_actions
from engine.subscriptions import iter_bound_subscribers


def invoke_subscription(bound_method, message: GameMessage) -> List:
    if isinstance(message, CombatStartedMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.enemies),
            lambda: bound_method(message.floor),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CombatEndedMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.enemies),
            lambda: bound_method(owner=message.owner, entities=message.enemies),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, PlayerTurnStartedMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.enemies),
            lambda: bound_method(),
            lambda: bound_method(message),
        ]
    elif isinstance(message, PlayerTurnEndedMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.enemies),
            lambda: bound_method(),
            lambda: bound_method(message),
        ]
    elif isinstance(message, RelicObtainedMessage):
        call_patterns = [
            lambda: bound_method(),
            lambda: bound_method(message),
        ]
    elif isinstance(message, GoldGainedMessage):
        call_patterns = [
            lambda: bound_method(message.amount, message.owner),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, ShuffleMessage):
        call_patterns = [
            lambda: bound_method(),
            lambda: bound_method(message),
        ]
    elif isinstance(message, PotionUsedMessage):
        call_patterns = [
            lambda: bound_method(message.potion, message.owner, message.entities),
            lambda: bound_method(message.potion, message.owner),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CardDrawnMessage):
        entities = alive_entities_from_game_state()
        call_patterns = [
            lambda: bound_method(message.card, message.owner, entities),
            lambda: bound_method(message.card),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CardDiscardedMessage):
        entities = alive_entities_from_game_state()
        call_patterns = [
            lambda: bound_method(message.card, message.owner, entities),
            lambda: bound_method(message.card),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CardAddedToPileMessage):
        call_patterns = [
            lambda: bound_method(message.card, message.dest_pile),
            lambda: bound_method(message.card),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CardExhaustedMessage):
        call_patterns = [
            lambda: bound_method(message.card, message.owner, message.source_pile),
            lambda: bound_method(message.card, message.owner),
            lambda: bound_method(message.card),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, CardPlayedMessage):
        call_patterns = [
            lambda: bound_method(message.card, message.owner, message.enemies),
            lambda: bound_method(message.card),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, AttackPerformedMessage):
        call_patterns = [
            lambda: bound_method(message.target, message.source, message.card),
            lambda: bound_method(message.target, message.source),
            lambda: bound_method(message.target),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, PowerAppliedMessage):
        call_patterns = [
            lambda: bound_method(message.power, message.target, message.owner, message.entities or []),
            lambda: bound_method(message.power, message.owner),
            lambda: bound_method(message.power, message.target),
            lambda: bound_method(message.power),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, HealedMessage):
        entities = alive_entities_from_game_state()
        current_hp = getattr(message.target, "hp", None)
        previous_hp = message.previous_hp

        def _call_with_heal_state(attempt):
            if previous_hp is None or current_hp is None:
                return attempt()
            message.target.hp = previous_hp
            try:
                return attempt()
            finally:
                message.target.hp = current_hp

        call_patterns = [
            lambda: _call_with_heal_state(lambda: bound_method(message.amount, message.target, entities)),
            lambda: _call_with_heal_state(lambda: bound_method(message.amount)),
            lambda: _call_with_heal_state(lambda: bound_method(message)),
            lambda: _call_with_heal_state(lambda: bound_method()),
        ]
    elif isinstance(message, HpLostMessage):
        call_patterns = [
            lambda: bound_method(message.amount, message.source, message.card),
            lambda: bound_method(message.amount),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, BlockGainedMessage):
        call_patterns = [
            lambda: bound_method(message.amount, message.target, message.source, message.card),
            lambda: bound_method(message.amount, message.source, message.card),
            lambda: bound_method(message.amount),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, DamageResolvedMessage):
        call_patterns = []
        method_name = getattr(bound_method, "__name__", "")
        from engine.game_state import game_state

        if method_name == "on_damage_taken":
            if getattr(message.target, "powers", None) and any(power is getattr(bound_method, "__self__", None) for power in message.target.powers):
                call_patterns = [
                    lambda: bound_method(message.amount, message.source, message.card, message.target, message.damage_type),
                    lambda: bound_method(message.amount, message.source, message.card, message.damage_type),
                ]
            elif getattr(bound_method, "__self__", None) is message.target:
                call_patterns = [
                    lambda: bound_method(message.amount, message.source, message.card, message.damage_type),
                    lambda: bound_method(message.amount, message.source, message.card),
                ]
            elif message.target is game_state.player:
                entities = alive_entities_from_game_state()
                call_patterns = [
                    lambda: bound_method(message.amount, message.source, game_state.player, entities),
                    lambda: bound_method(message.amount, message.source),
                ]
        elif method_name == "on_damage_dealt":
            entities = alive_entities_from_game_state()
            if getattr(bound_method, "__self__", None) is message.source:
                call_patterns = [
                    lambda: bound_method(message.amount, message.target, message.card, message.damage_type),
                    lambda: bound_method(message.amount, message.target),
                ]
            elif getattr(bound_method, "__self__", None) is message.card:
                call_patterns = [
                    lambda: bound_method(message.amount, message.target, message.card, message.damage_type),
                    lambda: bound_method(message.amount, message.target),
                ]
            elif game_state.player is not None:
                call_patterns = [
                    lambda: bound_method(message.amount, message.target, game_state.player, entities),
                    lambda: bound_method(message.amount, message.target),
                ]
        elif method_name == "on_fatal" and getattr(message.target, "is_dead", lambda: False)():
            call_patterns = [
                lambda: bound_method(message.amount, message.target, message.card, message.damage_type),
                lambda: bound_method(),
                lambda: bound_method(message),
            ]

        if not call_patterns:
            call_patterns = [lambda: bound_method(message), lambda: bound_method()]
    elif isinstance(message, CreatureDiedMessage):
        call_patterns = [
            lambda: bound_method(),
            lambda: bound_method(message),
        ]
    elif isinstance(message, ShopEnteredMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.entities),
            lambda: bound_method(message.owner),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    elif isinstance(message, EliteVictoryMessage):
        call_patterns = [
            lambda: bound_method(message.owner, message.entities),
            lambda: bound_method(message.owner),
            lambda: bound_method(message),
            lambda: bound_method(),
        ]
    else:
        call_patterns = [lambda: bound_method(message), lambda: bound_method()]

    for attempt in call_patterns:
        try:
            return as_actions(attempt())
        except TypeError:
            continue
    return []


def dispatch_class_level_subscribers(message: GameMessage, participants: List | None = None) -> List:
    actions: List = []
    subscriber_calls = []
    for participant_index, participant in enumerate(participants or []):
        for order, name, bound_method, spec in iter_bound_subscribers(participant, message):
            subscriber_calls.append((order, participant_index, name, bound_method, spec))
    subscriber_calls.sort(key=lambda item: (item[0], item[1], item[2]))
    for _order, _participant_index, _name, bound_method, _spec in subscriber_calls:
        result = invoke_subscription(bound_method, message)
        if not result:
            continue
        actions.extend(as_actions(result))
    return actions

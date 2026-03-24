"""Explicit message subscriber contracts."""
from __future__ import annotations

import inspect
from typing import Callable, Iterable, Tuple

from engine.message_helpers import alive_entities_from_game_state
from engine.messages import (
    AttackPerformedMessage,
    BlockGainedMessage,
    CardAddedToPileMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CardPlayedMessage,
    CardExhaustedMessage,
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

ParameterNames = Tuple[str, ...]


def subscription_parameter_names(func: Callable, *, bound: bool) -> ParameterNames:
    """Return declared subscriber parameter names, excluding ``self`` when needed."""
    signature = inspect.signature(func)
    names = []
    for parameter in signature.parameters.values():
        if parameter.kind not in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            raise TypeError("Subscriber signatures may not use *args or **kwargs")
        names.append(parameter.name)
    if not bound and names and names[0] in {"self", "cls"}:
        names = names[1:]
    return tuple(names)


def _generic_contracts() -> dict[type[GameMessage], set[ParameterNames]]:
    return {
        CombatStartedMessage: {
            (),
            ("message",),
            ("floor",),
            ("player", "entities"),
        },
        CombatEndedMessage: {
            (),
            ("message",),
            ("owner", "entities"),
            ("player", "entities"),
        },
        PlayerTurnStartedMessage: {
            (),
            ("message",),
            ("player", "entities"),
        },
        PlayerTurnEndedMessage: {
            (),
            ("message",),
            ("player", "entities"),
        },
        RelicObtainedMessage: {
            (),
            ("message",),
        },
        GoldGainedMessage: {
            (),
            ("message",),
            ("gold_amount", "player"),
        },
        ShuffleMessage: {
            (),
            ("message",),
        },
        PotionUsedMessage: {
            (),
            ("message",),
            ("potion", "player"),
            ("potion", "player", "entities"),
        },
        CardDrawnMessage: {
            (),
            ("message",),
            ("card",),
            ("card", "player", "entities"),
        },
        CardDiscardedMessage: {
            (),
            ("message",),
            ("card",),
            ("card", "player", "entities"),
        },
        CardAddedToPileMessage: {
            (),
            ("message",),
            ("card",),
            ("card", "dest_pile"),
        },
        CardExhaustedMessage: {
            (),
            ("message",),
            ("card",),
            ("card", "owner"),
            ("card", "owner", "source_pile"),
        },
        CardPlayedMessage: {
            (),
            ("message",),
            ("card",),
            ("card", "player", "entities"),
        },
        AttackPerformedMessage: {
            (),
            ("message",),
            ("target",),
            ("target", "source"),
            ("target", "source", "card"),
        },
        PowerAppliedMessage: {
            (),
            ("message",),
            ("power",),
            ("power", "owner"),
            ("power", "source"),
            ("power", "target"),
            ("power", "target", "player", "entities"),
        },
        HealedMessage: {
            (),
            ("message",),
            ("amount",),
            ("amount", "player", "entities"),
            ("heal_amount", "player", "entities"),
        },
        HpLostMessage: {
            (),
            ("message",),
            ("amount",),
            ("amount", "source", "card"),
        },
        BlockGainedMessage: {
            (),
            ("message",),
            ("amount",),
            ("amount", "source", "card"),
            ("amount", "player", "source", "card"),
        },
        CreatureDiedMessage: {
            (),
            ("message",),
        },
        ShopEnteredMessage: {
            (),
            ("message",),
            ("owner",),
            ("player",),
            ("player", "entities"),
        },
        EliteVictoryMessage: {
            (),
            ("message",),
            ("owner",),
            ("player",),
            ("player", "entities"),
        },
    }


_GENERIC_CONTRACTS = _generic_contracts()

_METHOD_CONTRACTS: dict[type[GameMessage], dict[str, set[ParameterNames]]] = {
    DamageResolvedMessage: {
        "on_damage_taken": {
            ("damage", "source", "card", "damage_type"),
            ("damage", "source", "card", "player", "damage_type"),
            ("damage", "source", "player", "entities"),
        },
        "on_damage_dealt": {
            ("damage", "target"),
            ("damage", "target", "card", "damage_type"),
            ("damage", "target", "source", "card"),
            ("damage", "target", "player", "entities"),
        },
        "on_fatal": {
            (),
            ("message",),
            ("damage", "target", "card", "damage_type"),
        },
    }
}


def validate_subscription(
    message_type: type[GameMessage],
    param_names: Iterable[str],
    method_name: str | None = None,
) -> bool:
    names = tuple(param_names)
    method_contracts = _METHOD_CONTRACTS.get(message_type, {})
    if method_name:
        return names in method_contracts.get(method_name, set()) or names in _GENERIC_CONTRACTS.get(message_type, set())
    if names in _GENERIC_CONTRACTS.get(message_type, set()):
        return True
    return any(names in contract_names for contract_names in method_contracts.values())


def _invoke(bound_method: Callable, *args):
    return bound_method(*args)


def invoke_subscription_contract(bound_method: Callable, message: GameMessage):
    """Invoke a subscriber using its explicit message contract."""
    method_name = getattr(bound_method, "__name__", "")
    param_names = subscription_parameter_names(bound_method, bound=True)
    if not validate_subscription(type(message), param_names, method_name=method_name):
        return None

    if isinstance(message, CombatStartedMessage):
        if param_names == ("player", "entities"):
            return _invoke(bound_method, message.owner, message.enemies)
        if param_names == ("floor",):
            return _invoke(bound_method, message.floor)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CombatEndedMessage):
        if param_names in {("player", "entities"), ("owner", "entities")}:
            return _invoke(bound_method, message.owner, message.enemies)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, PlayerTurnStartedMessage):
        if param_names == ("player", "entities"):
            return _invoke(bound_method, message.owner, message.enemies)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, PlayerTurnEndedMessage):
        if param_names == ("player", "entities"):
            return _invoke(bound_method, message.owner, message.enemies)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, RelicObtainedMessage):
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, GoldGainedMessage):
        if param_names == ("gold_amount", "player"):
            return _invoke(bound_method, message.amount, message.owner)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, ShuffleMessage):
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, PotionUsedMessage):
        if param_names == ("potion", "player", "entities"):
            return _invoke(bound_method, message.potion, message.owner, message.entities)
        if param_names == ("potion", "player"):
            return _invoke(bound_method, message.potion, message.owner)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CardDrawnMessage):
        entities = alive_entities_from_game_state()
        if param_names == ("card", "player", "entities"):
            return _invoke(bound_method, message.card, message.owner, entities)
        if param_names == ("card",):
            return _invoke(bound_method, message.card)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CardDiscardedMessage):
        entities = alive_entities_from_game_state()
        if param_names == ("card", "player", "entities"):
            return _invoke(bound_method, message.card, message.owner, entities)
        if param_names == ("card",):
            return _invoke(bound_method, message.card)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CardAddedToPileMessage):
        if param_names == ("card", "dest_pile"):
            return _invoke(bound_method, message.card, message.dest_pile)
        if param_names == ("card",):
            return _invoke(bound_method, message.card)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CardExhaustedMessage):
        if param_names == ("card", "owner", "source_pile"):
            return _invoke(bound_method, message.card, message.owner, message.source_pile)
        if param_names == ("card", "owner"):
            return _invoke(bound_method, message.card, message.owner)
        if param_names == ("card",):
            return _invoke(bound_method, message.card)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, CardPlayedMessage):
        if param_names == ("card", "player", "entities"):
            return _invoke(bound_method, message.card, message.owner, message.enemies)
        if param_names == ("card",):
            return _invoke(bound_method, message.card)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, AttackPerformedMessage):
        if param_names == ("target", "source", "card"):
            return _invoke(bound_method, message.target, message.source, message.card)
        if param_names == ("target", "source"):
            return _invoke(bound_method, message.target, message.source)
        if param_names == ("target",):
            return _invoke(bound_method, message.target)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, PowerAppliedMessage):
        if param_names == ("power", "target", "player", "entities"):
            return _invoke(bound_method, message.power, message.target, message.owner, message.entities or [])
        if param_names == ("power", "owner"):
            return _invoke(bound_method, message.power, message.owner)
        if param_names == ("power", "source"):
            return _invoke(bound_method, message.power, message.owner)
        if param_names == ("power", "target"):
            return _invoke(bound_method, message.power, message.target)
        if param_names == ("power",):
            return _invoke(bound_method, message.power)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, HealedMessage):
        entities = alive_entities_from_game_state()
        current_hp = getattr(message.target, "hp", None)
        previous_hp = message.previous_hp

        def call_with_previous_hp(*args):
            if previous_hp is None or current_hp is None:
                return _invoke(bound_method, *args)
            message.target.hp = previous_hp
            try:
                return _invoke(bound_method, *args)
            finally:
                message.target.hp = current_hp

        if param_names == ("heal_amount", "player", "entities"):
            return call_with_previous_hp(message.amount, message.target, entities)
        if param_names == ("amount", "player", "entities"):
            return call_with_previous_hp(message.amount, message.target, entities)
        if param_names == ("amount",):
            return call_with_previous_hp(message.amount)
        if param_names == ("message",):
            return call_with_previous_hp(message)
        if param_names == ():
            return call_with_previous_hp()
    elif isinstance(message, HpLostMessage):
        if param_names == ("amount", "source", "card"):
            return _invoke(bound_method, message.amount, message.source, message.card)
        if param_names == ("amount",):
            return _invoke(bound_method, message.amount)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, BlockGainedMessage):
        if param_names == ("amount", "player", "source", "card"):
            return _invoke(bound_method, message.amount, message.target, message.source, message.card)
        if param_names == ("amount", "source", "card"):
            return _invoke(bound_method, message.amount, message.source, message.card)
        if param_names == ("amount",):
            return _invoke(bound_method, message.amount)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, DamageResolvedMessage):
        from engine.game_state import game_state

        subscriber = getattr(bound_method, "__self__", None)
        entities = alive_entities_from_game_state()

        if method_name == "on_damage_taken":
            if (
                param_names == ("damage", "source", "card", "player", "damage_type")
                and getattr(message.target, "powers", None)
                and any(power is subscriber for power in message.target.powers)
            ):
                return _invoke(
                    bound_method,
                    message.amount,
                    message.source,
                    message.card,
                    message.target,
                    message.damage_type,
                )
            if (
                param_names == ("damage", "source", "card", "damage_type")
                and subscriber is message.target
            ):
                return _invoke(
                    bound_method,
                    message.amount,
                    message.source,
                    message.card,
                    message.damage_type,
                )
            if param_names == ("damage", "source", "player", "entities") and game_state.player is not None:
                return _invoke(
                    bound_method,
                    message.amount,
                    message.source,
                    game_state.player,
                    entities,
                )
        elif method_name == "on_damage_dealt":
            if param_names == ("damage", "target", "source", "card"):
                return _invoke(
                    bound_method,
                    message.amount,
                    message.target,
                    message.source,
                    message.card,
                )
            if (
                param_names == ("damage", "target", "card", "damage_type")
                and subscriber in {message.source, message.card}
            ):
                return _invoke(
                    bound_method,
                    message.amount,
                    message.target,
                    message.card,
                    message.damage_type,
                )
            if param_names == ("damage", "target") and subscriber in {message.source, message.card}:
                return _invoke(bound_method, message.amount, message.target)
            if param_names == ("damage", "target", "player", "entities") and game_state.player is not None:
                return _invoke(
                    bound_method,
                    message.amount,
                    message.target,
                    game_state.player,
                    entities,
                )
        elif method_name == "on_fatal":
            if not getattr(message.target, "is_dead", lambda: False)():
                return None
            if param_names == ("damage", "target", "card", "damage_type"):
                return _invoke(
                    bound_method,
                    message.amount,
                    message.target,
                    message.card,
                    message.damage_type,
                )
            if param_names == ("message",):
                return _invoke(bound_method, message)
            if param_names == ():
                return _invoke(bound_method)
    elif isinstance(message, CreatureDiedMessage):
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, ShopEnteredMessage):
        if param_names in {("player", "entities"), ("owner", "entities")}:
            return _invoke(bound_method, message.owner, message.entities)
        if param_names in {("player",), ("owner",)}:
            return _invoke(bound_method, message.owner)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    elif isinstance(message, EliteVictoryMessage):
        if param_names in {("player", "entities"), ("owner", "entities")}:
            return _invoke(bound_method, message.owner, message.entities)
        if param_names in {("player",), ("owner",)}:
            return _invoke(bound_method, message.owner)
        if param_names == ("message",):
            return _invoke(bound_method, message)
        if param_names == ():
            return _invoke(bound_method)
    return None


"""Class-level message subscriptions with semantic priorities."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Iterable, List, Optional, Type


class MessagePriority(Enum):
    SYSTEM = auto()
    PLAYER_RELIC = auto()
    PLAYER_POWER = auto()
    REACTION = auto()
    ENEMY = auto()
    ENEMY_POWER = auto()
    CARD = auto()


_PRIORITY_ORDER = {
    MessagePriority.SYSTEM: 100,
    MessagePriority.PLAYER_RELIC: 200,
    MessagePriority.PLAYER_POWER: 300,
    MessagePriority.REACTION: 400,
    MessagePriority.ENEMY: 500,
    MessagePriority.ENEMY_POWER: 600,
    MessagePriority.CARD: 700,
}


@dataclass(frozen=True)
class SubscriptionSpec:
    message_type: Type[Any]
    priority: MessagePriority


def subscribe(message_type: Type[Any], priority: MessagePriority = MessagePriority.SYSTEM):
    """Mark a method as a subscriber for a message type."""

    def decorator(func: Callable):
        specs = list(getattr(func, "__message_subscriptions__", []))
        specs.append(SubscriptionSpec(message_type=message_type, priority=priority))
        setattr(func, "__message_subscriptions__", specs)
        return func

    return decorator


def iter_bound_subscribers(participant: Any, message: Any) -> Iterable[tuple[int, str, Callable, SubscriptionSpec]]:
    """Yield bound subscriber methods, inheriting metadata from decorated base methods."""
    seen_names: set[str] = set()
    for cls in participant.__class__.mro():
        for name, value in cls.__dict__.items():
            specs: List[SubscriptionSpec] = getattr(value, "__message_subscriptions__", [])
            if not specs:
                continue
            if name in seen_names:
                continue
            seen_names.add(name)
            bound_method = getattr(participant, name)
            for spec in specs:
                if isinstance(message, spec.message_type):
                    yield (_PRIORITY_ORDER[spec.priority], name, bound_method, spec)

"""Class-level message subscriber dispatch."""
from __future__ import annotations

from typing import List

from engine.message_contracts import invoke_subscription_contract
from engine.message_helpers import as_actions
from engine.messages import GameMessage
from engine.subscriptions import iter_bound_subscribers


def invoke_subscription(bound_method, message: GameMessage, method_name: str | None = None) -> List:
    result = invoke_subscription_contract(bound_method, message, method_name=method_name)
    if result is None:
        return []
    return as_actions(result)


_OWNER_SCOPED_TURN_HOOKS = {"on_turn_start", "on_turn_end"}
_PLAYER_TURN_MESSAGES = {"PlayerTurnStartedMessage", "PlayerTurnEndedMessage"}


def _owner_turn_hook_applies(participant, message: GameMessage, method_name: str) -> bool:
    """Player turn hooks run only for powers owned by that turn's owner."""
    if method_name not in _OWNER_SCOPED_TURN_HOOKS:
        return True
    if type(message).__name__ not in _PLAYER_TURN_MESSAGES:
        return True
    owner = getattr(participant, "owner", None)
    if owner is None:
        return True
    return owner is getattr(message, "owner", None)


def dispatch_class_level_subscribers(message: GameMessage, participants: List | None = None) -> List:
    actions: List = []
    subscriber_calls = []
    for participant_index, participant in enumerate(participants or []):
        for order, name, bound_method, spec in iter_bound_subscribers(participant, message):
            if not _owner_turn_hook_applies(participant, message, name):
                continue
            subscriber_calls.append((order, participant_index, name, bound_method, spec))
    subscriber_calls.sort(key=lambda item: (item[0], item[1], item[2]))
    for _order, _participant_index, name, bound_method, _spec in subscriber_calls:
        result = invoke_subscription(bound_method, message, method_name=name)
        if not result:
            continue
        actions.extend(as_actions(result))
    return actions

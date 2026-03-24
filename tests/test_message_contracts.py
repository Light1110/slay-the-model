import pytest

from engine.message_contracts import get_message_contract, validate_subscription
from engine.messages import (
    EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES,
    CardDrawnMessage,
    CombatStartedMessage,
)
from engine.subscriptions import subscribe


def test_invalid_subscription_signature_raises():
    with pytest.raises(TypeError):
        @subscribe(CardDrawnMessage)
        def bad_handler(self, a, b, c, d):
            return []


def test_card_drawn_contract_accepts_message_form():
    assert validate_subscription(CardDrawnMessage, ["message"]) is True


def test_combat_started_contract_accepts_floor_form():
    assert validate_subscription(CombatStartedMessage, ["floor"]) is True


def test_contract_registry_exposes_declared_variants():
    contract = get_message_contract(CardDrawnMessage)

    assert contract.message_type is CardDrawnMessage
    assert ("message",) in {variant.param_names for variant in contract.default_variants}
    assert ("card", "player", "entities") in {variant.param_names for variant in contract.default_variants}


def test_messages_export_explicit_subscription_scope():
    assert CardDrawnMessage in EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES
    assert CombatStartedMessage in EXPLICIT_SUBSCRIPTION_MESSAGE_TYPES

import pytest

from engine.message_contracts import validate_subscription
from engine.messages import CardDrawnMessage, CombatStartedMessage
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

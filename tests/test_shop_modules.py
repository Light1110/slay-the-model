"""Tests for extracted shop helper modules."""

from actions.misc import LeaveRoomAction

from rooms.shop_menu import build_shop_menu
from rooms.shop_pricing import compute_card_removal_price, compute_shop_price
from rooms.shop_state import ShopItem


class _DummyCard:
    def info(self):
        return "Dummy Strike"


def test_shop_pricing_applies_membership_discount():
    price = compute_shop_price(base_price=100, has_membership_card=True)
    assert price == 50


def test_card_removal_price_uses_smiling_mask_override():
    price = compute_card_removal_price(
        base_price=75,
        has_membership_card=True,
        has_smiling_mask=True,
    )
    assert price == 50


def test_shop_menu_builds_leave_option():
    menu = build_shop_menu(
        title="shop-title",
        localize=lambda key, **kwargs: key,
        items=[ShopItem("card", _DummyCard(), 100)],
        player_gold=200,
        ascension_level=0,
        card_removal_price=75,
        card_removal_used=False,
        has_smiling_mask=False,
        has_membership_card=False,
        has_the_courier=False,
        room=object(),
    )

    assert any(isinstance(option.actions[0], LeaveRoomAction) for option in menu.options)

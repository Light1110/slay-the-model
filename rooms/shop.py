"""
Shop room implementation.
"""
import random
from actions.base import Action, action_queue
from actions.card import AddCardAction
from actions.display import SelectAction
from actions.reward import AddGoldAction, AddRelicAction, AddRandomPotionAction
from actions.shop import BuyItemAction, CardRemovalAction, LeaveShopAction, _has_relic, _get_final_price
from engine.game_state import game_state
from localization import LocalStr, t
from rooms.base import Room
from utils.option import Option
from utils.random import get_random_card, get_random_relic, get_random_potion
from utils.registry import register
from utils.types import RarityType, CardType


class ShopItem:
    """Represents an item for sale in the shop"""

    def __init__(self, item_type, item, base_price, discount=0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False

    def get_final_price(self, ascension_level=0):
        """Calculate final price considering ascension and discounts"""
        price = self.base_price
        if ascension_level >= 16:
            price = int(price * 1.1)
        if self.discount > 0:
            price = int(price * (1 - self.discount))
        return price




@register("room")
class ShopRoom(Room):
    """Shop room where player can buy cards, relics, potions, and card removal"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.localization_prefix = "rooms"
        self.items = []
        self.card_removal_price = 75
        self.card_removal_used = False

    def enter_room(self):
        """Enter shop room"""
        super().enter_room()

        self.items = []
        character = game_state.player.character if game_state.player else "ironclad"
        ascension = game_state.ascension_level if game_state else 0

        # Generate 5 colored cards (2 attacks, 2 skills, 1 power)
        for _ in range(2):
            card = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[CardType.ATTACK],
                characters=[character]
            )
            base = 50 if card.rarity == RarityType.COMMON else 75 if card.rarity == RarityType.UNCOMMON else 150
            variance = int(base * 0.1)
            self.items.append(ShopItem("card", card, base - variance + random.randint(0, variance * 2)))

        for _ in range(2):
            card = get_random_card(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
                card_types=[CardType.SKILL],
                characters=[character]
            )
            base = 50 if card.rarity == RarityType.COMMON else 75 if card.rarity == RarityType.UNCOMMON else 150
            variance = int(base * 0.1)
            self.items.append(ShopItem("card", card, base - variance + random.randint(0, variance * 2)))

        card = get_random_card(
            rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            card_types=[CardType.POWER],
            characters=[character]
        )
        base = 50 if card.rarity == RarityType.COMMON else 75 if card.rarity == RarityType.UNCOMMON else 150
        variance = int(base * 0.1)
        self.items.append(ShopItem("card", card, base - variance + random.randint(0, variance * 2)))

        # Apply 50% discount to one random card
        if self.items:
            random.choice(self.items[:5]).discount = 0.5

        # Generate 2 colorless cards (1 uncommon, 1 rare)
        card = get_random_card(rarities=[RarityType.UNCOMMON], card_types=[], colors=["colorless"])
        base = 75
        variance = int(base * 0.1)
        self.items.append(ShopItem("card", card, int(base * 1.2) - variance + random.randint(0, variance * 2)))

        card = get_random_card(rarities=[RarityType.RARE], card_types=[], colors=["colorless"])
        base = 150
        variance = int(base * 0.1)
        self.items.append(ShopItem("card", card, int(base * 1.2) - variance + random.randint(0, variance * 2)))

        # Generate 3 potions
        for _ in range(3):
            rarity_roll = random.random()
            rarity = RarityType.COMMON if rarity_roll < 0.65 else RarityType.UNCOMMON if rarity_roll < 0.90 else RarityType.RARE
            base = 50 if rarity == RarityType.COMMON else 75 if rarity == RarityType.UNCOMMON else 100
            variance = int(base * 0.05)
            potion = get_random_potion(rarities=[rarity])
            self.items.append(ShopItem("potion", potion, base - variance + random.randint(0, variance * 2)))

        # Generate 3 relics (rightmost is always a shop relic)
        for _ in range(2):
            rarity_roll = random.random()
            rarity = RarityType.COMMON if rarity_roll < 0.50 else RarityType.UNCOMMON if rarity_roll < 0.83 else RarityType.RARE
            base = 150 if rarity == RarityType.COMMON else 250 if rarity == RarityType.UNCOMMON else 300
            variance = int(base * 0.05)
            relic = get_random_relic(rarities=[rarity])
            self.items.append(ShopItem("relic", relic, base - variance + random.randint(0, variance * 2)))

        shop_relic = get_random_relic(rarities=[RarityType.SHOP])
        base = 150
        variance = int(base * 0.05)
        self.items.append(ShopItem("relic", shop_relic, base - variance + random.randint(0, variance * 2)))

        # Create options
        options = []

        # Card removal service
        if not self.card_removal_used:
            price = self.card_removal_price
            if _has_relic("SmilingMask"):
                price = 50
            elif _has_relic("MembershipCard"):
                price = int(price * 0.5)
            options.append(Option(
                name=self.local("ShopRoom.remove_card", price=price),
                actions=[CardRemovalAction(self)]
            ))

        # Purchase options for each item
        for idx, shop_item in enumerate(self.items):
            if not shop_item.purchased:
                final_price = _get_final_price(shop_item, ascension)
                if shop_item.item_type == "card":
                    name = self.local("ShopRoom.buy_card", card=shop_item.item.name, price=final_price)
                elif shop_item.item_type == "relic":
                    name = self.local("ShopRoom.buy_relic", relic=shop_item.item.name, price=final_price)
                elif shop_item.item_type == "potion":
                    name = self.local("ShopRoom.buy_potion", potion=shop_item.item.name, price=final_price)
                else:
                    name = f"Buy for {final_price}"
                options.append(Option(name=name, actions=[BuyItemAction(shop_item, idx)]))

        # Leave option
        options.append(Option(
            name=self.local("ShopRoom.leave"),
            actions=[LeaveShopAction()]
        ))

        action_queue.add_action(SelectAction(
            title=self.local("ShopRoom.title"),
            options=options
        ))

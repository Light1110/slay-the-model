"""Shop inventory state helpers."""
import random

from utils.random import get_random_card, get_random_potion, get_random_relic
from utils.types import CardType, RarityType

from rooms.shop_pricing import compute_shop_price


class ShopItem:
    """Represents an item for sale in the shop."""

    def __init__(self, item_type, item, base_price, discount=0):
        self.item_type = item_type
        self.item = item
        self.base_price = base_price
        self.discount = discount
        self.purchased = False

    def get_final_price(self, ascension_level=0):
        """Calculate the final price using only local item state."""
        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            item_type=self.item_type,
        )

    def get_final_price_with_modifiers(
        self,
        ascension_level=0,
        game_state=None,
        has_membership_card=None,
        has_the_courier=None,
        has_smiling_mask=None,
    ):
        """Calculate the final price including relic-based modifiers."""
        if game_state is not None:
            has_membership_card = game_state_has_relic("MembershipCard", game_state)
            has_the_courier = game_state_has_relic("TheCourier", game_state)
            has_smiling_mask = game_state_has_relic("SmilingMask", game_state)

        return compute_shop_price(
            base_price=self.base_price,
            ascension_level=ascension_level,
            discount=self.discount,
            has_membership_card=bool(has_membership_card),
            has_the_courier=bool(has_the_courier),
            has_smiling_mask=bool(has_smiling_mask),
            item_type=self.item_type,
        )



def normalize_relic_key(value):
    return str(value).strip().lower().replace(" ", "").replace("_", "").replace("-", "")



def game_state_has_relic(relic_key, game_state=None):
    """Check whether the current player has a relic by id or name."""
    if not game_state or not getattr(game_state, "player", None):
        return False

    target = normalize_relic_key(relic_key)
    for relic in getattr(game_state.player, "relics", []):
        relic_id = getattr(relic, "idstr", None)
        if relic_id and normalize_relic_key(relic_id) == target:
            return True
        relic_name = getattr(relic, "name", None)
        if relic_name and normalize_relic_key(relic_name) == target:
            return True
    return False



def build_card_namespaces(player):
    """Return the card namespace restriction for the current player."""
    if not player:
        return ["ironclad"]

    namespace = getattr(player, "namespace", None) or "ironclad"
    if any(getattr(relic, "idstr", None) == "PrismaticShard" for relic in getattr(player, "relics", [])):
        return None
    return [namespace]



def generate_colored_cards(player, card_provider=get_random_card):
    """Generate 5 colored cards for the shop."""
    card_namespaces = build_card_namespaces(player)
    cards = []

    for _ in range(2):
        card = card_provider(
            rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            card_types=[CardType.ATTACK],
            namespaces=card_namespaces,
        )
        if card:
            cards.append(card)

    for _ in range(2):
        card = card_provider(
            rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
            card_types=[CardType.SKILL],
            namespaces=card_namespaces,
        )
        if card:
            cards.append(card)

    card = card_provider(
        rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE],
        card_types=[CardType.POWER],
        namespaces=card_namespaces,
    )
    if card:
        cards.append(card)

    return cards



def generate_colorless_cards(card_provider=get_random_card):
    """Generate 2 colorless cards for the shop."""
    cards = []

    uncommon_card = card_provider(
        rarities=[RarityType.UNCOMMON],
        card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
        namespaces=["colorless"],
    )
    if uncommon_card:
        cards.append(uncommon_card)

    rare_card = card_provider(
        rarities=[RarityType.RARE],
        card_types=[CardType.SKILL, CardType.ATTACK, CardType.POWER],
        namespaces=["colorless"],
    )
    if rare_card:
        cards.append(rare_card)

    return cards



def generate_shop_items(
    player=None,
    rng=None,
    card_provider=get_random_card,
    potion_provider=get_random_potion,
    relic_provider=get_random_relic,
):
    """Generate the current shop inventory."""
    rng = rng or random
    items = []
    namespace = getattr(player, "namespace", None) or "ironclad"

    colored_cards = generate_colored_cards(player=player, card_provider=card_provider)
    colored_start_idx = len(items)
    for card in colored_cards:
        if card is None:
            raise ValueError("unable to get card")

        if card.rarity == RarityType.COMMON:
            price = rng.randint(45, 55)
        elif card.rarity == RarityType.UNCOMMON:
            price = rng.randint(68, 83)
        else:
            price = rng.randint(135, 165)
        items.append(ShopItem("card", card, price))

    colored_end_idx = len(items)
    if colored_end_idx > colored_start_idx:
        discounted_index = rng.randint(colored_start_idx, colored_end_idx - 1)
        items[discounted_index].discount = 0.5

    for card in generate_colorless_cards(card_provider=card_provider):
        if card is None:
            continue

        if card.rarity == RarityType.UNCOMMON:
            price = rng.randint(81, 99)
        elif card.rarity == RarityType.RARE:
            price = rng.randint(162, 198)
        else:
            price = rng.randint(81, 99)
        items.append(ShopItem("card", card, price))

    for _ in range(3):
        rarity_roll = rng.random()
        rarity = (
            RarityType.COMMON
            if rarity_roll < 0.65
            else RarityType.UNCOMMON if rarity_roll < 0.90 else RarityType.RARE
        )
        potion = potion_provider(characters=[namespace], rarities=[rarity])
        if rarity == RarityType.COMMON:
            price = rng.randint(48, 53)
        elif rarity == RarityType.UNCOMMON:
            price = rng.randint(71, 79)
        else:
            price = rng.randint(95, 105)
        items.append(ShopItem("potion", potion, price))

    for _ in range(2):
        rarity_roll = rng.random()
        rarity = (
            RarityType.COMMON
            if rarity_roll < 0.50
            else RarityType.UNCOMMON if rarity_roll < 0.83 else RarityType.RARE
        )
        relic = relic_provider(rarities=[rarity])
        if rarity == RarityType.COMMON:
            price = rng.randint(143, 158)
        elif rarity == RarityType.UNCOMMON:
            price = rng.randint(238, 263)
        else:
            price = rng.randint(285, 315)
        items.append(ShopItem("relic", relic, price))

    shop_relic = relic_provider(rarities=[RarityType.SHOP])
    items.append(ShopItem("relic", shop_relic, rng.randint(143, 158)))
    return items

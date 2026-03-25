from actions.base import Action
from typing import List, Optional, TYPE_CHECKING
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card, get_random_card_reward
from utils.result_types import BaseResult, MultipleActionsResult, NoneResult, SingleActionResult

if TYPE_CHECKING:
    from cards.base import Card

from actions.card_lifecycle import AddCardAction, RemoveCardAction

@register("action")
class TransformCardAction(Action):
    """Choose a card to transform from pile
    
    Required:
        card (Card): Card to remove
        pile (str): Card location
        
    Optional:
        reason (str): Transform reason (for UI / logging)
    """
    def __init__(self, card, pile: str, reason: Optional[str] = None):
        self.card = card
        self.pile = pile
        self.reason = reason
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        # 相当于删掉原卡，随机获得一张新卡
        if not game_state.player:
            return NoneResult()

        namespace = self.card.namespace

        # Return actions to be added to caller's action_queue
        return MultipleActionsResult([
            RemoveCardAction(card=self.card, src_pile=self.pile),
            AddCardAction(card=get_random_card(namespaces=[namespace]), dest_pile=self.pile),
        ])

@register("action")
class RemoveAllStrikesAction(Action):
    """Remove all Strike cards from player's deck.

    Required:
        None

    Optional:
        None
    """
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from cards.ironclad.strike import Strike

        if not game_state.player:
            return NoneResult()

        removed_count = 0
        # Check all piles
        piles = ['draw_pile', 'hand', 'discard_pile', 'exhaust_pile']

        for pile_name in piles:
            if not hasattr(game_state.player, 'card_manager'):
                continue
            pile = getattr(game_state.player.card_manager, pile_name, None)
            if not pile:
                continue

            # Find all Strike cards in this pile
            strikes = [card for card in pile if isinstance(card, Strike)]
            for strike in strikes:
                game_state.player.card_manager.remove_from_pile(strike, pile_name)
                removed_count += 1

        print(f"[Event] Removed {removed_count} Strike card(s)")
        return NoneResult()

@register("action")
class RemoveRandomCardAction(Action):
    """Remove a random card of a specific type from player's deck.

    Required:
        card_type (CardType): Type of card to remove (SKILL, POWER, ATTACK)

    Optional:
        None
    """
    def __init__(self, card_type):
        self.card_type = card_type

    def execute(self) -> 'BaseResult':
        import random
        from engine.game_state import game_state
        from utils.types import CardType

        if not game_state.player or not hasattr(game_state.player, 'card_manager'):
            return NoneResult()

        # Get all cards from all piles
        all_cards = []
        card_manager = game_state.player.card_manager

        # Map card_type string to actual CardType enum if needed
        target_type = self.card_type
        if isinstance(target_type, str):
            type_map = {
                'skill': CardType.SKILL,
                'power': CardType.POWER,
                'attack': CardType.ATTACK
            }
            target_type = type_map.get(target_type.lower())

        # Check each pile for matching cards
        piles = ['draw_pile', 'hand', 'discard_pile', 'exhaust_pile']
        for pile_name in piles:
            pile = getattr(card_manager, pile_name, [])
            for card in pile:
                if hasattr(card, 'card_type') and card.card_type == target_type:
                    all_cards.append((card, pile_name))

        if not all_cards:
            print(f"[Event] No {self.card_type} cards found to remove")
            return NoneResult()

        # Remove a random card
        card_to_remove, pile_name = random.choice(all_cards)
        card_manager.remove_from_pile(card_to_remove, pile_name)
        print(f"[Event] Removed {card_to_remove.name} ({self.card_type})")

        return NoneResult()

@register("action")
class UpgradeCardAction(Action):
    """Upgrade a specific card.
    
    Required:
        card (Card): Card to upgrade
        
    Optional:
        None
    """
    def __init__(self, card):
        self.card = card
    
    def execute(self) -> 'BaseResult':
        if self.card and self.card.can_upgrade():
            self.card.upgrade()
            return NoneResult()
        return NoneResult()

@register("action")   
class AddRandomCardAction(Action):
    """Obtain a random card

    Required:
        pile (str): Card location ('deck' or 'hand')
        upgrade (bool)
        namespace (str): Card namespace
        card_type (CardType): Card type
        rarity (str): Card rarity
        permanent_cost (int)
        temp_cost (int)

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', upgrade: bool = False,
                 card_type: Optional[CardType] = None, rarity: Optional[RarityType] = None, namespace: Optional[str] = None,
                 permanent_cost: Optional[int] = None, temp_cost: Optional[int] = None):
        self.pile = pile
        self.upgrade = upgrade
        self.card_type = card_type
        self.rarity = rarity
        self.namespace = namespace
        self.permanent_cost = permanent_cost
        self.temp_cost = temp_cost
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        random_card = get_random_card(
            namespaces=[self.namespace if self.namespace else game_state.player.character.lower()],
            card_types=[self.card_type] if self.card_type else None,
            rarities=[self.rarity] if self.rarity else None
        )

        if random_card is None:
            return NoneResult()
        
        if self.upgrade:
            random_card.upgrade()
        if self.permanent_cost:
            random_card.cost = self.permanent_cost
        if self.temp_cost:
            random_card.temp_cost = self.temp_cost

        # Return AddCardAction to be added to caller's action_queue
        return SingleActionResult(AddCardAction(card=random_card, dest_pile=self.pile))

@register("action")
class UpgradeAllCardsAction(Action):
    """Upgrade all cards in player's deck.

    Required:
        None

    Optional:
        None
    """

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        deck = game_state.player.card_manager.get_pile('deck')

        upgraded_count = 0
        for card in deck:
            if card.can_upgrade():
                card.upgrade()
                upgraded_count += 1

        if upgraded_count > 0:
            print(f"[Event] Upgraded {upgraded_count} card(s)")

        return NoneResult()

@register("action")
class UpgradeRandomCardAction(Action):
    """Upgrade a random card from player's deck.

    Required:
        count (int): Number of cards to upgrade

    Optional:
        card_type (str): Type of cards to choose from (Attack/Skill/Power)
        namespace (str): Card namespace (default: player's character)
    """
    def __init__(self, count: int = 1, card_type: Optional[str] = None, 
                 namespace: Optional[str] = None):
        self.count = count
        self.card_type = card_type
        self.namespace = namespace
    
    def execute(self) -> 'BaseResult':
        """Execute: upgrade random cards from deck"""
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        
        from utils.types import CardType
        
        # Get deck
        deck = game_state.player.card_manager.get_pile('deck')
        
        if not deck:
            return NoneResult()
        
        # Filter cards by type (if specified) and that can be upgraded
        cards_to_choose = []
        for card in deck:
            if not card.can_upgrade():
                continue
            if self.card_type is not None:
                # Match card type
                if self.card_type == "Attack" and card.card_type != CardType.ATTACK:
                    continue
                elif self.card_type == "Skill" and card.card_type != CardType.SKILL:
                    continue
                elif self.card_type == "Power" and card.card_type != CardType.POWER:
                    continue
            
            cards_to_choose.append(card)
        
        # Use specified namespace or default to player's character
        card_namespace = self.namespace if self.namespace else game_state.player.namespace
        
        # Filter cards by namespace if specified
        if self.namespace is not None:
            cards_to_choose = [c for c in cards_to_choose if c.namespace == card_namespace]
        
        if not cards_to_choose:
            print(t("ui.no_upgradeable_cards", default="No upgradeable cards found"))
            return NoneResult()
        
        # If requesting more than available, reduce to available
        actual_count = min(self.count, len(cards_to_choose))
        
        # Randomly select cards to upgrade
        import random
        cards_to_upgrade = random.sample(cards_to_choose, actual_count)
        
        # Create upgrade actions for all selected cards
        actions = []
        for card in cards_to_upgrade:
            actions.append(UpgradeCardAction(card=card))
        
        if len(actions) == 1:
            return SingleActionResult(actions[0])
        else:
            return MultipleActionsResult(actions)

@register("action")
class TransformRandomCardAction(Action):
    """Transform a random card from player's deck.

    Required:
        count (int): Number of cards to transform

    Optional:
        card_type (str): Type of cards to choose from (Attack/Skill/Power)
    """
    def __init__(self, count: int = 1, card_type: Optional[str] = None):
        self.count = count
        self.card_type = card_type

    def execute(self) -> 'BaseResult':
        """Execute: transform random cards from deck"""
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        from utils.types import CardType

        # Get deck
        deck = game_state.player.card_manager.get_pile('deck')

        if not deck:
            return NoneResult()

        # Filter cards by type (if specified)
        cards_to_choose = []
        for card in deck:
            if self.card_type is not None:
                # Match card type
                if self.card_type == "Attack" and card.card_type != CardType.ATTACK:
                    continue
                elif self.card_type == "Skill" and card.card_type != CardType.SKILL:
                    continue
                elif self.card_type == "Power" and card.card_type != CardType.POWER:
                    continue

            cards_to_choose.append(card)

        if not cards_to_choose:
            print(t("ui.no_cards_to_transform", default="No cards to transform found"))
            return NoneResult()

        # If requesting more than available, reduce to available
        actual_count = min(self.count, len(cards_to_choose))

        # Randomly select cards to transform
        import random
        cards_to_transform = random.sample(cards_to_choose, actual_count)

        # Create transform actions for all selected cards
        actions = []
        for card in cards_to_transform:
            actions.append(TransformCardAction(card=card, pile='deck'))

        if len(actions) == 1:
            return SingleActionResult(actions[0])
        else:
            return MultipleActionsResult(actions)

@register("action")
class TransformAndUpgradeCardAction(Action):
    """Transform a card and upgrade the new card.
    
    Used by Astrolabe relic.
    
    Required:
        card (Card): Card to transform
        pile (str): Card location
        
    Optional:
        None
    """
    def __init__(self, card, pile: str):
        self.card = card
        self.pile = pile
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if not game_state.player:
            return NoneResult()

        namespace = self.card.namespace
        
        # Get a random card from the same namespace
        new_card = get_random_card(namespaces=[namespace])
        
        if new_card is None:
            return NoneResult()
        
        # Upgrade the new card before adding
        if new_card.can_upgrade():
            new_card.upgrade()
        
        # Return actions: remove old card, add upgraded new card
        return MultipleActionsResult([
            RemoveCardAction(card=self.card, src_pile=self.pile),
            AddCardAction(card=new_card, dest_pile=self.pile),
        ])

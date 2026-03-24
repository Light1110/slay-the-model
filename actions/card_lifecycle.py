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

@register("action")
class RemoveCardAction(Action):
    """Choose a card to remove from src pile
    
    Required:
        card (Card): Card to remove
        src_pile (str): Card location
        
    Optional:
        None
    """
    def __init__(self, card, src_pile: str):
        self.card = card
        self.src_pile = src_pile
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
        return NoneResult()

@register("action")
class AddCardAction(Action):
    """Add a specific card to a pile

    Required:
        card (Card): Card to add
        dest_pile (str): Destination pile

    Optional:
        source (str): Source of card ("reward", "enemy", etc.)
        position (PilePosType): Position in pile (TOP or BOTTOM), default TOP
        
    Warning:
        This action doesn't copy the card
    """
    def __init__(
        self,
        card,
        dest_pile: str = None,
        source: str = None,
        position: PilePosType = PilePosType.TOP,
        chance: float = 1.0,
        target=None,
    ):
        self.card = card
        self.dest_pile = dest_pile
        self.source = source
        self.position = position
        self.chance = chance
        # Legacy call sites still pass target=player for AddCardAction.
        # The action always resolves against game_state.player, so keep the
        # argument for backward compatibility and ignore it.
        self.target = target

    def execute(self) -> 'BaseResult':
        import random
        from engine.game_state import game_state
        from engine.messages import CardDrawnMessage
        from engine.messages import CardAddedToPileMessage
        from utils.types import CardType

        # Check probability if chance < 1.0
        if self.chance < 1.0 and random.random() >= self.chance:
            # Chance check failed - don't add the card
            return NoneResult()

        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                target_pile = self.dest_pile or "deck"
                follow_up_actions = []
    
                # todo: 该遗物还没有被实现
                # Omamori: negate curse cards that would be added to deck.
                if (
                    target_pile in ("deck")
                    and getattr(self.card, "card_type", None) == CardType.CURSE
                ):
                    for relic in list(game_state.player.relics):
                        if getattr(relic, "idstr", None) != "Omamori":
                            continue
                        if not hasattr(relic, "try_negate_curse"):
                            continue
                        if relic.try_negate_curse():
                            if getattr(relic, "curses_to_negate", 0) <= 0:
                                game_state.player.relics.remove(relic)
                            print(
                                f"[Relic] Omamori negated curse: "
                                f"{self.card.display_name.resolve()}"
                            )
                            return NoneResult()

                # Egg relics: upgrade qualifying cards before adding to deck.
                if target_pile in ("deck"):
                    for relic in list(game_state.player.relics):
                        hook = getattr(relic, "should_upgrade_added_card", None)
                        if not hook:
                            continue
                        if hook(self.card, target_pile) and self.card.can_upgrade():
                            self.card.upgrade()

                game_state.player.card_manager.add_to_pile(self.card, target_pile, pos=self.position)
                
                # todo: 改为事件系统
                # Ceramic Fish: whenever a card is added to deck, gain 9 gold.
                follow_up_actions.extend(
                    game_state.publish_message(
                        CardAddedToPileMessage(
                            card=self.card,
                            owner=game_state.player,
                            dest_pile=target_pile,
                            source=self.source,
                            position=self.position,
                        ),
                        participants=list(game_state.player.relics),
                    )
                )
                # Only show [Reward] for actual rewards, use appropriate prefix for others
                # Localize pile name
                pile_name = t(f'combat.{target_pile}', default=target_pile)
                if self.source is None:
                    print(f"{t('combat.card_added', default='Added')} {self.card.display_name.resolve()} {t('combat.to_pile', default='to')} {pile_name}")
                elif self.source == "reward":
                    print(f"[{t('combat.reward', default='Reward')}] {t('combat.card_added', default='Added')} {self.card.display_name.resolve()} {t('combat.to_pile', default='to')} {pile_name}")
                elif self.source == "enemy":
                    print(f"[{t('combat.enemy', default='Enemy')}] {t('combat.card_added', default='Added')} {self.card.display_name.resolve()} {t('combat.to_pile', default='to')} {pile_name}")
                else:
                    print(f"[{self.source.title()}] {t('combat.card_added', default='Added')} {self.card.display_name.resolve()} {t('combat.to_pile', default='to')} {pile_name}")
                if follow_up_actions:
                    return MultipleActionsResult(follow_up_actions)
        return NoneResult()

@register("action")
class ExhaustCardAction(Action):
    """Exhaust a card into exhaust pile.

    Required:
        card (Card): Card to exhaust

    Optional:
        source_pile (str): Source pile name
    """
    def __init__(self, card: "Card", source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from engine.messages import CardExhaustedMessage
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Actually exhaust card
            exhausted = game_state.player.card_manager.exhaust(self.card, src=self.source_pile)
            
            # Trigger card's on_exhaust method
            card_actions = self.card.on_exhaust() if hasattr(self.card, 'on_exhaust') else []

            message_actions = []
            if exhausted:
                message_actions = game_state.publish_message(
                    CardExhaustedMessage(
                        card=self.card,
                        owner=game_state.player,
                        source_pile=self.source_pile,
                    ),
                    participants=[
                        *list(getattr(game_state.player, "powers", [])),
                        *list(getattr(game_state.player, "relics", [])),
                    ],
                )

            return MultipleActionsResult(card_actions + message_actions)

        return NoneResult()

@register("action")
class DiscardCardAction(Action):
    """Discard a card into discard pile.

    Required:
        card (Card): Card to discard

    Optional:
        source_pile (str): Source pile name
    """
    def __init__(self, card: "Card", source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from engine.messages import CardDiscardedMessage
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Find source pile if not specified
            if self.source_pile is None:
                self.source_pile = game_state.player.card_manager.get_card_location(self.card)
            
            # Actually discard card
            discarded = game_state.player.card_manager.discard(self.card, src=self.source_pile)
            
            if discarded:
                actions = game_state.publish_message(
                    CardDiscardedMessage(
                        card=self.card,
                        owner=game_state.player,
                        source_pile=self.source_pile,
                    ),
                    participants=[self.card, *list(game_state.player.powers), *list(game_state.player.relics)],
                )
                if actions:
                    return MultipleActionsResult(actions)
        return NoneResult()

@register("action")
class DrawCardsAction(Action):
    """Draw cards from draw pile

    Required:
        count (int): Number of cards to draw

    Optional:
        None
    """
    def __init__(self, count: int):
        self.count = count

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from engine.messages import CardDrawnMessage

        if game_state.player and hasattr(game_state.player, "card_manager"):
            # Handle callable count (dynamic card draw amounts)
            count = self.count() if callable(self.count) else self.count
            # Draw cards from draw pile to hand
            cards: List[Card] = game_state.player.card_manager.draw_many(count)
            
            # Note: Draw message is now printed in CombatState._print_combat_state()
            # after "Player Turn" header for better display order
            
            message_actions = []
            for card in cards:
                message_actions.extend(
                    game_state.publish_message(
                        CardDrawnMessage(
                            card=card,
                            owner=game_state.player,
                        ),
                        participants=[card, *list(game_state.player.powers), *list(game_state.player.relics)],
                    )
                )
            
            # If there are any actions from powers/card callbacks, queue them
            if message_actions:
                from utils.result_types import MultipleActionsResult
                return MultipleActionsResult(message_actions)
            
            return NoneResult()

        return NoneResult()

@register("action")
class ReplaceCardAction(Action):
    """Discard the card and draw one
    
    Required:
        card (Card): the card to replcae
        
    Optional:
        None
    """
    def __init__(self, card: "Card"):
        self.card = card
        
    def execute(self) -> 'BaseResult':
        return MultipleActionsResult([
            DiscardCardAction(self.card),
            DrawCardsAction(count=1)
        ])

@register("action")
class ExhaustRandomCardAction(Action):
    """Exhaust random cards from a pile

    Required:
        pile (str): Source pile name
        amount (int): Number of cards to exhaust

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from engine.messages import ShuffleMessage
        import random

        if not game_state.player:
            return NoneResult()

        card_manager = game_state.player.card_manager
        cards_in_pile = list(card_manager.get_pile(self.pile))

        if not cards_in_pile:
            return NoneResult()

        amount_to_exhaust = min(self.amount, len(cards_in_pile))
        cards_to_exhaust = random.sample(cards_in_pile, amount_to_exhaust)

        actions = []
        for card in cards_to_exhaust:
            actions.append(ExhaustCardAction(card=card, source_pile=self.pile))

        if actions:
            return MultipleActionsResult(actions)
        return NoneResult()

@register("action")
class ShuffleAction(Action):
    """Shuffle all cards from hand and discard piles into draw pile."""

    def execute(self):
        """Execute shuffle: move all cards from hand/discard to draw pile and shuffle."""
        from engine.game_state import game_state
        from engine.messages import ShuffleMessage
        import random

        if not game_state.player or not hasattr(game_state.player, "card_manager"):
            return NoneResult()

        card_manager = game_state.player.card_manager

        # Collect all cards from hand and discard
        hand_cards = list(card_manager.get_pile("hand"))
        discard_cards = list(card_manager.get_pile("discard_pile"))

        # Add them to draw pile
        for card in hand_cards:
            card_manager.move_to(card=card, dst="draw_pile")
        for card in discard_cards:
            card_manager.move_to(card, "draw_pile")

        # Combine and shuffle
        draw_cards = card_manager.get_pile("draw_pile")
        random.shuffle(draw_cards)
        
        relic_actions = game_state.publish_message(
            ShuffleMessage(owner=game_state.player),
            participants=list(game_state.player.relics),
        )
        
        # If there are any actions from relic callbacks, queue them
        if relic_actions:
            return MultipleActionsResult(relic_actions)
        
        return NoneResult()

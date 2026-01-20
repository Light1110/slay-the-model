
from actions.base import Action
from utils.registry import register

@register("action")
class CreateRandomCardAction(Action):
    """Create a random card and add to deck"""
    def execute(self):
        from engine.game_state import game_state
        location = self.kwargs.get('location', 'deck')

        if not game_state.player:
            return

        # Generate a random card
        import random
        from cards.namespaces import CARD_NAMESPACES
        all_cards = []
        for namespace in CARD_NAMESPACES.values():
            all_cards.extend(namespace.keys())

        if all_cards:
            card_id = random.choice(all_cards)
            if location == 'deck':
                game_state.player.deck.append(card_id)
            from cards.registry import create_card
            card = create_card(card_id)
            from localization import t
            print(t("ui.received_card", default=f"Received card: {card.name if card else card_id}!", name=card.name if card else card_id))
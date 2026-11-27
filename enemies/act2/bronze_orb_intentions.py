"""Bronze Orb minion intentions."""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from typing import List
from enemies.intention import Intention
from actions.combat import AttackAction, GainBlockAction


class Steal(Intention):
    """Steal from the draw pile, or from the discard pile if the draw pile is empty."""

    def __init__(self, enemy):
        super().__init__("Steal", enemy)

    def execute(self) -> None:
        from engine.card_pools import java_id_key, original_id, original_rarity
        from engine.game_state import game_state
        from utils.types import RarityType

        if not game_state.player:
            return
        card_manager = game_state.player.card_manager
        pile_name = "draw_pile" if card_manager.get_pile("draw_pile") else "discard_pile"
        pile = card_manager.get_pile(pile_name)
        if not pile:
            return

        candidates = pile
        for rarity in (RarityType.RARE, RarityType.UNCOMMON, RarityType.COMMON):
            matching = [card for card in pile if original_rarity(card) == rarity]
            if matching:
                candidates = sorted(matching, key=lambda card: java_id_key(original_id(card)))
                break

        stolen_card = get_rng("card_random").choice(candidates)
        card_manager.remove_from_pile(stolen_card, pile_name)
        self.enemy.stolen_cards.append(stolen_card)


class SupportBeam(Intention):
    """Give Bronze Automaton 11 Block."""

    def __init__(self, enemy):
        super().__init__("Support Beam", enemy)
        self.base_block = 12

    def execute(self) -> None:
        """Give block to Bronze Automaton."""
        from engine.game_state import game_state
        actions = []
        # Find the Bronze Automaton (parent) in combat
        if game_state.current_combat:
            for e in game_state.current_combat.enemies:
                if e.__class__.__name__ == "BronzeAutomaton" and e.hp > 0:
                    actions.append(GainBlockAction(self.base_block, e))
                    break
        from engine.game_state import game_state
        add_actions(actions)
class Beam(Intention):
    """Deal 8 damage."""

    def __init__(self, enemy):
        super().__init__("Beam", enemy)
        self.base_damage = 8

    def execute(self) -> None:
        """Deal damage to player."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions([AttackAction(self.base_damage, game_state.player, self.enemy, "attack")])

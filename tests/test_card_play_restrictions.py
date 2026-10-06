"""Play restrictions from cards in hand, relics, and powers."""

import unittest

from cards.colorless.normality import Normality
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from cards.ironclad.whirlwind import Whirlwind
from powers.definitions.entangled import EntangledPower
from relics.global_relics.boss import VelvetChoker
from relics.global_relics.uncommon import BlueCandle
from tests.test_combat_utils import CombatTestHelper


class TestCardPlayRestrictions(unittest.TestCase):
    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(energy=3)
        self.combat = self.helper.start_combat([])

    def tearDown(self):
        self.helper._reset_game_state()

    def test_normality_in_hand_blocks_the_fourth_card(self):
        self.helper.add_card_to_hand(Normality())
        strike = Strike()
        self.helper.add_card_to_hand(strike)

        self.combat.combat_state.turn_cards_played = 2
        allowed, _ = strike.can_play()
        self.assertTrue(allowed)

        self.combat.combat_state.turn_cards_played = 3
        allowed, reason = strike.can_play()
        self.assertFalse(allowed)
        self.assertEqual(reason, "Normality restriction")

    def test_normality_outside_hand_does_not_block(self):
        self.helper.add_card_to_discard_pile(Normality())
        strike = Strike()
        self.helper.add_card_to_hand(strike)
        self.combat.combat_state.turn_cards_played = 5

        allowed, _ = strike.can_play()
        self.assertTrue(allowed)

    def test_multiple_normality_cards_do_not_stack(self):
        self.helper.add_card_to_hand(Normality())
        self.helper.add_card_to_hand(Normality())
        strike = Strike()
        self.helper.add_card_to_hand(strike)
        self.combat.combat_state.turn_cards_played = 2

        allowed, _ = strike.can_play()
        self.assertTrue(allowed)

    def test_blue_candle_cannot_play_normality_after_three_cards(self):
        self.player.relics.append(BlueCandle())
        normality = Normality()
        self.helper.add_card_to_hand(normality)

        self.combat.combat_state.turn_cards_played = 2
        allowed, _ = normality.can_play()
        self.assertTrue(allowed)

        self.combat.combat_state.turn_cards_played = 3
        allowed, reason = normality.can_play()
        self.assertFalse(allowed)
        self.assertEqual(reason, "Normality restriction")

    def test_velvet_choker_blocks_the_seventh_card(self):
        self.player.relics.append(VelvetChoker())
        strike = Strike()
        self.helper.add_card_to_hand(strike)

        self.combat.combat_state.turn_cards_played = 5
        allowed, _ = strike.can_play()
        self.assertTrue(allowed)

        self.combat.combat_state.turn_cards_played = 6
        allowed, reason = strike.can_play()
        self.assertFalse(allowed)
        self.assertEqual(reason, "Velvet Choker restriction (max 6 cards per turn)")

    def test_velvet_choker_also_blocks_x_cost_cards(self):
        self.player.relics.append(VelvetChoker())
        whirlwind = Whirlwind()
        self.helper.add_card_to_hand(whirlwind)
        self.combat.combat_state.turn_cards_played = 6

        allowed, reason = whirlwind.can_play()
        self.assertFalse(allowed)
        self.assertEqual(reason, "Velvet Choker restriction (max 6 cards per turn)")

    def test_six_cards_are_playable_without_velvet_choker(self):
        strike = Strike()
        self.helper.add_card_to_hand(strike)
        self.combat.combat_state.turn_cards_played = 6

        allowed, _ = strike.can_play()
        self.assertTrue(allowed)

    def test_entangled_blocks_attacks_and_allows_skills(self):
        self.player.add_power(EntangledPower(duration=1, owner=self.player))
        strike = Strike()
        defend = Defend()
        self.helper.add_card_to_hand(strike)
        self.helper.add_card_to_hand(defend)

        attack_allowed, attack_reason = strike.can_play()
        skill_allowed, _ = defend.can_play()

        self.assertFalse(attack_allowed)
        self.assertEqual(attack_reason, "Entangled restriction")
        self.assertTrue(skill_allowed)

    def test_player_turn_start_resets_cards_played_this_turn(self):
        self.helper.add_card_to_hand(Normality())
        strike = Strike()
        self.helper.add_card_to_hand(strike)
        self.combat.combat_state.turn_cards_played = 3
        self.combat.combat_state.turn_attack_cards_played = 2
        self.combat.combat_state.discarded_cards_this_turn = 4

        blocked, _ = strike.can_play()
        self.assertFalse(blocked)

        self.combat._start_player_turn()

        self.assertEqual(self.combat.combat_state.turn_cards_played, 0)
        self.assertEqual(self.combat.combat_state.turn_attack_cards_played, 0)
        self.assertEqual(self.combat.combat_state.discarded_cards_this_turn, 0)
        allowed, _ = strike.can_play()
        self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()

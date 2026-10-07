"""Effect fixes for cards whose localization already matches the original game."""

from actions.card_choice import ChooseAddRandomCardAction
from actions.combat_cards import PlayCardBHAction
from cards.base import COST_X
from cards.colorless.discovery import Discovery
from cards.colorless.expunger import Expunger
from cards.colorless.miracle import Miracle
from cards.defect.darkness import Darkness
from cards.ironclad.defend import Defend
from cards.ironclad.disarm import Disarm
from cards.ironclad.intimidate import Intimidate
from cards.ironclad.strike import Strike
from cards.ironclad.war_cry import WarCry
from cards.silent.doppelganger import Doppelganger
from cards.silent.terror import Terror
from cards.watcher.meditate import Meditate
from cards.watcher.sanctity import Sanctity
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import CardType, StatusType


class TestLocalizationEffectCards:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=70, max_hp=70, energy=3)

    def _exhausts(self, card, target=None):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=target or enemy)
        assert card in self.player.card_manager.get_pile("exhaust_pile")

    def test_skill_exhaust_flags(self):
        for card in (Disarm(), Intimidate(), WarCry(), Terror()):
            assert card.exhaust is True

    def test_disarm_exhausts_when_played(self):
        self._exhausts(Disarm())

    def test_intimidate_exhausts_when_played(self):
        self._exhausts(Intimidate())

    def test_terror_exhausts_when_played(self):
        self._exhausts(Terror())

    def test_war_cry_exhausts_when_played(self):
        self._exhausts(WarCry(), target=self.player)

    def test_miracle_retains_and_exhausts(self):
        card = Miracle()
        assert card.retain is True
        assert card.exhaust is True

    def test_expunger_does_not_exhaust(self):
        card = Expunger(hits=2)
        assert card.exhaust is False
        assert "Exhaust" not in card.get_combat_description().resolve()

    def test_darkness_upgrade_keeps_cost(self):
        card = Darkness()
        card.upgrade()
        assert card.cost == 1

    def test_discovery_zero_cost_only_when_upgraded_and_still_exhausts(self):
        self.helper.start_combat([])
        base = Discovery()
        base.on_play([])
        queued = [
            action
            for action in self.helper.game_state.action_queue.queue
            if isinstance(action, ChooseAddRandomCardAction)
        ]
        assert queued[-1].cost_until_end_of_turn is None
        assert base.exhaust is True

        self.helper.game_state.action_queue.queue.clear()
        upgraded = Discovery()
        upgraded.upgrade()
        upgraded.on_play([])
        queued = [
            action
            for action in self.helper.game_state.action_queue.queue
            if isinstance(action, ChooseAddRandomCardAction)
        ]
        assert queued[-1].cost_until_end_of_turn == 0
        assert upgraded.exhaust is True

    def test_doppelganger_stays_x_cost_and_scales_on_upgrade(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.energy = 2
        card = Doppelganger()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=self.player)
        assert card in self.player.card_manager.get_pile("exhaust_pile")
        assert self.player.get_power("Energized").amount == 2
        assert self.player.get_power("Draw Card Next Turn").amount == 2

        upgraded = Doppelganger()
        upgraded.upgrade()
        assert upgraded._cost == COST_X
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.energy = 2
        self.helper.add_card_to_hand(upgraded)
        assert self.helper.play_card(upgraded, target=self.player)
        assert self.player.get_power("Energized").amount == 3
        assert self.player.get_power("Draw Card Next Turn").amount == 3

    def test_meditate_returns_a_retained_card_and_does_not_exhaust(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        returned = Strike()
        self.player.card_manager.piles["discard_pile"].append(returned)
        card = Meditate()
        self.helper.add_card_to_hand(card)
        assert self.helper.play_card(card, target=self.player)
        assert card not in self.player.card_manager.get_pile("exhaust_pile")
        assert returned in self.player.card_manager.get_pile("hand")
        assert returned.retain_this_turn is True
        assert self.player.status_manager.status == StatusType.CALM

    def test_sanctity_draws_only_after_a_skill(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        combat = self.helper.start_combat([enemy])
        draw_a = Strike()
        draw_b = Strike()
        self.player.card_manager.piles["draw_pile"] = [draw_a, draw_b]

        attack = Strike()
        self.helper.add_card_to_hand(attack)
        PlayCardBHAction(attack, [enemy]).execute()
        self.helper.game_state.drive_actions()

        sanctity = Sanctity()
        self.helper.add_card_to_hand(sanctity)
        PlayCardBHAction(sanctity, [self.player]).execute()
        self.helper.game_state.drive_actions()
        assert self.player.card_manager.piles["draw_pile"] == [draw_a, draw_b]

        self.player.card_manager.piles["draw_pile"] = [draw_a, draw_b]
        skill = Defend()
        self.helper.add_card_to_hand(skill)
        PlayCardBHAction(skill, [self.player]).execute()
        self.helper.game_state.drive_actions()
        combat.combat_state.reset_turn_info()
        assert combat.combat_state.last_played_card is skill

        sanctity_after_skill = Sanctity()
        self.helper.add_card_to_hand(sanctity_after_skill)
        PlayCardBHAction(sanctity_after_skill, [self.player]).execute()
        self.helper.game_state.drive_actions()
        assert draw_a not in self.player.card_manager.piles["draw_pile"]
        assert draw_b not in self.player.card_manager.piles["draw_pile"]

    def test_sanctity_ignores_calm_without_a_previous_skill(self):
        enemy = self.helper.create_enemy(Cultist, hp=40)
        self.helper.start_combat([enemy])
        self.player.status_manager.status = StatusType.CALM
        waiting = Strike()
        self.player.card_manager.piles["draw_pile"] = [waiting]
        card = Sanctity()
        self.helper.add_card_to_hand(card)
        PlayCardBHAction(card, [self.player]).execute()
        self.helper.game_state.drive_actions()
        assert waiting in self.player.card_manager.piles["draw_pile"]

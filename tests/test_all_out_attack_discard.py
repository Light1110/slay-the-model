from typing import cast

import pytest

from actions.base import LambdaAction
from actions.combat_cards import PlayCardAction
from cards.silent.all_out_attack import AllOutAttack
from cards.silent.defend import Defend
from cards.silent.tactician import Tactician
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from tests.test_deferred_damage_protocols import play, prepare


@pytest.mark.parametrize("health, expected_discards", [((1,), 0), ((1, 40), 1)])
def test_all_out_attack_discards_single_card_only_if_combat_continues(health, expected_discards):
    player, enemies, combat = prepare("silent", health=health)
    tactician = Tactician()
    piles = player.card_manager.piles
    piles["hand"] = [tactician]
    rng = cast(StreamRandom, get_rng("card_random"))
    before = rng.export_state()

    play(AllOutAttack())

    assert [enemy.hp for enemy in enemies] == [max(0, hp - 10) for hp in health]
    assert combat.combat_state.discarded_cards_this_turn == expected_discards
    assert (tactician in piles["discard_pile"]) == bool(expected_discards)
    assert player.energy == 9 + expected_discards
    assert rng.export_state() == before


def test_all_out_attack_selects_from_live_hand_after_damage(monkeypatch):
    player, (enemy,), combat = prepare("silent", health=(40,))
    piles = player.card_manager.piles
    card = AllOutAttack()
    initial = [Defend(), Defend()]
    replacement = [Defend(), Defend()]
    piles["hand"] = [*initial, card]
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(0)
    choose = rng.choice

    def choose_after_damage(candidates):
        assert enemy.hp == 30
        assert candidates == replacement
        return choose(candidates)

    def replace_hand():
        assert rng.counter == 0
        piles["hand"][:] = replacement
        piles["draw_pile"].extend(initial)

    monkeypatch.setattr(rng, "choice", choose_after_damage)
    game_state.add_actions([PlayCardAction(card), LambdaAction(replace_hand)])
    assert game_state.drive_actions() is None

    assert piles["hand"] == [replacement[1]]
    assert piles["draw_pile"] == initial
    assert replacement[0] in piles["discard_pile"]
    assert combat.combat_state.discarded_cards_this_turn == rng.counter == 1

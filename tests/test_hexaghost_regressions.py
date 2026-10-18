"""Hexaghost opening, locked damage, ascension, and Burn lifecycle."""
import pytest

from actions.combat import DealDamageAction, HealAction, LoseHPAction
from cards.colorless.burn import Burn
from cards.ironclad.strike import Strike
from enemies.act1.the_hexaghost import TheHexaghost
from engine.game_state import game_state
from localization import set_language
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper


@pytest.mark.parametrize('ascension', [0, 19])
def test_real_combat_preserves_opening_and_repeats_only_main_cycle(ascension):
    helper = create_test_helper()
    player = helper.create_player(hp=1000, max_hp=1000)
    player.base_draw_count = 0
    game_state.ascension = ascension
    boss = TheHexaghost()
    combat = helper.start_combat([boss])
    assert boss.current_intention is boss.intentions['activate']
    cycle = ['sear', 'tackle', 'sear', 'inflame', 'tackle', 'sear', 'inferno']
    expected = ['activate', 'divider', *cycle, *cycle]
    for index, name in enumerate(expected):
        combat._start_player_turn()
        game_state.drive_actions()
        assert boss.current_intention is boss.intentions[name]
        for _ in range(3):
            assert boss.determine_next_intention() is boss.intentions[name]
        before = player.hp
        combat._end_player_phase()
        combat.execute_enemy_phase()
        assert boss.history_intentions == expected[:index + 1]
        if index == 0:
            assert player.hp == before
            assert boss.current_intention is boss.intentions['divider']
            assert boss.intentions['divider'].base_damage == 84
        if name == 'inferno':
            burns = player.card_manager.get_pile('discard_pile')
            assert burns and all(isinstance(c, Burn) and c.upgrade_level == 1 for c in burns)
            assert boss._used_inferno
    assert boss.strength == (6 if ascension >= 19 else 4)


@pytest.mark.parametrize('new_hp', [40, 80])
def test_divider_locks_at_activation_despite_later_hp_loss_or_healing(new_hp):
    helper = create_test_helper()
    player = helper.create_player(hp=60, max_hp=80)
    combat = helper.start_combat([TheHexaghost()])
    boss = combat.enemies[0]
    combat._start_player_turn()
    game_state.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._start_player_turn()
    game_state.drive_actions()
    if new_hp < 60:
        LoseHPAction(amount=60 - new_hp).execute()
    else:
        HealAction(amount=new_hp - 60).execute()
    assert boss.intentions['divider'].base_damage == 6
    assert boss.intentions['divider'].description.kwargs['damage'] == 6
    combat._end_player_phase()
    combat.execute_enemy_phase()
    assert player.hp == new_hp - 36


@pytest.mark.parametrize('ascension,hp,tackle,inferno,cards,strength', [
    (0, 250, 5, 2, 1, 2), (3, 250, 5, 2, 1, 2), (4, 250, 6, 3, 1, 2),
    (8, 250, 6, 3, 1, 2), (9, 264, 6, 3, 1, 2),
    (18, 264, 6, 3, 1, 2), (19, 264, 6, 3, 2, 3),
])
def test_ascension_boundaries_and_inflame_execution(ascension, hp, tackle, inferno, cards, strength):
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = ascension
    boss = TheHexaghost()
    assert boss.max_hp == hp
    assert boss.intentions['tackle'].base_damage == tackle
    assert boss.intentions['inferno'].base_damage == inferno
    assert boss.intentions['sear'].base_cards == cards
    boss.intentions['inflame'].execute()
    game_state.drive_actions()
    assert boss.block == 12
    assert boss.strength == strength


@pytest.mark.parametrize('ascension,count', [(18, 1), (19, 2)])
@pytest.mark.parametrize('after_inferno', [False, True])
def test_sear_adds_distinct_burns_to_discard_only(ascension, count, after_inferno):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = ascension
    boss = TheHexaghost()
    boss._used_inferno = after_inferno
    boss.intentions['sear'].execute()
    game_state.drive_actions()
    burns = player.card_manager.get_pile('discard_pile')
    assert len(burns) == count
    assert len({id(card) for card in burns}) == count
    assert all(isinstance(card, Burn) and card.upgrade_level == int(after_inferno) for card in burns)
    assert player.hp == 74
    for pile in ('hand', 'draw_pile', 'exhaust_pile', 'deck'):
        assert not player.card_manager.get_pile(pile)


def test_inferno_upgrades_only_live_draw_and_discard_burns_after_six_hits(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=200, max_hp=200)
    boss = TheHexaghost()
    originals = {pile: Burn() for pile in ('draw_pile', 'discard_pile', 'hand', 'exhaust_pile', 'deck')}
    for pile, burn in originals.items():
        player.card_manager.get_pile(pile).append(burn)
    strike = Strike()
    player.card_manager.get_pile('draw_pile').append(strike)
    late_burn = Burn()
    damage_calls = []
    original_execute = DealDamageAction.execute
    def damage_step(action):
        assert all(b.upgrade_level == 0 for b in originals.values())
        assert not boss._used_inferno
        damage_calls.append(player.hp)
        original_execute(action)
        if len(damage_calls) == 6:
            player.card_manager.get_pile('discard_pile').append(late_burn)
    monkeypatch.setattr(DealDamageAction, 'execute', damage_step)
    boss.intentions['inferno'].execute()
    assert not boss._used_inferno
    game_state.drive_actions()
    assert len(damage_calls) == 6
    assert player.hp == 188
    for pile, burn in originals.items():
        assert burn.upgrade_level == int(pile in ('draw_pile', 'discard_pile'))
    assert late_burn.upgrade_level == 1
    assert strike.upgrade_level == 0
    discard = player.card_manager.get_pile('discard_pile')
    assert len(discard) == 5
    assert len({id(card) for card in discard}) == 5
    assert all(card.upgrade_level == 1 for card in discard)
    assert boss._used_inferno
    monkeypatch.setattr(DealDamageAction, 'execute', original_execute)
    boss.intentions['inferno'].execute()
    game_state.drive_actions()
    assert len(discard) == 8
    assert all(card.upgrade_level == 1 for card in discard)


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_intent_text_uses_locked_base_damage_and_normal_modifiers(language):
    helper = create_test_helper()
    player = helper.create_player(hp=60, max_hp=100)
    game_state.ascension = 19
    set_language(language)
    boss = TheHexaghost()
    boss.intentions['activate'].execute()
    boss.add_power(StrengthPower(amount=4, owner=boss))
    boss.add_power(WeakPower(duration=2, owner=boss))
    player.add_power(VulnerablePower(duration=2, owner=player))
    divider = boss.intentions['divider']
    assert divider.description.kwargs['damage'] == 11
    assert divider.description.kwargs['hits'] == 6
    player.hp = 100
    divider.execute()
    game_state.drive_actions()
    assert player.hp == 34
    for key in ('divider', 'sear', 'inflame', 'inferno'):
        text = str(boss.intentions[key].description)
        assert '{' not in text
    assert boss.intentions['sear'].description.kwargs['cards'] == 2
    assert boss.intentions['inflame'].description.kwargs['strength_gain'] == 3
    assert boss.intentions['inflame'].description.kwargs['block'] == 12

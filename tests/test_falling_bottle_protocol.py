"""Exercise Falling and bottle selection through room, reward, and combat entry points."""
from unittest.mock import patch

import pytest

from actions.reward import AddRelicAction, LoseRelicAction
from cards.colorless.regret import Regret
from cards.ironclad.defend import Defend
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from engine.random_streams import RandomStreams, StreamRandom
from events.falling import Falling
from events.nloth import Nloth
from localization import resolve_text
from relics.global_relics.common import Anchor
from relics.global_relics.event import NlothGift
from relics.global_relics.uncommon import BottledFlame, BottledLightning, BottledTornado
from test_designer_joust_protocol import choose, next_menu, open_event
from test_opening_draw_protocol import first_decision, prepare


@pytest.mark.parametrize("seed", range(16))
@pytest.mark.parametrize("index", [0, 1, 2])
def test_falling_previews_and_removes_the_seeded_instance(seed, index):
    marked_attack, legacy_skill = Strike(), Defend()
    marked_attack.bottled = True
    bottle = BottledLightning()
    bottle.selected_card = legacy_skill
    attacks = [Strike(), Strike()]
    skills = [Defend(), Defend()]
    powers = [Inflame()]
    for group in (attacks, skills, powers):
        group[-1].upgrade()
    deck = attacks + [legacy_skill] + powers + skills + [marked_attack]
    game_state.player.deck = deck.copy()
    game_state.player.relics = [bottle]
    game_state.random_streams = RandomStreams(seed)
    rng = game_state.random_streams["misc"]
    reference = StreamRandom(seed)
    attack, skill, power = [group[reference.random_int(len(group) - 1)]
                            for group in (attacks, skills, powers)]
    target = (skill, power, attack)[index]

    event = Falling()
    assert rng.export_state() == reference.export_state()
    room = open_event(event)
    menu = next_menu()
    assert not room.should_leave
    assert all(option.enabled for option in menu.options)
    assert resolve_text(target.display_name) in resolve_text(menu.options[index].name)
    assert resolve_text(menu.options[index].detail) == resolve_text(target.info())
    assert rng.export_state() == reference.export_state()
    actions = choose(index)
    game_state.drive_actions()
    assert room.should_leave
    assert game_state.player.deck == [card for card in deck if card is not target]
    for action in actions:
        action.execute()
    assert game_state.player.deck == [card for card in deck if card is not target]
    assert rng.export_state() == reference.export_state()
    assert rng.random_int(100) == reference.random_int(100)


@pytest.mark.parametrize("with_bottles", [False, True])
def test_falling_leaves_without_a_draw_or_loss_when_all_targets_unavailable(with_bottles):
    deck = [Strike(), Defend(), Inflame()] if with_bottles else [Regret()]
    for card in deck:
        card.bottled = with_bottles
    game_state.player.deck = deck.copy()
    rng = game_state.random_streams["misc"]
    before = rng.export_state()
    room = open_event(Falling())

    assert [option.enabled for option in next_menu().options] == [True]
    choose(0)
    game_state.drive_actions()
    assert room.should_leave
    assert game_state.player.deck == deck
    assert rng.export_state() == before


def test_falling_requires_a_loss_with_one_available_type():
    skill = Defend()
    game_state.player.deck = [skill, Regret()]
    rng = game_state.random_streams["misc"]
    before = rng.counter
    room = open_event(Falling())

    assert [option.enabled for option in next_menu().options] == [True, False, False]
    assert rng.counter == before + 1
    choose(0)
    game_state.drive_actions()
    assert room.should_leave
    assert skill not in game_state.player.deck
    assert rng.counter == before + 1


BOTTLES = [(BottledFlame, Strike), (BottledLightning, Defend), (BottledTornado, Inflame)]


@pytest.mark.parametrize("relic_class,card_class", BOTTLES)
@pytest.mark.parametrize("lose", [False, True])
def test_bottle_binds_a_real_deck_card_and_nloth_can_release_it(relic_class, card_class, lose):
    twin, selected = card_class(), card_class()
    selected.upgrade()
    deck = [twin, selected, Regret(), *[Regret() for _ in range(10)]]
    player, combat, observer = prepare(deck.copy(), [Anchor()])
    relic = relic_class()
    rng = game_state.random_streams["card_random"]
    before = rng.export_state()
    game_state.add_action(AddRelicAction(relic))

    assert [resolve_text(option.name) for option in next_menu().options] == [
        resolve_text(card.info()) for card in (twin, selected)
    ]
    choose(1)
    game_state.drive_actions()
    assert rng.export_state() == before
    assert relic.selected_card is selected and selected.bottled and not twin.bottled

    event = Nloth()
    open_event(event)
    choose(event.offered_relics.index(relic) if lose else len(event.offered_relics))
    game_state.drive_actions()
    assert (relic in player.relics) is not lose
    assert any(isinstance(relic, NlothGift) for relic in player.relics) is lose
    assert selected.bottled is not lose
    assert relic.selected_card is (None if lose else selected)
    assert not twin.bottled

    first_decision(combat)
    copies = [
        card for pile in ("hand", "draw_pile")
        for card in player.card_manager.get_pile(pile) if getattr(card, "origin_card", None) is selected
    ]
    assert len(copies) == 1
    assert copies[0] is not selected
    assert copies[0].upgrade_level == selected.upgrade_level
    assert copies[0].bottled is not lose
    if not lose:
        assert observer.draws[0] is copies[0]
    assert rng.export_state() == before


@pytest.mark.parametrize("relic_class,card_class", BOTTLES)
@pytest.mark.parametrize("size", [0, 1])
def test_bottle_handles_empty_and_single_candidate_sets(relic_class, card_class, size):
    deck = [card_class() for _ in range(size)]
    player, _, _ = prepare(deck, [])
    rng = game_state.random_streams["card_random"]
    before = rng.export_state()
    relic = relic_class()
    game_state.add_action(AddRelicAction(relic))
    if size:
        choose(0)
        game_state.drive_actions()
        assert relic.selected_card is player.deck[0]
    else:
        with patch.object(game_state, "resolve_input_request", side_effect=AssertionError("unexpected menu")):
            game_state.drive_actions()
        assert relic.selected_card is None
    assert rng.export_state() == before


def test_typed_relic_loss_clears_only_the_binding_last_released():
    selected, twin = Strike(), Strike()
    first, another = BottledFlame(), BottledFlame()
    player, _, _ = prepare([selected, twin], [first, another])
    first.bind_card(selected)
    another.bind_card(selected)

    LoseRelicAction(relic_type=BottledFlame).execute()
    LoseRelicAction(first).execute()
    assert player.relics == [another]
    assert first.selected_card is None and selected.bottled and not twin.bottled

    LoseRelicAction(another).execute()
    assert not player.relics and not selected.bottled and not twin.bottled

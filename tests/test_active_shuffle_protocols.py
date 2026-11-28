"""Native active shuffle, Mark of Pain and ordinary refill regressions."""
from typing import cast

import pytest

from actions.card_lifecycle import AddCardAction, DrawCardsAction
from cards.colorless.deep_breath import DeepBreath
from cards.colorless.wound import Wound
from cards.defect.reboot import Reboot
from cards.defect.scrape import Scrape
from cards.ironclad.defend import Defend
from cards.ironclad.havoc import Havoc
from enemies.act1.cultist import Cultist
from engine.combat import Combat
from engine.game_state import game_state
from engine.messages import ShuffleMessage
from engine.random_streams import StreamRandom, get_rng
from player.player_factory import create_player
from powers.definitions.no_draw import NoDrawPower
from relics.character.ironclad import MarkOfPain
from relics.global_relics.shop import TheAbacus
from relics.global_relics.uncommon import Sundial
from tests.test_deferred_damage_protocols import play, prepare
from tests.test_shuffle_insertion_reference import ROWS, normalized_calls
from tests.test_special_card_reference import trace_rng


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("card_type", [DeepBreath, Reboot])
@pytest.mark.parametrize("draw,discard,hand", [(4, 4, 3), (4, 0, 1), (0, 0, 0), (1, 1, 1)])
def test_actual_card_order_rng_relics_and_own_cleanup(role, ascension, upgraded, card_type, draw, discard, hand, monkeypatch):
    player, _, _ = prepare(role, ascension)
    labels = {}
    for pile, prefix, count in [("draw_pile", "D", draw), ("discard_pile", "C", discard), ("hand", "H", hand)]:
        cards = [Defend() for _ in range(count)]
        labels.update({id(card): prefix + str(index) for index, card in enumerate(cards)})
        player.card_manager.piles[pile] = cards
    sundial = Sundial()
    sundial.shuffle_count = 2
    player.relics = [sundial, TheAbacus()]
    rngs = {name: cast(StreamRandom, get_rng(name)) for name in ("card_random", "shuffle")}
    rngs["card_random"].seed(42)
    rngs["shuffle"].seed(43)
    calls = {name: trace_rng(rng, monkeypatch) for name, rng in rngs.items()}
    notices = []
    original = game_state.publish_message

    def publish(message, *args, **kwargs):
        if isinstance(message, ShuffleMessage):
            notices.append([rngs["card_random"].counter, rngs["shuffle"].counter])
        return original(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", publish)
    kind = "reboot" if card_type is Reboot else "deep_breath"
    expected = next(row for row in ROWS if row["kind"] == kind and row["seed"] == "42"
                    and (row["draw"], row["discard"], row["hand"]) == (draw, discard, hand))
    card = card_type()
    if upgraded:
        card.upgrade()
    assert play(card) is None
    count = min(card.draw, len(expected["draw_after"]), 10 - len(expected["hand_after"]))
    drawn = list(reversed(expected["draw_after"][-count:])) if count else []
    assert [labels[id(value)] for value in player.card_manager.get_pile("hand")] == expected["hand_after"] + drawn
    remaining = expected["draw_after"][:-count] if count else expected["draw_after"]
    assert [labels[id(value)] for value in player.card_manager.get_pile("draw_pile")] == remaining
    assert notices == expected["notices"]
    assert player.energy == 10 + (2 if notices else 0)
    assert player.block == (6 if notices else 0)
    assert sundial.shuffle_count == (0 if notices else 2)
    for name, prefix in [("card_random", "card"), ("shuffle", "shuffle")]:
        assert normalized_calls(calls[name]) == expected[prefix + "_calls"]
        state = rngs[name].export_state()
        assert {key: state[key] for key in expected[prefix + "_state"]} == expected[prefix + "_state"]
    assert player.card_manager.get_card_location(card) == ("exhaust_pile" if card_type is Reboot else "discard_pile")
    assert all(card is not value for value in player.card_manager.get_pile("draw_pile"))
    assert all(card is not value for value in player.card_manager.get_pile("hand"))


@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
@pytest.mark.parametrize("size", [0, 1, 4])
@pytest.mark.parametrize("seed", [0, 1])
def test_mark_of_pain_native_start_inserts_both_wounds(role, ascension, size, seed, monkeypatch):
    player = create_player(role, ascension=ascension)
    game_state.player = player
    game_state.ascension = ascension
    player.base_draw_count = 0
    player.card_manager.piles["deck"] = [Defend() for _ in range(size)]
    player.relics = [MarkOfPain()]
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(seed)
    calls = trace_rng(rng, monkeypatch)
    labels = {}
    inserted = []
    original = AddCardAction.execute

    def add(action):
        if isinstance(action.card, Wound):
            if not inserted:
                labels.update({id(card): "I" + str(index) for index, card in enumerate(player.card_manager.get_pile("draw_pile"))})
            labels[id(action.card)] = "N" + str(len(inserted))
            inserted.append(action.card)
        return original(action)

    monkeypatch.setattr(AddCardAction, "execute", add)
    combat = Combat(enemies=[Cultist()])
    game_state.combat = combat
    combat._init_combat()
    assert game_state.drive_actions() is None
    expected = next(row for row in ROWS if row["kind"] == "insert" and row["seed"] == str(seed)
                    and row["size"] == size and row["count"] == 2)
    assert len(inserted) == 2
    assert [labels[id(card)] for card in player.card_manager.get_pile("draw_pile")] == expected["stages"][-1]
    assert normalized_calls(calls) == expected["card_calls"]


@pytest.mark.parametrize("card_type", [DeepBreath, Reboot])
@pytest.mark.parametrize("upgraded", [False, True])
def test_no_draw_still_completes_active_shuffle(card_type, upgraded, monkeypatch):
    player, _, _ = prepare()
    player.add_power(NoDrawPower(owner=player))
    hand = Defend()
    discard = Defend()
    player.card_manager.piles["hand"] = [hand]
    player.card_manager.piles["discard_pile"] = [discard]
    rng = cast(StreamRandom, get_rng("shuffle"))
    calls = trace_rng(rng, monkeypatch)
    card = card_type()
    if upgraded:
        card.upgrade()
    assert play(card) is None
    assert len(calls) == 2 and all(call[0] == "long" for call in calls)
    expected_hand = [hand] if card_type is DeepBreath else []
    assert player.card_manager.get_pile("hand") == expected_hand


@pytest.mark.parametrize("upgraded", [False, True])
def test_deep_breath_draw_respects_full_hand(upgraded):
    player, _, _ = prepare()
    player.card_manager.piles["hand"] = [Defend() for _ in range(9)]
    player.card_manager.piles["draw_pile"] = [Defend() for _ in range(4)]
    card = DeepBreath()
    if upgraded:
        card.upgrade()
    assert play(card) is None
    assert len(player.card_manager.get_pile("hand")) == 10
    assert len(player.card_manager.get_pile("draw_pile")) == 3


@pytest.mark.parametrize("size", [1, 4])
def test_ordinary_nonempty_discard_refill_control(size, monkeypatch):
    player, _, _ = prepare()
    player.card_manager.piles["discard_pile"] = [Defend() for _ in range(size)]
    player.relics = [TheAbacus()]
    calls = trace_rng(cast(StreamRandom, get_rng("shuffle")), monkeypatch)
    game_state.add_action(DrawCardsAction(count=1))
    assert game_state.drive_actions() is None
    assert len(calls) == (1 if size else 0)
    assert player.block == (6 if size else 0)
    assert len(player.card_manager.get_pile("hand")) == min(size, 1)


@pytest.mark.parametrize(
    "draw,discard,count,hand,no_draw,expected_drawn,shuffles",
    [
        (0, 0, 1, 0, False, 0, 0),
        (1, 0, 1, 0, False, 1, 0),
        (1, 0, 2, 0, False, 1, 1),
        (0, 1, 1, 0, False, 1, 1),
        (0, 1, 2, 0, False, 1, 2),
        (1, 1, 3, 0, False, 2, 2),
        (1, 0, 2, 9, False, 1, 0),
        (0, 1, 2, 10, False, 0, 0),
        (0, 1, 2, 0, True, 0, 0),
    ],
)
def test_refill_consumes_one_long_per_scheduled_shuffle(
    draw, discard, count, hand, no_draw, expected_drawn, shuffles,
):
    player, _, _ = prepare()
    for pile, size in (("draw_pile", draw), ("discard_pile", discard), ("hand", hand)):
        player.card_manager.piles[pile] = [Defend() for _ in range(size)]
    sundial = Sundial()
    sundial.shuffle_count = 2
    player.relics = [TheAbacus(), sundial]
    if no_draw:
        player.add_power(NoDrawPower(owner=player))
    rng = cast(StreamRandom, get_rng("shuffle"))
    rng.seed(523)
    reference = StreamRandom(523)
    for _ in range(shuffles):
        reference.random_long()

    game_state.add_action(DrawCardsAction(count))
    assert game_state.drive_actions() is None

    assert len(player.card_manager.get_pile("hand")) == hand + expected_drawn
    assert player.block == 6 * shuffles
    assert player.energy == 10 + 2 * ((2 + shuffles) // 3)
    assert sundial.shuffle_count == (2 + shuffles) % 3
    assert rng.export_state() == reference.export_state()
    assert rng.random_int(1000) == reference.random_int(1000)


@pytest.mark.parametrize("discard", [False, True])
def test_havoc_preserves_target_draw_and_shuffles_only_if_it_can_play_a_card(discard):
    player, enemies, _ = prepare()
    defend = Defend()
    if discard:
        player.card_manager.piles["discard_pile"] = [defend]
    player.relics = [TheAbacus()]
    shuffle = cast(StreamRandom, get_rng("shuffle"))
    target_rng = cast(StreamRandom, get_rng("card_random"))
    shuffle.seed(523)
    target_rng.seed(523)
    expected_shuffle = StreamRandom(523)
    expected_target = StreamRandom(523)
    expected_target.random_int(len(enemies) - 1)
    if discard:
        expected_shuffle.random_long()

    assert play(Havoc()) is None

    assert shuffle.export_state() == expected_shuffle.export_state()
    assert target_rng.export_state() == expected_target.export_state()
    assert (defend in player.card_manager.get_pile("exhaust_pile")) is discard
    assert player.block == (11 if discard else 0)


@pytest.mark.parametrize("draw,shuffles", [(0, 0), (1, 1)])
def test_scrape_treats_queued_draws_as_one_request(draw, shuffles):
    player, _, _ = prepare("defect")
    player.card_manager.piles["draw_pile"] = [Defend() for _ in range(draw)]
    player.relics = [TheAbacus()]
    rng = cast(StreamRandom, get_rng("shuffle"))
    rng.seed(523)
    reference = StreamRandom(523)
    for _ in range(shuffles):
        reference.random_long()

    assert play(Scrape()) is None

    assert rng.export_state() == reference.export_state()
    assert player.block == 6 * shuffles


@pytest.mark.parametrize("card_type", [DeepBreath, Reboot])
def test_shuffle_relic_effects_run_before_preparation(card_type, monkeypatch):
    player, _, _ = prepare()
    player.card_manager.piles["discard_pile"] = [Defend()]
    sundial = Sundial()
    sundial.shuffle_count = 2
    player.relics = [TheAbacus(), sundial]
    rng = cast(StreamRandom, get_rng("shuffle"))
    original = rng.shuffle
    observations = []

    def shuffle(pile):
        observations.append((player.block, player.energy))
        return original(pile)

    monkeypatch.setattr(rng, "shuffle", shuffle)
    assert play(card_type()) is None
    assert observations == [(6, 12), (6, 12)]

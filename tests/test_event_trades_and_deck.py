"""Trades and deck changes for We Meet Again, the note, and Match and Keep."""
from engine.random_streams import get_rng

from typing import cast

import pytest

from actions.card import AddCardAction, ChooseRemoveCardAction, RemoveCardAction
from actions.display import InputRequestAction
from actions.reward import AddRandomRelicAction, LoseGoldAction, LosePotionAction
from cards.colorless.doubt import Doubt
from cards.ironclad.inflame import Inflame
from cards.ironclad.iron_wave import IronWave
from cards.ironclad.strike import Strike
from engine.card_pools import current_pools, original_id, original_rarity
from engine.game_state import game_state
from events.a_note_for_yourself import ANoteForYourself, StoreCardForFutureAction
from events.match_and_keep import _generate_card_pairs
from events.we_meet_again import WeMeetAgain
from potions.ironclad import BloodPotion
from tests.test_combat_utils import create_test_helper
from utils.types import RarityType


def _requests_in(actions) -> list[InputRequestAction]:
    found = [action for action in actions if isinstance(action, InputRequestAction)]
    return [cast(InputRequestAction, action) for action in found]


def _options(event) -> list:
    game_state.action_queue.clear()
    event.trigger()
    request = next(
        action
        for action in game_state.action_queue.queue
        if isinstance(action, InputRequestAction)
    )
    return list(cast(InputRequestAction, request).options)


def _removal(actions) -> ChooseRemoveCardAction:
    removal = next(action for action in actions if isinstance(action, ChooseRemoveCardAction))
    return cast(ChooseRemoveCardAction, removal)


def _pick(kind: str):
    def choice(seq):
        if kind in seq:
            return kind
        return seq[0]

    return choice


def test_we_meet_again_designates_one_potion_and_locks_it(monkeypatch):
    from actions.combat import UsePotionAction
    from rooms.event import EventRoom

    helper = create_test_helper()
    player = helper.create_player()
    potions = [BloodPotion(), BloodPotion()]
    player.potions.extend(potions)
    player.gold = 100
    player.deck.append(Inflame())
    monkeypatch.setattr(get_rng("misc"), "choice", _pick("potion"))

    options = _options(WeMeetAgain())
    trades = [option for option in options if option.actions]

    assert len(trades) == 1
    assert any(not option.actions for option in options)
    loss = next(action for action in trades[0].actions if isinstance(action, LosePotionAction))
    assert loss.potion is potions[0]
    assert loss.index is None
    assert any(isinstance(action, AddRandomRelicAction) for action in trades[0].actions)
    assert potions[0].event_locked is True
    assert potions[1].event_locked is False
    assert potions[0].can_use([]) is False

    UsePotionAction(potion=potions[0], target=player).execute()
    assert potions[0] in player.potions

    EventRoom().leave()
    assert potions[0].event_locked is False
    assert potions[0].can_use([]) is True


def test_we_meet_again_asks_for_gold_or_a_card_but_not_both(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    player.gold = 120
    player.deck.append(Inflame())
    monkeypatch.setattr(get_rng("misc"), "choice", _pick("gold"))
    monkeypatch.setattr(get_rng("misc"), "randint", lambda a, b: 50)

    options = _options(WeMeetAgain())
    trades = [option for option in options if option.actions]

    assert len(trades) == 1
    gold = next(
        action
        for action in trades[0].actions
        if isinstance(action, LoseGoldAction)
    )
    assert gold.amount == 50
    assert any(isinstance(action, AddRandomRelicAction) for action in trades[0].actions)

    monkeypatch.setattr(get_rng("misc"), "choice", _pick("card"))
    card_options = _options(WeMeetAgain())
    card_trades = [option for option in card_options if option.actions]
    assert len(card_trades) == 1
    removal = _removal(card_trades[0].actions)
    assert removal.exclude_rarities is not None
    assert RarityType.STARTER in removal.exclude_rarities
    assert RarityType.CURSE in removal.exclude_rarities
    assert removal.exclude_bottled is True


def test_we_meet_again_only_offers_attack_when_nothing_can_be_traded():
    helper = create_test_helper()
    player = helper.create_player()
    player.gold = 40
    bottled = Inflame()
    bottled.bottled = True
    player.deck.extend([Strike(), Doubt(), bottled])

    options = _options(WeMeetAgain())

    assert options
    assert all(not option.actions for option in options)


def test_note_defaults_to_iron_wave_and_stores_the_card_you_leave(monkeypatch, tmp_path):
    helper = create_test_helper()
    player = helper.create_player()
    strike = Strike()
    doubt = Doubt()
    player.deck.extend([strike, doubt])
    storage = tmp_path / "note.json"
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", storage)

    options = _options(ANoteForYourself())
    trades = [option for option in options if option.actions]

    assert len(trades) == 1
    picker = _requests_in(trades[0].actions)[0]
    removed = [
        next(action.card for action in option.actions if isinstance(action, RemoveCardAction))
        for option in picker.options
    ]
    assert removed == [strike]
    added = next(
        action.card
        for action in picker.options[0].actions
        if isinstance(action, AddCardAction)
    )
    assert isinstance(added, IronWave)
    assert added.upgrade_level == 0
    assert added.damage == 5

    for action in picker.options[0].actions:
        action.execute()

    assert strike not in player.deck
    assert any(isinstance(card, IronWave) and card.upgrade_level == 0 for card in player.deck)
    saved = storage.read_text(encoding="utf-8")
    assert '"namespace": "ironclad"' in saved
    assert '"name": "Strike"' in saved
    assert '"upgrade_level": 0' in saved


def test_note_returns_the_stored_card_from_its_namespace(monkeypatch, tmp_path):
    import cards.silent.strike  # noqa: F401

    helper = create_test_helper()
    player = helper.create_player()
    player.deck.append(Strike())
    storage = tmp_path / "note.json"
    storage.write_text(
        '{"stored_card": {"namespace": "ironclad", "name": "Strike", "upgrade_level": 1}}',
        encoding="utf-8",
    )
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", storage)

    options = _options(ANoteForYourself())
    picker = _requests_in(next(option.actions for option in options if option.actions))[0]
    added = next(
        action.card
        for action in picker.options[0].actions
        if isinstance(action, AddCardAction)
    )

    assert isinstance(added, Strike)
    assert added.namespace == "ironclad"
    assert added.__class__.__module__ == "cards.ironclad.strike"
    assert added.upgrade_level == 1
    assert added.damage == 9
    assert any(isinstance(action, StoreCardForFutureAction) for action in picker.options[0].actions)


def test_note_hides_the_trade_when_every_card_is_a_curse(monkeypatch, tmp_path):
    helper = create_test_helper()
    player = helper.create_player()
    player.deck.append(Doubt())
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", tmp_path / "note.json")

    options = _options(ANoteForYourself())

    assert options
    assert all(not option.actions for option in options)
    assert not (tmp_path / "note.json").exists()


def test_note_stays_hidden_on_ascension_15():
    helper = create_test_helper()
    helper.create_player()
    game_state.config.highest_unlocked_ascension = {game_state.player.namespace.lower(): 15}
    game_state.ascension = 14
    assert ANoteForYourself.can_appear()
    game_state.ascension = 15
    assert not ANoteForYourself.can_appear()


@pytest.mark.parametrize("namespace,starter", [
    ("ironclad", "Bash"), ("silent", "Neutralize"), ("defect", "Zap"), ("watcher", "Eruption"),
])
@pytest.mark.parametrize("ascension", [14, 15])
def test_match_and_keep_uses_ordered_role_slots_and_independent_eligible_curses(namespace, starter, ascension):
    helper = create_test_helper()
    player = helper.create_player()
    player.namespace = namespace
    game_state.ascension = ascension
    game_state.random_streams["card"].seed(9)
    game_state.random_streams["shuffle"].seed(9)
    pools = current_pools().current
    last_common = pools[(namespace, "COMMON")][-1]
    pools[(namespace, "COMMON")][:] = [last_common]
    colorless_before = pools[("colorless", None)].copy()
    pairs = _generate_card_pairs()
    originals = [card for card, _ in pairs]

    assert len(originals) == 6
    assert len({id(card) for pair in pairs for card in pair}) == 12
    assert all(original_id(first) == original_id(second) for first, second in pairs)
    assert [card.namespace for card in originals[:3]] == [namespace] * 3
    assert [original_rarity(card) for card in originals[:3]] == [
        RarityType.RARE, RarityType.UNCOMMON, RarityType.COMMON,
    ]
    assert original_id(originals[2]) == last_common
    assert original_id(originals[-1]) == starter
    if ascension >= 15:
        assert [original_id(card) for card in originals[3:5]] == ["Normality", "Normality"]
        assert pools[("colorless", None)] == colorless_before
        assert game_state.random_streams["card"].counter == 5
        assert game_state.random_streams["shuffle"].counter == 0
    else:
        assert originals[3].namespace == "colorless"
        assert original_rarity(originals[3]) == RarityType.UNCOMMON
        assert original_rarity(originals[4]) == RarityType.CURSE
        assert pools[("colorless", None)] != colorless_before
        assert game_state.random_streams["card"].counter == 4
        assert game_state.random_streams["shuffle"].counter == 1

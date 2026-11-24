from typing import cast

from actions.base import LambdaAction
from actions.combat_cards import PlayCardAction
from cards.colorless.violence import Violence
from cards.ironclad.anger import Anger
from cards.ironclad.bash import Bash
from cards.ironclad.clash import Clash
from cards.ironclad.defend import Defend
from cards.ironclad.rampage import Rampage
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from tests.test_deferred_damage_protocols import play, prepare


def test_violence_selects_attacks_from_draw_pile_at_effect_resolution():
    player, _, _ = prepare()
    piles = player.card_manager.piles
    original_attack = Strike()
    remaining_skill = Defend()
    replacement_attack = Strike()
    existing_discard = Strike()
    violence = Violence()
    piles["draw_pile"] = [original_attack, remaining_skill]
    piles["discard_pile"] = [existing_discard]
    piles["hand"] = [violence]
    card_rng = cast(StreamRandom, get_rng("card_random"))
    shuffle_rng = cast(StreamRandom, get_rng("shuffle"))
    card_rng.seed(0)
    shuffle_rng.seed(1)
    before_shuffle = shuffle_rng.export_state()

    def replace_attack():
        assert player.card_manager.get_card_location(violence) == "limbo"
        assert shuffle_rng.export_state() == before_shuffle
        piles["draw_pile"][0] = replacement_attack

    game_state.add_actions([PlayCardAction(violence), LambdaAction(replace_attack)])
    assert game_state.drive_actions() is None

    assert piles["hand"] == [replacement_attack]
    assert piles["draw_pile"] == [remaining_skill]
    assert piles["discard_pile"] == [existing_discard]
    assert piles["exhaust_pile"] == [violence]
    assert card_rng.counter == 0
    assert shuffle_rng.counter == 1


def test_violence_uses_original_selection_order_when_hand_overflows():
    player, _, _ = prepare()
    piles = player.card_manager.piles
    strike, skill, bash, anger, other_skill, rampage, clash = (
        Strike(), Defend(), Bash(), Anger(), Defend(), Rampage(), Clash(),
    )
    same_card_type = Strike()
    piles["draw_pile"] = [strike, skill, bash, anger, other_skill, rampage, clash]
    starting_hand = [same_card_type, *[Defend() for _ in range(8)]]
    piles["hand"] = starting_hand.copy()
    card_rng = cast(StreamRandom, get_rng("card_random"))
    shuffle_rng = cast(StreamRandom, get_rng("shuffle"))
    card_rng.seed(0)
    shuffle_rng.seed(1)
    violence = Violence()
    violence.upgrade()

    assert play(violence) is None

    assert piles["hand"] == [*starting_hand, bash]
    assert piles["discard_pile"] == [rampage, anger, strike]
    assert piles["draw_pile"] == [skill, other_skill, clash]
    assert card_rng.counter == shuffle_rng.counter == 4

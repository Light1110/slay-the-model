import pytest

from actions.card_lifecycle import DiscardCardAction, ExhaustRandomCardAction
from actions.combat_damage import DealDamageAction, LoseHPAction
from cards.colorless.burn import Burn
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from cards.ironclad.true_grit import TrueGrit
from cards.ironclad.whirlwind import Whirlwind
from enemies.act1.cultist import Cultist
from enemies.act3.awakened_one import AwakenedOne
from engine.combat import Combat
from engine.game_state import game_state
from potions.global_potions import SneckoOil
from powers.definitions.poison import PoisonPower
from relics.character.silent import TheSpecimen, Tingsha


def test_true_grit_exhausts_the_only_card_without_sampling():
    rng = game_state.random_streams["card_random"]
    rng.seed(0)
    card = Strike()
    piles = game_state.player.card_manager.piles
    piles["hand"] = [card]

    TrueGrit().on_play([])
    game_state.drive_actions()

    assert piles["hand"] == []
    assert piles["exhaust_pile"] == [card]
    assert (rng.counter, rng.randint(0, 999)) == (0, 972)


def test_exhaust_entire_pile_in_top_first_order_without_sampling():
    rng = game_state.random_streams["card_random"]
    piles = game_state.player.card_manager.piles
    cards = [Strike(), Inflame()]
    piles["draw_pile"] = cards.copy()
    before = rng.export_state()

    ExhaustRandomCardAction("draw_pile", amount=3).execute()
    game_state.drive_actions()

    assert piles["draw_pile"] == []
    assert piles["exhaust_pile"] == cards[::-1]
    assert rng.export_state() == before


def test_tingsha_selects_again_after_an_earlier_discard_kills():
    rng = game_state.random_streams["card_random"]
    rng.seed(0)
    enemies = [Cultist(), Cultist()]
    for enemy in enemies:
        enemy.hp = 3
    game_state.combat = Combat(enemies=enemies)
    game_state.player.relics.append(Tingsha())
    cards = [Strike(), Strike(), Strike()]
    game_state.player.card_manager.piles["hand"] = cards.copy()

    game_state.action_queue.add_actions([DiscardCardAction(card, source_pile="hand") for card in cards])
    game_state.drive_actions()

    assert all(enemy.is_dead() for enemy in enemies)
    assert (rng.counter, rng.randint(0, 999)) == (2, 752)


@pytest.mark.parametrize("direct_loss", [False, True])
def test_specimen_snapshots_poison_and_resolves_target_after_pending_death(direct_loss):
    rng = game_state.random_streams["card_random"]
    rng.seed(0)
    victim, next_victim, survivor = Cultist(), Cultist(), Cultist()
    victim.hp = next_victim.hp = 1
    victim.add_power(PoisonPower(amount=5, duration=5))
    game_state.combat = Combat(enemies=[victim, next_victim, survivor])
    game_state.player.relics.append(TheSpecimen())
    kill = LoseHPAction(amount=1, target=victim) if direct_loss else DealDamageAction(
        damage=1, target=victim, source=game_state.player,
    )

    game_state.action_queue.add_actions([kill, LoseHPAction(amount=1, target=next_victim)])
    game_state.action_queue.execute_next()
    assert rng.counter == 0
    game_state.drive_actions()

    assert victim.is_dead() and next_victim.is_dead()
    poison = survivor.get_power("Poison")
    assert poison is not None and poison.amount == 5
    assert (rng.counter, rng.randint(0, 999)) == (1, 960)


def test_specimen_ignores_half_dead_collapse():
    rng = game_state.random_streams["card_random"]
    victim, survivor = AwakenedOne(), Cultist()
    victim.hp = 1
    victim.add_power(PoisonPower(amount=5, duration=5))
    game_state.combat = Combat(enemies=[victim, survivor])
    game_state.player.relics.append(TheSpecimen())
    before = rng.export_state()

    LoseHPAction(amount=1, target=victim).execute()
    game_state.drive_actions()

    assert victim.half_dead
    assert survivor.get_power("Poison") is None
    assert rng.export_state() == before


def test_snecko_oil_skips_negative_base_costs_with_nonnegative_effective_costs():
    rng = game_state.random_streams["card_random"]
    rng.seed(0)
    burn, strike, whirlwind, inflame = Burn(), Strike(), Whirlwind(), Inflame()
    burn.cost_until_played = 0
    assert burn.cost == 0 and whirlwind.cost >= 0
    game_state.player.card_manager.piles["hand"] = [burn, strike, whirlwind, inflame]

    SneckoOil().on_use([])
    game_state.drive_actions()

    assert burn.cost_until_end_of_turn is None and whirlwind.cost_until_end_of_turn is None
    assert strike.cost_until_end_of_turn == inflame.cost_until_end_of_turn == 0
    assert (rng.counter, rng.randint(0, 999)) == (2, 752)

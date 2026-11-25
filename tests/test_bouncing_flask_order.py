from typing import cast

import pytest

from actions.base import LambdaAction
from actions.combat import ApplyPowerAction
from cards.silent.bouncing_flask import BouncingFlask
from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_action
from powers.definitions.artifact import ArtifactPower
from powers.definitions.poison import PoisonPower
from tests.test_deferred_damage_protocols import play, prepare
from tests.test_special_card_reference import trace_rng


@pytest.mark.parametrize("clear_all", [False, True])
def test_flask_rechecks_enemies_between_bounces(monkeypatch, clear_all):
    _, enemies, _ = prepare("silent", health=(40, 40, 40))
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(0)
    calls = trace_rng(rng, monkeypatch)
    applications = []
    apply_power = ApplyPowerAction.execute

    def resolve_casualties():
        for enemy in enemies[0 if clear_all else 1:]:
            enemy.hp = 0

    def observe_poison(action):
        apply_power(action)
        if isinstance(action.power, PoisonPower):
            assert action.target.hp > 0
            applications.append((enemies.index(action.target), rng.counter))
            if len(applications) == 1:
                add_action(LambdaAction(resolve_casualties), to_front=True)

    monkeypatch.setattr(ApplyPowerAction, "execute", observe_poison)
    play(BouncingFlask())

    assert calls[:2] == [["int", 2, 1], ["int", 2, 1]]
    if clear_all:
        assert len(calls) == 2
        assert applications == [(1, 2)]
    else:
        assert calls[2:] == [["int", 0, 0]]
        assert applications == [(1, 2), (0, 3)]


def test_upgraded_flask_rolls_each_bounce_even_with_one_enemy_and_artifact():
    _, (enemy,), _ = prepare("silent", health=(40,))
    enemy.add_power(ArtifactPower(owner=enemy))
    rng = cast(StreamRandom, get_rng("card_random"))
    rng.seed(0)
    card = BouncingFlask()
    card.upgrade()

    assert play(card) is None

    assert rng.counter == 4
    assert enemy.get_power("Artifact") is None
    poison = enemy.get_power("Poison")
    assert poison is not None and poison.amount == 9

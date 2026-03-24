import pytest

from entities.creature import Creature


class _TrackingPower:
    def __init__(self):
        self.damage_taken_calls = 0
        self.lose_hp_calls = 0
        self.power_added_calls = 0

    def on_damage_taken(self, *args, **kwargs):
        self.damage_taken_calls += 1
        return ["damage"]

    def on_lose_hp(self, *args, **kwargs):
        self.lose_hp_calls += 1
        return ["lose_hp"]

    def on_power_added(self, *args, **kwargs):
        self.power_added_calls += 1
        return ["power_added"]


def test_creature_legacy_wrappers_no_longer_fan_out_to_powers():
    power = _TrackingPower()
    creature = Creature(max_hp=20, powers=[power])

    assert creature.on_damage_taken(5) == []
    assert creature.on_lose_hp(3) == []
    assert creature.on_power_added(object()) == []

    assert power.damage_taken_calls == 0
    assert power.lose_hp_calls == 0
    assert power.power_added_calls == 0


def test_take_damage_list_input_raises_instead_of_silent_coercion():
    creature = Creature(max_hp=20)

    with pytest.raises(TypeError, match="take_damage expects int, got list"):
        creature.take_damage([3])

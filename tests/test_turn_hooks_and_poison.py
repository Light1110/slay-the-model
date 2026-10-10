"""Owner-scoped turn hooks, end-of-round debuffs, and poison timing."""

from enemies.act1.cultist import Cultist
from enemies.intention import Intention
from actions.combat import ApplyPowerAction
from powers.definitions.metallicize import MetallicizePower
from powers.definitions.poison import PoisonPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper


class RecordingIntention(Intention):
    def __init__(self, enemy):
        super().__init__("record", enemy)
        self.seen_hp = None
        self.seen_poison = None
        self.seen_vulnerable = None

    def execute(self) -> None:
        poison = self.enemy.get_power("Poison")
        vulnerable = self.enemy.get_power("Vulnerable")
        self.seen_hp = self.enemy.hp
        self.seen_poison = None if poison is None else poison.amount
        self.seen_vulnerable = None if vulnerable is None else vulnerable.duration


class ApplyWeakIntention(Intention):
    def __init__(self, enemy):
        super().__init__("apply_weak", enemy)

    def execute(self) -> None:
        from engine.game_state import game_state

        game_state.action_queue.add_action(
            ApplyPowerAction(
                WeakPower(amount=2, duration=2, owner=game_state.player),
                game_state.player,
                source=self.enemy,
            )
        )


def _prepare(helper, enemy_hp=40):
    helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=enemy_hp)
    combat = helper.start_combat([enemy])
    return combat, enemy


def test_player_poison_loses_one_stack_per_own_turn():
    helper = create_test_helper()
    combat, _enemy = _prepare(helper)
    player = helper.game_state.player
    player.add_power(PoisonPower(amount=3, duration=3, owner=player))

    expected_hp = 80
    for loss in (3, 2, 1):
        combat._start_player_turn()
        helper.game_state.drive_actions()
        expected_hp -= loss
        assert player.hp == expected_hp
        combat._end_player_phase()
        helper.game_state.drive_actions()
        if loss > 1:
            poison = player.get_power("Poison")
            assert poison is not None
            assert poison.amount == loss - 1

    assert player.get_power("Poison") is None


def test_enemy_poison_resolves_before_that_enemy_acts():
    helper = create_test_helper()
    combat, enemy = _prepare(helper, enemy_hp=50)
    enemy.add_power(PoisonPower(amount=5, duration=5, owner=enemy))
    intention = RecordingIntention(enemy)
    enemy.current_intention = intention

    combat.execute_enemy_phase()

    assert intention.seen_hp == 45
    assert intention.seen_poison == 4
    assert enemy.hp == 45
    assert enemy.get_power("Poison").amount == 4


def test_player_vulnerable_on_enemy_lasts_two_enemy_actions():
    helper = create_test_helper()
    combat, enemy = _prepare(helper)
    enemy.add_power(VulnerablePower(amount=2, duration=2, owner=enemy))
    first = RecordingIntention(enemy)
    enemy.current_intention = first

    combat._end_player_phase()
    helper.game_state.drive_actions()
    combat.execute_enemy_phase()

    assert first.seen_vulnerable == 2
    assert enemy.get_power("Vulnerable").duration == 1

    second = RecordingIntention(enemy)
    enemy.current_intention = second
    combat.execute_enemy_phase()

    assert second.seen_vulnerable == 1
    assert enemy.get_power("Vulnerable") is None


def test_monster_applied_weak_skips_the_round_it_was_applied():
    helper = create_test_helper()
    combat, enemy = _prepare(helper)
    player = helper.game_state.player
    enemy.current_intention = ApplyWeakIntention(enemy)

    combat.execute_enemy_phase()

    weak = player.get_power("Weak")
    assert weak is not None
    assert weak.duration == 2
    assert weak.just_applied is False

    enemy.current_intention = RecordingIntention(enemy)
    combat.execute_enemy_phase()

    weak = player.get_power("Weak")
    assert weak is not None
    assert weak.duration == 1


def test_metallicize_triggers_once_on_player_turn_end():
    helper = create_test_helper()
    combat, enemy = _prepare(helper)
    player = helper.game_state.player
    player.add_power(MetallicizePower(amount=3, owner=player))
    enemy.current_intention = RecordingIntention(enemy)

    combat._end_player_phase()
    helper.game_state.drive_actions()
    assert player.block == 3

    combat.execute_enemy_phase()
    assert player.block == 3


def test_player_turn_start_still_refreshes_enemy_intention():
    helper = create_test_helper()
    combat, enemy = _prepare(helper)

    combat._start_player_turn()

    assert enemy.current_intention is not None

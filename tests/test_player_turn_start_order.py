"""Player turn start runs refill, stance exit, hooks, block loss, then draw."""

from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from powers.base import Power
from powers.definitions.barricade import BarricadePower
from powers.definitions.blur import BlurPower
from powers.definitions.next_turn_block import NextTurnBlockPower
from relics.global_relics.common import Anchor
from relics.global_relics.rare import Calipers, IceCream
from tests.test_combat_utils import create_test_helper
from utils.types import StatusType


class _TurnOrderObserver(Power):
    name = "Turn Order Observer"

    def __init__(self):
        super().__init__(amount=0, duration=-1)
        self.start_block = None
        self.start_energy = None
        self.start_status = None
        self.post_draw_status = None
        self.post_draw_hand = None

    def on_turn_start(self):
        from engine.game_state import game_state

        player = game_state.player
        self.start_block = player.block
        self.start_energy = player.energy
        self.start_status = player.status_manager.status

    def on_turn_start_post_draw(self):
        from engine.game_state import game_state

        player = game_state.player
        self.post_draw_status = player.status_manager.status
        self.post_draw_hand = list(player.card_manager.get_pile("hand"))


def _begin():
    helper = create_test_helper()
    player = helper.create_player(hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=40)
    combat = helper.start_combat([enemy])
    return helper, player, combat


def test_turn_start_hook_sees_refilled_energy_and_ice_cream_adds_leftover():
    helper, player, combat = _begin()
    player.max_energy = 3
    player.energy = 2
    ice_cream = IceCream()
    ice_cream.conserved_energy = 2
    player.relics.append(ice_cream)
    observer = _TurnOrderObserver()
    player.add_power(observer)

    combat._execute_player_start_phase()

    assert observer.start_energy == 3
    assert player.energy == 5


def test_divinity_exits_before_turn_start_and_post_draw_hooks():
    helper, player, combat = _begin()
    player.status_manager.status = StatusType.DIVINITY
    observer = _TurnOrderObserver()
    player.add_power(observer)

    combat._execute_player_start_phase()

    assert observer.start_status == StatusType.NEUTRAL
    assert observer.post_draw_status == StatusType.NEUTRAL
    assert player.status_manager.status == StatusType.NEUTRAL


def test_post_draw_hook_sees_the_card_drawn_this_turn():
    helper, player, combat = _begin()
    drawn = Strike()
    player.base_draw_count = 1
    player.card_manager.get_pile("draw_pile").append(drawn)
    observer = _TurnOrderObserver()
    player.add_power(observer)

    combat._execute_player_start_phase()

    assert observer.post_draw_hand is not None
    assert drawn in observer.post_draw_hand


def test_first_turn_keeps_block_gained_before_the_turn():
    helper, player, combat = _begin()
    player.block = 8

    combat._execute_player_start_phase()

    assert player.block == 8


def test_anchor_block_lasts_the_first_turn_and_clears_on_the_next():
    helper = create_test_helper()
    player = helper.create_player(hp=80, energy=3)
    player.relics.append(Anchor())
    combat = helper.start_combat([helper.create_enemy(Cultist, hp=40)])

    combat._execute_player_start_phase()
    assert player.block == 10

    combat._execute_player_start_phase()
    assert player.block == 0


def test_later_turn_shows_old_block_to_hooks_then_applies_next_turn_block():
    helper, player, combat = _begin()
    combat._execute_player_start_phase()

    player.block = 4
    player.add_power(NextTurnBlockPower(amount=7, owner=player))
    observer = _TurnOrderObserver()
    player.add_power(observer)

    combat._execute_player_start_phase()

    assert observer.start_block == 4
    assert player.block == 7


def test_calipers_keep_all_but_fifteen_block_on_later_turns():
    _helper, player, combat = _begin()
    combat._execute_player_start_phase()
    player.block = 20
    player.relics.append(Calipers())

    combat._execute_player_start_phase()

    assert player.block == 5


def test_barricade_and_blur_keep_block_on_later_turns():
    helper, player, combat = _begin()
    combat._execute_player_start_phase()
    player.block = 12
    player.add_power(BarricadePower(owner=player))

    combat._execute_player_start_phase()
    assert player.block == 12

    player.remove_power("Barricade")
    player.block = 9
    player.add_power(BlurPower(owner=player))
    combat._execute_player_start_phase()
    assert player.block == 9

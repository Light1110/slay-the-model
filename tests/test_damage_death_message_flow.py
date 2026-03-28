from actions.combat import DealDamageAction
from cards.ironclad.feed import Feed
from enemies.act1.cultist import Cultist
from enemies.act1.fungi_beast import FungiBeast
from relics.character.ironclad import RedSkull
from tests.test_combat_utils import create_test_helper


def test_damage_actions_import_from_split_modules():
    from actions.combat import DealDamageAction as CombatDealDamageAction
    from actions.combat import HealAction as CombatHealAction
    from actions.combat_damage import DealDamageAction as SplitDealDamageAction
    from actions.combat_damage import HealAction as SplitHealAction

    assert CombatDealDamageAction is SplitDealDamageAction
    assert CombatHealAction is SplitHealAction


def _capture_published_message_types(game_state, monkeypatch):
    original_publish = game_state.publish_message
    published = []

    def wrapped(message, *args, **kwargs):
        published.append(type(message).__name__)
        return original_publish(message, *args, **kwargs)

    monkeypatch.setattr(game_state, "publish_message", wrapped)
    return published


def test_deal_damage_action_publishes_damage_resolved_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=50, max_hp=80, energy=3)
    red_skull = RedSkull()
    player.relics = [red_skull]
    enemy = helper.create_enemy(Cultist, hp=30)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=25, target=player, source=enemy).execute()
    helper.game_state.drive_actions()

    assert "DamageResolvedMessage" in published
    assert player.strength == 3


def test_deal_damage_action_publishes_creature_died_message(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(FungiBeast, hp=1)
    helper.start_combat([enemy])

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=5, target=enemy, source=player).execute()
    helper.game_state.drive_actions()

    assert "DamageResolvedMessage" in published
    assert "CreatureDiedMessage" in published
    assert player.has_power("Vulnerable")


def test_deal_damage_action_preserves_card_on_fatal(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=10)
    helper.start_combat([enemy])
    card = Feed()
    initial_max_hp = player.max_hp

    published = _capture_published_message_types(helper.game_state, monkeypatch)

    DealDamageAction(damage=10, target=enemy, source=player, card=card, damage_type="attack").execute()
    helper.game_state.drive_actions()

    assert "DamageResolvedMessage" in published
    assert "CreatureDiedMessage" in published
    assert player.max_hp == initial_max_hp + 3


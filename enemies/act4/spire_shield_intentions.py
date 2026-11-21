"""Spire Shield Elite intentions for Act 4."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_actions

from actions.combat import ApplyPowerAction, AttackAction, GainBlockAction
from enemies.intention import Intention
from powers.definitions.focus import FocusPower
from powers.definitions.strength import StrengthPower


class Bash(Intention):
    """Deal damage and apply a conditional debuff."""

    def __init__(self, enemy):
        super().__init__("Bash", enemy)
        self.base_damage = 14 if enemy.ascension >= 3 else 12

    def execute(self):
        from engine.game_state import game_state

        player = game_state.player
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=player,
                source=self.enemy,
                damage_type="attack",
            )
        ]

        has_orb_slot = (
            hasattr(player, "orb_manager")
            and getattr(player.orb_manager, "max_orb_slots", 0) > 0
        )
        if has_orb_slot and cast(StreamRandom, get_rng("ai")).random_boolean():
            actions.append(ApplyPowerAction(FocusPower(amount=-1, owner=player), player, source=self.enemy))
        else:
            actions.append(ApplyPowerAction(StrengthPower(amount=-1, owner=player), player, source=self.enemy))

        from engine.game_state import game_state

        add_actions(actions)

        return
class Fortify(Intention):
    """All enemies gain 30 Block."""

    def __init__(self, enemy):
        super().__init__("Fortify", enemy)
        self.base_block = 30

    def execute(self):
        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None) or getattr(
            game_state, "combat", None
        )
        if combat is None:
            from engine.game_state import game_state
            add_actions([GainBlockAction(block=self.base_block, target=self.enemy)])
            return
        actions = []
        for enemy in combat.enemies:
            if enemy.is_alive:
                actions.append(GainBlockAction(block=self.base_block, target=enemy))
        from engine.game_state import game_state
        add_actions(actions)
        return
class Smash(Intention):
    """Deal heavy damage and gain Block."""

    def __init__(self, enemy):
        super().__init__("Smash", enemy)
        self.base_damage = 38 if enemy.ascension >= 3 else 34
        self.base_block = 99 if enemy.ascension >= 18 else self.base_damage

    def execute(self) -> None:
        from engine.game_state import game_state
        from utils.dynamic_values import resolve_potential_damage

        player = game_state.player
        block = self.base_block
        if self.enemy.ascension < 18:
            block = resolve_potential_damage(self.base_damage, self.enemy, player, damage_type="attack")
        add_actions([
            AttackAction(self.base_damage, player, self.enemy, "attack"),
            GainBlockAction(block=block, target=self.enemy),
        ])

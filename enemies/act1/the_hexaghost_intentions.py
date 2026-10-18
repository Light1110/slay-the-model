"""Hexaghost actions, locked Divider damage, and combat-only Burn handling."""
from typing import TYPE_CHECKING

from actions.base import LambdaAction
from actions.card import AddCardAction
from actions.combat import ApplyPowerAction, AttackAction, GainBlockAction
from cards.colorless.burn import Burn
from engine.runtime_api import add_actions
from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy


class _HexaghostAttackIntention(Intention):
    """Preview physical damage using the same type as the queued attacks."""

    @property
    def description(self):
        from engine.game_state import game_state
        from utils.dynamic_values import resolve_potential_damage

        return self.local(
            "description",
            damage=resolve_potential_damage(self.base_damage, self.enemy,
                                            game_state.player, damage_type="attack"),
            hits=self._get_hits(), cards=self.base_cards,
        )


class ActivateIntention(Intention):
    """Lock Divider's base damage at the end of the opening player turn."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("activate", enemy)

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        divider = self.enemy.intentions["divider"]
        divider.base_damage = game_state.player.hp // 12 + 1
        self.enemy.current_intention = divider


class DividerIntention(_HexaghostAttackIntention):
    """Attack six times using the base damage saved by Activate."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("divider", enemy)
        self._hits = 6

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        add_actions([
            AttackAction(damage=self.base_damage, target=game_state.player,
                         source=self.enemy, damage_type="attack")
            for _ in range(self._hits)
        ])


class SearIntention(_HexaghostAttackIntention):
    """Deal 6 damage and add Burns, upgraded after the first Inferno."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("sear", enemy)
        from engine.game_state import game_state

        self.base_damage = 6
        self.base_cards = 2 if game_state.ascension >= 19 else 1

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        burns = [Burn() for _ in range(self.base_cards)]
        if getattr(self.enemy, '_used_inferno', False):
            for burn in burns:
                burn.upgrade()
        add_actions([
            AttackAction(damage=self.base_damage, target=game_state.player,
                         source=self.enemy, damage_type="attack"),
            *[AddCardAction(card=burn, dest_pile="discard_pile") for burn in burns],
        ])


class TackleIntention(_HexaghostAttackIntention):
    """Deal 5 damage twice, or 6 twice on A4+."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("tackle", enemy)
        from engine.game_state import game_state

        self.base_damage = 6 if game_state.ascension >= 4 else 5
        self._hits = 2

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        add_actions([
            AttackAction(damage=self.base_damage, target=game_state.player,
                         source=self.enemy, damage_type="attack")
            for _ in range(self._hits)
        ])


class InflameIntention(Intention):
    """Gain 12 Block and 2 Strength, or 3 Strength on A19+."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("inflame", enemy)
        from engine.game_state import game_state

        self.base_block = 12
        self.base_strength_gain = 3 if game_state.ascension >= 19 else 2

    def execute(self) -> None:
        add_actions([
            GainBlockAction(block=self.base_block, target=self.enemy),
            ApplyPowerAction(power="strength", target=self.enemy,
                             amount=self.base_strength_gain, duration=-1),
        ])


class InfernoIntention(_HexaghostAttackIntention):
    """Attack six times, upgrade existing Burns, then add three Burn+."""

    def __init__(self, enemy: 'Enemy'):
        super().__init__("inferno", enemy)
        from engine.game_state import game_state

        self.base_damage = 3 if game_state.ascension >= 4 else 2
        self._hits = 6
        self.base_cards = 3

    def _upgrade_existing_burns(self) -> None:
        """Read the actual piles after all Inferno attacks have resolved."""
        from engine.game_state import game_state

        if game_state.player is None:
            return
        for pile in ("draw_pile", "discard_pile"):
            for card in list(game_state.player.card_manager.get_pile(pile)):
                if isinstance(card, Burn):
                    card.upgrade()

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        burns = [Burn() for _ in range(self.base_cards)]
        for burn in burns:
            burn.upgrade()
        add_actions([
            *[AttackAction(damage=self.base_damage, target=game_state.player,
                           source=self.enemy, damage_type="attack")
              for _ in range(self._hits)],
            LambdaAction(self._upgrade_existing_burns),
            *[AddCardAction(card=burn, dest_pile="discard_pile") for burn in burns],
            LambdaAction(lambda: setattr(self.enemy, '_used_inferno', True)),
        ])

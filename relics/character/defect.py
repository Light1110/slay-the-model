"""Defect-specific relics."""

from actions.orb import AddOrbAction
from orbs.lightning import LightningOrb
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


@register("relic")
class CrackedCore(Relic):
    """At the start of each combat, Channel 1 Lightning."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        from engine.runtime_api import add_actions

        add_actions([AddOrbAction(LightningOrb())])
        return

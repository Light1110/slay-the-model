"""Basic tests for relic implementations."""
import pytest
from relics.global_relics.common import Akabeko, Anchor, BagOfMarbles, BronzeScales
from relics.global_relics.uncommon import BlueCandle, BottledFlame, BottledLightning
from relics.global_relics.rare import DeadBranch, Ginger
from relics.global_relics.boss import SneckoEye, BustedCrown
from relics.character.ironclad import BurningBlood, RedSkull, BlackBlood


class TestRelicImports:
    """Test that relic modules can be imported."""
    
    def test_common_relics_import(self):
        """Common relics module should import successfully."""
        from relics.global_relics import common
        assert common is not None
        assert hasattr(common, 'Akabeko')
    
    def test_uncommon_relics_import(self):
        """Uncommon relics module should import successfully."""
        from relics.global_relics import uncommon
        assert uncommon is not None
        assert hasattr(uncommon, 'BlueCandle')
    
    def test_rare_relics_import(self):
        """Rare relics module should import successfully."""
        from relics.global_relics import rare
        assert rare is not None
        assert hasattr(rare, 'DeadBranch')
    
    def test_boss_relics_import(self):
        """Boss relics module should import successfully."""
        from relics.global_relics import boss
        assert boss is not None
        assert hasattr(boss, 'SneckoEye')
    
    def test_ironclad_relics_import(self):
        """Ironclad relics module should import successfully."""
        from relics.character import ironclad
        assert ironclad is not None
        assert hasattr(ironclad, 'BurningBlood')


class TestRelicInstantiation:
    """Test that relics can be instantiated."""
    
    def test_common_relics_can_instantiate(self):
        """Common relics should be instantiatable."""
        relic = Akabeko()
        assert relic is not None
    
    def test_uncommon_relics_can_instantiate(self):
        """Uncommon relics should be instantiatable."""
        relic = BlueCandle()
        assert relic is not None
    
    def test_rare_relics_can_instantiate(self):
        """Rare relics should be instantiatable."""
        relic = DeadBranch()
        assert relic is not None
    
    def test_boss_relics_can_instantiate(self):
        """Boss relics should be instantiatable."""
        relic = SneckoEye()
        assert relic is not None
    
    def test_ironclad_relics_can_instantiate(self):
        """Ironclad relics should be instantiatable."""
        relic = BurningBlood()
        assert relic is not None


class TestRelicMethods:
    """Test that relics have expected methods."""
    
    def test_relic_has_on_combat_start(self):
        """Relics should have on_combat_start hook."""
        relic = Anchor()
        assert hasattr(relic, 'on_combat_start')
    
    def test_relic_has_on_player_turn_start(self):
        """Relics should have on_player_turn_start hook."""
        relic = BronzeScales()
        assert hasattr(relic, 'on_player_turn_start')
    
    def test_relic_has_on_combat_end(self):
        """Relics should have on_combat_end hook."""
        relic = BurningBlood()
        assert hasattr(relic, 'on_combat_end')
    
    def test_relic_has_on_card_play(self):
        """Relics should have on_card_play hook."""
        relic = DeadBranch()
        assert hasattr(relic, 'on_card_play')

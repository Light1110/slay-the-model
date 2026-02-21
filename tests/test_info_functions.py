"""
Test info() functions for Relic, Potion, and Power classes.

Note: Due to circular import issues, these tests import base modules directly using importlib
"""
import unittest
import sys
import os
import importlib.util

# Import relic base module directly to avoid circular import
spec = importlib.util.spec_from_file_location(
    "relics.base",
    os.path.join(os.path.dirname(__file__), "..", "relics", "base.py")
)
relic_base_module = importlib.util.module_from_spec(spec)
sys.modules['relics.base'] = relic_base_module
spec.loader.exec_module(relic_base_module)
Relic = relic_base_module.Relic

# Import potion base module directly to avoid circular import
spec = importlib.util.spec_from_file_location(
    "potions.base",
    os.path.join(os.path.dirname(__file__), "..", "potions", "base.py")
)
potion_base_module = importlib.util.module_from_spec(spec)
sys.modules['potions.base'] = potion_base_module
spec.loader.exec_module(potion_base_module)
Potion = potion_base_module.Potion

# Import power base module directly to avoid circular import
spec = importlib.util.spec_from_file_location(
    "powers.base",
    os.path.join(os.path.dirname(__file__), "..", "powers", "base.py")
)
power_base_module = importlib.util.module_from_spec(spec)
sys.modules['powers.base'] = power_base_module
spec.loader.exec_module(power_base_module)
Power = power_base_module.Power

# Import utils.types separately
spec = importlib.util.spec_from_file_location(
    "utils.types",
    os.path.join(os.path.dirname(__file__), "..", "utils", "types.py")
)
types_module = importlib.util.module_from_spec(spec)
sys.modules['utils.types'] = types_module
spec.loader.exec_module(types_module)
RarityType = types_module.RarityType


class TestRelicInfo(unittest.TestCase):
    """Test Relic.info() function"""
    
    def test_relic_info_format(self):
        """Test that relic info returns expected format"""
        
        class TestRelic(Relic):
            pass
        
        relic = TestRelic()
        info = relic.info()
        
        # Check that info contains name
        self.assertIn("TestRelic", str(info))
        # Check that info contains rarity
        self.assertIn("Rarity: Common", str(info))
        # Check that info contains newline
        self.assertIn("\n", str(info))
        
    def test_relic_info_with_custom_rarity(self):
        """Test relic info with custom rarity"""
        
        class RareRelic(Relic):
            rarity = RarityType.RARE
        
        relic = RareRelic()
        info = relic.info()
        
        self.assertIn("Rarity: Rare", str(info))


class TestPotionInfo(unittest.TestCase):
    """Test Potion.info() function"""
    
    def test_potion_info_format(self):
        """Test that potion info returns expected format"""
        
        class TestPotion(Potion):
            pass
        
        potion = TestPotion()
        info = potion.info()
        
        # Check that info contains name
        self.assertIn("TestPotion", str(info))
        # Check that info contains rarity
        self.assertIn("Rarity: Common", str(info))
        # Check that info contains category
        self.assertIn("Category: Global", str(info))
        # Check that info contains newline
        self.assertIn("\n", str(info))
        
    def test_potion_info_with_custom_category(self):
        """Test potion info with custom category"""
        
        class CustomPotion(Potion):
            category = "Ironclad"
        
        potion = CustomPotion()
        info = potion.info()
        
        self.assertIn("Category: Ironclad", str(info))


class TestPowerInfo(unittest.TestCase):
    """Test Power.info() function"""
    
    def test_power_info_buff(self):
        """Test power info for buff"""
        
        class TestBuff(Power):
            is_buff = True
        
        power = TestBuff(amount=5, duration=3)
        info = power.info()
        
        # Check that info contains name
        self.assertIn("TestBuff", str(info))
        # Check that info contains amount
        self.assertIn("Amount: 5", str(info))
        # Check that info contains duration
        self.assertIn("Duration: 3", str(info))
        # Check that info shows it's a buff
        self.assertIn("Type: Buff", str(info))
        # Check that info contains newline
        self.assertIn("\n", str(info))
        
    def test_power_info_debuff(self):
        """Test power info for debuff"""
        
        class TestDebuff(Power):
            is_buff = False
        
        power = TestDebuff(amount=2, duration=5)
        info = power.info()
        
        self.assertIn("Amount: 2", str(info))
        self.assertIn("Duration: 5", str(info))
        self.assertIn("Type: Debuff", str(info))
        
    def test_power_info_permanent(self):
        """Test power info for permanent power (duration=-1)"""
        
        class TestPermanent(Power):
            is_buff = True
        
        power = TestPermanent(amount=10, duration=-1)
        info = power.info()
        
        self.assertIn("Amount: 10", str(info))
        self.assertIn("Duration: Permanent", str(info))


if __name__ == '__main__':
    unittest.main()
"""
Unit tests for Event Pool system with Act-based categorization.
"""
import unittest
from events.base_event import Event
from events.event_pool import EventPool, EventMetadata, register_event


class MockEvent(Event):
    """Mock event for testing"""
    
    def trigger(self) -> str:
        return None


class TestEventPool(unittest.TestCase):
    """Test cases for EventPool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pool = EventPool()
    
    def test_register_event(self):
        """Test event registration"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="test_event",
            acts=[1],
            weight=100,
            is_unique=False
        )
        
        # Check event is in registry
        self.assertIn("test_event", self.pool._event_registry)
        
        # Check metadata
        metadata = self.pool._event_registry["test_event"]
        self.assertEqual(metadata.event_class, MockEvent)
        self.assertEqual(metadata.event_id, "test_event")
        self.assertEqual(metadata.acts, [1])
        self.assertEqual(metadata.weight, 100)
        self.assertFalse(metadata.is_unique)
    
    def test_act_pool_assignment(self):
        """Test event is added to correct Act pools"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="act1_event",
            acts=[1],
            weight=100
        )
        
        self.assertIn("act1_event", self.pool._act_pools[1])
        self.assertNotIn("act1_event", self.pool._act_pools[2])
    
    def test_shared_event_assignment(self):
        """Test event with 'shared' acts is added to shared pool"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="shared_event",
            acts='shared',
            weight=100
        )
        
        self.assertIn("shared_event", self.pool._act_pools['shared'])
    
    def test_multi_act_event_assignment(self):
        """Test multi-Act event is added to multiple Act pools"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="multi_act_event",
            acts=[1, 2],
            weight=100
        )
        
        # Should be in Act 1 and Act 2 pools
        self.assertIn("multi_act_event", self.pool._act_pools[1])
        self.assertIn("multi_act_event", self.pool._act_pools[2])
        # Should NOT be in Act 3 pool
        self.assertNotIn("multi_act_event", self.pool._act_pools[3])
        # Should NOT be in shared pool
        self.assertNotIn("multi_act_event", self.pool._act_pools['shared'])
    
    def test_get_available_events(self):
        """Test getting available events for an Act"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="act1_event",
            acts=[1],
            weight=100
        )
        
        available = self.pool.get_available_events(act=1)
        self.assertEqual(len(available), 1)
        self.assertEqual(available[0].event_id, "act1_event")
    
    def test_available_events_filters_by_act(self):
        """Test that only events for current Act are available"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="act1_event",
            acts=[1],
            weight=100
        )
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="act3_event",
            acts=[3],
            weight=100
        )
        
        # Act 1 should only have Act 1 event
        act1_available = self.pool.get_available_events(act=1)
        self.assertEqual(len(act1_available), 1)
        self.assertEqual(act1_available[0].event_id, "act1_event")
        
        # Act 3 should only have Act 3 event
        act3_available = self.pool.get_available_events(act=3)
        self.assertEqual(len(act3_available), 1)
        self.assertEqual(act3_available[0].event_id, "act3_event")
    
    def test_shared_events_available_in_all_acts(self):
        """Test that shared events are available in all Acts 1-3"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="shared_event",
            acts='shared',
            weight=100
        )
        
        # Shared event should be available in all Acts 1-3
        for act in [1, 2, 3]:
            available = self.pool.get_available_events(act=act)
            event_ids = [e.event_id for e in available]
            self.assertIn("shared_event", event_ids, 
                         f"Shared event not available in Act {act}")
    
    def test_multi_act_events_available_in_specified_acts(self):
        """Test that multi-Act events are only available in specified Acts"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="acts_1_2_event",
            acts=[1, 2],
            weight=100
        )
        
        # Should be available in Acts 1 and 2
        for act in [1, 2]:
            available = self.pool.get_available_events(act=act)
            event_ids = [e.event_id for e in available]
            self.assertIn("acts_1_2_event", event_ids,
                         f"Multi-Act event not available in Act {act}")
        
        # Should NOT be available in Act 3
        act3_available = self.pool.get_available_events(act=3)
        event_ids = [e.event_id for e in act3_available]
        self.assertNotIn("acts_1_2_event", event_ids,
                        "Multi-Act event should not be available in Act 3")
    
    def test_unique_event_not_repeated(self):
        """Test that unique events are not available after being used"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="unique_event",
            acts=[1],
            weight=100,
            is_unique=True
        )
        
        # Event should be available initially
        available = self.pool.get_available_events(act=1)
        self.assertEqual(len(available), 1)
        
        # Mark as used
        self.pool.mark_event_used("unique_event")
        
        # Event should no longer be available
        available = self.pool.get_available_events(act=1)
        self.assertEqual(len(available), 0)
    
    def test_reset_unique_events(self):
        """Test resetting unique events"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="unique_event",
            acts=[1],
            weight=100,
            is_unique=True
        )
        
        # Mark as used
        self.pool.mark_event_used("unique_event")
        self.assertTrue(self.pool._event_registry["unique_event"].has_been_used)
        
        # Reset
        self.pool.reset_unique_events()
        self.assertFalse(self.pool._event_registry["unique_event"].has_been_used)
    
    def test_custom_condition_filter(self):
        """Test events filtered by custom condition"""
        condition_met = False
        
        def custom_condition():
            return condition_met
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="conditional_event",
            acts=[1],
            weight=100,
            requires_condition=custom_condition
        )
        
        # Event not available when condition is False
        available = self.pool.get_available_events(act=1)
        self.assertEqual(len(available), 0)
        
        # Event available when condition is True
        condition_met = True
        available = self.pool.get_available_events(act=1)
        self.assertEqual(len(available), 1)
    
    def test_get_random_event(self):
        """Test getting random event"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="event1",
            acts=[1],
            weight=100
        )
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="event2",
            acts=[1],
            weight=100
        )
        
        # Should return an event class
        event_class = self.pool.get_random_event(act=1)
        self.assertIsNotNone(event_class)
        self.assertIn(event_class, [MockEvent])
    
    def test_get_event_by_id(self):
        """Test getting event by ID"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="test_event",
            acts=[1],
            weight=100
        )
        
        event_class = self.pool.get_event_by_id("test_event")
        self.assertEqual(event_class, MockEvent)
        
        # Non-existent event should return None
        event_class = self.pool.get_event_by_id("nonexistent")
        self.assertIsNone(event_class)
    
    def test_get_events_by_act(self):
        """Test getting event IDs for a specific Act"""
        self.pool.register_event(
            event_class=MockEvent,
            event_id="act1_only",
            acts=[1],
            weight=100
        )
        
        self.pool.register_event(
            event_class=MockEvent,
            event_id="shared_event",
            acts='shared',
            weight=100
        )
        
        # Act 1 should have both exclusive and shared events
        act1_events = self.pool.get_events_by_act(1)
        self.assertIn("act1_only", act1_events)
        self.assertIn("shared_event", act1_events)
        
        # Act 2 should only have shared event
        act2_events = self.pool.get_events_by_act(2)
        self.assertNotIn("act1_only", act2_events)
        self.assertIn("shared_event", act2_events)


class TestEventDecorator(unittest.TestCase):
    """Test cases for @register_event decorator"""
    
    def setUp(self):
        """Set up test fixtures"""
        from events.event_pool import event_pool
        self.pool = event_pool
    
    def test_decorator_registration(self):
        """Test decorator registers event"""
        @register_event(
            event_id="decorated_event",
            acts=[2],
            weight=150,
            is_unique=True
        )
        class DecoratedEvent(Event):
            def trigger(self) -> str:
                return None
        
        # Check event is registered
        self.assertIn("decorated_event", self.pool._event_registry)
        
        metadata = self.pool._event_registry["decorated_event"]
        self.assertEqual(metadata.event_class, DecoratedEvent)
        self.assertEqual(metadata.acts, [2])
        self.assertEqual(metadata.weight, 150)
        self.assertTrue(metadata.is_unique)


class TestEventMetadata(unittest.TestCase):
    """Test cases for EventMetadata"""
    
    def test_metadata_initialization(self):
        """Test EventMetadata initialization"""
        metadata = EventMetadata(
            event_class=MockEvent,
            event_id="test",
            acts=[3],
            weight=200,
            is_unique=True
        )
        
        self.assertEqual(metadata.event_class, MockEvent)
        self.assertEqual(metadata.event_id, "test")
        self.assertEqual(metadata.acts, [3])
        self.assertEqual(metadata.weight, 200)
        self.assertTrue(metadata.is_unique)
        self.assertFalse(metadata.has_been_used)


if __name__ == '__main__':
    unittest.main()

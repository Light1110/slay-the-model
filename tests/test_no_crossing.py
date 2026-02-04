"""
Test to verify that map connections don't cross.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def check_no_crossing(nodes):
    """
    Check that no connections cross each other.
    
    A crossing occurs if:
    - Node A at position i connects to position j above
    - Node B at position k (where k > i) connects to position l (where l < j)
    
    This would mean the line from i to j crosses the line from k to l.
    """
    for floor in range(len(nodes) - 1):
        current_floor_nodes = nodes[floor]
        
        # Collect all connections from this floor
        connections = []
        for node in current_floor_nodes:
            for up_pos in node.connections_up:
                connections.append((node.position, up_pos))
        
        # Check for crossings
        # A crossing happens if (i, j) and (k, l) exist where i < k and j > l
        for i in range(len(connections)):
            for j in range(i + 1, len(connections)):
                pos1, up1 = connections[i]
                pos2, up2 = connections[j]
                
                if pos1 < pos2 and up1 > up2:
                    return False, (floor, pos1, up1, pos2, up2)
        
    return True, None


def test_no_crossing_multiple_maps():
    """Test multiple maps to ensure no crossing connections."""
    print("=" * 60)
    print("Test: No Crossing Connections")
    print("=" * 60)
    
    from map.map_manager import MapManager
    
    num_maps = 50
    passed = 0
    
    for seed in range(num_maps):
        manager = MapManager(seed=seed, act_id=1)
        map_data = manager.generate_map()
        
        is_valid, crossing_info = check_no_crossing(map_data.nodes)
        
        if is_valid:
            passed += 1
        else:
            floor, pos1, up1, pos2, up2 = crossing_info
            print(f"[FAIL] Map {seed}: Crossing detected!")
            print(f"  Floor {floor}:")
            print(f"    Node at pos {pos1} -> pos {up1}")
            print(f"    Node at pos {pos2} -> pos {up2}")
            print()
            
            # Print the problematic floor
            print(f"  Floor {floor} details:")
            current_floor = map_data.get_floor(floor)
            next_floor = map_data.get_floor(floor + 1)
            
            print(f"  Current floor ({len(current_floor)} nodes):")
            for node in current_floor:
                print(f"    Pos {node.position}: Up -> {node.connections_up}")
            
            return False
    
    print(f"Checked {num_maps} maps")
    print(f"All maps passed: {passed}/{num_maps}")
    print()
    
    if passed == num_maps:
        print("[OK] No crossing connections detected in any map")
        print()
        return True
    else:
        print("[FAIL] Some maps have crossing connections")
        print()
        return False


def test_single_map_detail():
    """Test a single map in detail."""
    print("=" * 60)
    print("Test: Single Map Detail")
    print("=" * 60)
    
    from map.map_manager import MapManager
    
    manager = MapManager(seed=42, act_id=1)
    map_data = manager.generate_map()
    
    print(f"Generated map with {map_data.floor_count} floors")
    print()
    
    # Check each floor
    all_valid = True
    for floor in range(map_data.floor_count - 1):
        current_floor = map_data.get_floor(floor)
        next_floor = map_data.get_floor(floor + 1)
        
        print(f"Floor {floor} -> {floor + 1}:")
        
        if not current_floor or not next_floor:
            print(f"  (empty floor)")
            continue
        
        # Display connections
        for node in current_floor:
            if node.connections_up:
                print(f"  Pos {node.position} -> {node.connections_up}")
        
        # Check for crossing
        is_valid, crossing_info = check_no_crossing([current_floor, next_floor])
        if not is_valid:
            _, pos1, up1, pos2, up2 = crossing_info
            print(f"  [CROSSING] Pos {pos1} -> {up1} crosses Pos {pos2} -> {up2}")
            all_valid = False
    
    print()
    
    if all_valid:
        print("[OK] No crossing connections in this map")
        print()
    else:
        print("[FAIL] Crossing connections detected")
        print()
    
    return all_valid


def main():
    """Run all tests."""
    print("\n")
    print("============================================================")
    print("         Map Connection Crossing Test")
    print("============================================================")
    print("\n")
    
    try:
        # Test single map in detail
        if not test_single_map_detail():
            return 1
        
        # Test multiple maps
        if not test_no_crossing_multiple_maps():
            return 1
        
        print("=" * 60)
        print("All crossing tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
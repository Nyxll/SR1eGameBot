"""
Initiative System Tests for SR1eGameBot (Python)
Tests validate initiative rolling and tracking
"""

import pytest
from src.initiative import (
    roll_initiative,
    track_initiative,
    add_player_mid_combat,
    remove_npc,
    calculate_phases,
    create_phase_order
)


class TestInitiativeSetup:
    """Test suite for initiative setup functionality."""
    
    # INIT-001: Set GM
    def test_init001_set_gm(self):
        """Verify GM can be set for initiative tracking."""
        result = set_gm('user123', 'channel456', 'gm789')
        
        assert result['success'] is True
        assert result['gm_id'] == 'gm789'
    
    # INIT-002: Set Player Initiative Formula
    def test_init002_set_player_formula(self):
        """Verify player can set init formula."""
        result = set_player_formula('user123', 'channel456', '1d6+4')
        
        assert result['success'] is True
        assert result['formula']['dice'] == 1
        assert result['formula']['modifier'] == 4
    
    # INIT-003: Set Player List
    def test_init003_set_player_list(self):
        """Verify GM can set players."""
        players = ['player1', 'player2', 'player3']
        result = set_player_list('gm123', 'channel456', players)
        
        assert result['success'] is True
        assert len(result['players']) == 3
        assert result['players'] == players
    
    # INIT-004: Add NPCs
    def test_init004_add_npcs(self):
        """Verify GM can add NPCs with formulas."""
        npcs = [
            {'label': 'thug1', 'dice': 1, 'modifier': 3},
            {'label': 'thug2', 'dice': 1, 'modifier': 3},
            {'label': 'boss', 'dice': 2, 'modifier': 5}
        ]
        
        result = add_npcs('gm123', 'channel456', npcs)
        
        assert result['success'] is True
        assert len(result['npcs']) == 3
        assert result['npcs'][0]['label'] == 'thug1'
        assert result['npcs'][2]['dice'] == 2


class TestInitiativeRolling:
    """Test suite for initiative rolling."""
    
    # INIT-010: Roll SR1e Initiative
    def test_init010_roll_sr1e_initiative(self):
        """Verify SR1e initiative rolls correctly."""
        characters = [
            {'id': 'P1', 'dice': 1, 'modifier': 4},
            {'id': 'P2', 'dice': 1, 'modifier': 6},
            {'id': 'P3', 'dice': 1, 'modifier': 3},
            {'label': 'thug1', 'dice': 1, 'modifier': 2},
            {'label': 'thug2', 'dice': 1, 'modifier': 2}
        ]
        
        result = track_initiative(characters, system='sr1e')
        
        # All combatants should have rolled
        assert len(result['order']) == 5
        
        # Should be sorted descending by initiative
        for i in range(len(result['order']) - 1):
            assert result['order'][i]['initiative'] >= result['order'][i + 1]['initiative']
        
        # Each should have correct structure
        for combatant in result['order']:
            assert 'initiative' in combatant
            assert 'rolls' in combatant
            assert combatant['initiative'] >= combatant['modifier'] + len(combatant['rolls'])
    
    # INIT-011: Roll SR3e Initiative with Multiple Passes
    def test_init011_roll_sr3e_multiple_passes(self):
        """Verify SR3e initiative with multiple passes."""
        characters = [
            {'id': 'samurai', 'dice': 2, 'modifier': 10},
            {'id': 'mage', 'dice': 3, 'modifier': 8}
        ]
        
        result = track_initiative(characters, system='sr3e')
        
        for combatant in result['order']:
            # Should have phases array
            assert 'phases' in combatant
            assert isinstance(combatant['phases'], list)
            
            # Phases should be initiative, initiative-10, initiative-20, etc.
            expected_phases = []
            phase = combatant['initiative']
            while phase > 0:
                expected_phases.append(phase)
                phase -= 10
            
            assert combatant['phases'] == expected_phases
        
        # Should have phase breakdown
        assert 'phase_order' in result
        assert isinstance(result['phase_order'], list)
    
    # INIT-012: Roll CP2020 Initiative (d10)
    def test_init012_roll_cp2020_initiative(self):
        """Verify CP2020 uses d10."""
        characters = [
            {'id': 'solo', 'dice': 1, 'modifier': 7},
            {'id': 'netrunner', 'dice': 1, 'modifier': 5}
        ]
        
        result = track_initiative(characters, system='cp2020')
        
        for combatant in result['order']:
            # Each roll should be 1-10 (d10)
            for roll in combatant['rolls']:
                assert 1 <= roll <= 10


class TestInitiativeManagement:
    """Test suite for managing initiative during combat."""
    
    # INIT-020: Add Player Mid-Combat
    def test_init020_add_player_mid_combat(self):
        """Verify adding player during initiative."""
        existing_init = {
            'order': [
                {'id': 'P1', 'initiative': 15},
                {'id': 'P2', 'initiative': 12}
            ]
        }
        
        new_player = {'id': 'P3', 'dice': 1, 'modifier': 8}
        result = add_player_mid_combat(existing_init, new_player)
        
        assert len(result['order']) == 3
        assert any(p['id'] == 'P3' for p in result['order'])
        
        # Should still be sorted
        for i in range(len(result['order']) - 1):
            assert result['order'][i]['initiative'] >= result['order'][i + 1]['initiative']
    
    # INIT-021: Remove NPC
    def test_init021_remove_npc(self):
        """Verify removing NPC from initiative."""
        existing_init = {
            'order': [
                {'id': 'P1', 'initiative': 15},
                {'label': 'thug1', 'initiative': 12},
                {'label': 'thug2', 'initiative': 10}
            ]
        }
        
        result = remove_npc(existing_init, 'thug1')
        
        assert len(result['order']) == 2
        assert not any(c.get('label') == 'thug1' for c in result['order'])
        assert any(c.get('label') == 'thug2' for c in result['order'])


class TestInitiativeTieBreaking:
    """Test suite for tie-breaking in initiative."""
    
    def test_break_ties_by_higher_modifier(self):
        """Verify ties broken by higher modifier."""
        characters = [
            {'id': 'P1', 'dice': 1, 'modifier': 10, 'rolls': [7]},  # init 17
            {'id': 'P2', 'dice': 1, 'modifier': 8, 'rolls': [9]}    # init 17
        ]
        
        result = track_initiative(characters)
        
        # P1 has higher modifier, should come first
        p1_index = next(i for i, c in enumerate(result['order']) if c['id'] == 'P1')
        p2_index = next(i for i, c in enumerate(result['order']) if c['id'] == 'P2')
        
        assert p1_index < p2_index
    
    def test_handle_multiway_ties(self):
        """Verify handling multi-way ties."""
        characters = [
            {'id': 'P1', 'dice': 1, 'modifier': 10, 'rolls': [7]},   # init 17
            {'id': 'P2', 'dice': 1, 'modifier': 8, 'rolls': [9]},    # init 17
            {'id': 'P3', 'dice': 1, 'modifier': 6, 'rolls': [11]}    # init 17
        ]
        
        result = track_initiative(characters)
        
        # Should be ordered by modifier: P1 (10), P2 (8), P3 (6)
        assert result['order'][0]['id'] == 'P1'
        assert result['order'][1]['id'] == 'P2'
        assert result['order'][2]['id'] == 'P3'


class TestInitiativeEdgeCases:
    """Test suite for edge cases in initiative."""
    
    def test_initiative_dice_never_explode(self):
        """Verify initiative dice don't explode even with ! notation."""
        result = roll_initiative('2d6!+10')
        
        # Should have exactly 2 rolls
        assert len(result['rolls']) == 2
        
        # Each roll should be 1-6
        for roll in result['rolls']:
            assert 1 <= roll <= 6
    
    def test_handle_zero_dice(self):
        """Verify handling zero dice (attribute only)."""
        result = roll_initiative('0d6+5')
        
        assert len(result['rolls']) == 0
        assert result['initiative'] == 5
    
    def test_handle_negative_modifiers(self):
        """Verify handling negative modifiers."""
        result = roll_initiative('1d6-2')
        
        assert result['modifier'] == -2
        assert result['initiative'] == result['rolls'][0] - 2
    
    def test_prevent_negative_initiative(self):
        """Verify initiatives don't go below 0."""
        result = roll_initiative('1d6-10')
        
        if result['initiative'] < 0:
            assert result['initiative'] == 0


class TestPhaseCalculation:
    """Test suite for SR3e phase calculation."""
    
    def test_calculate_correct_phases(self):
        """Verify correct phase calculation for SR3e."""
        test_cases = [
            {'init': 25, 'expected': [25, 15, 5]},
            {'init': 19, 'expected': [19, 9]},
            {'init': 8, 'expected': []},  # Below 10, no second pass
            {'init': 10, 'expected': [10]}
        ]
        
        for case in test_cases:
            phases = calculate_phases(case['init'])
            assert phases == case['expected']
    
    def test_create_phase_order_with_all_combatants(self):
        """Verify phase order includes all combatants."""
        characters = [
            {'id': 'P1', 'initiative': 19},
            {'id': 'P2', 'initiative': 17},
            {'id': 'P3', 'initiative': 8}
        ]
        
        phase_order = create_phase_order(characters)
        
        # Should have phases: 19, 17, 9, 8, 7
        assert {'phase': 19, 'actors': ['P1']} in phase_order
        assert {'phase': 17, 'actors': ['P2']} in phase_order
        assert {'phase': 9, 'actors': ['P1']} in phase_order
        assert {'phase': 8, 'actors': ['P3']} in phase_order
        assert {'phase': 7, 'actors': ['P2']} in phase_order


class TestPerformance:
    """Test suite for performance benchmarks."""
    
    def test_handle_large_initiative_lists(self):
        """Verify efficient handling of large initiative lists."""
        import time
        
        # Create 50 combatants
        characters = [
            {'id': f'char{i}', 'dice': 1, 'modifier': i % 10}
            for i in range(50)
        ]
        
        start = time.time()
        result = track_initiative(characters)
        duration = time.time() - start
        
        assert len(result['order']) == 50
        assert duration < 0.1  # Should complete in under 100ms


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("dice,modifier,min_init,max_init", [
    (1, 5, 6, 11),    # 1d6+5: min 6, max 11
    (2, 10, 12, 22),  # 2d6+10: min 12, max 22
    (3, 8, 11, 26),   # 3d6+8: min 11, max 26
])
def test_initiative_ranges(dice, modifier, min_init, max_init):
    """Test various initiative dice configurations."""
    result = roll_initiative(f'{dice}d6+{modifier}')
    
    assert len(result['rolls']) == dice
    assert min_init <= result['initiative'] <= max_init

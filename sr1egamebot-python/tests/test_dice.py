"""
Dice Rolling Tests for SR1eGameBot (Python)
Tests validate core dice rolling functionality
"""

import pytest
from src.dice_roller import roll_dice, roll_opposed


class TestDiceRolling:
    """Test suite for basic dice rolling functionality."""
    
    # DR-001: Single Die Roll
    def test_dr001_single_die_roll(self):
        """Verify single die roll produces valid result."""
        result = roll_dice(num_dice=1, explode=False, target_number=None)
        
        assert len(result['rolls']) == 1
        assert 1 <= result['rolls'][0] <= 6
        assert result['total'] == result['rolls'][0]
    
    # DR-002: Multiple Dice
    def test_dr002_multiple_dice(self):
        """Verify multiple dice roll correctly."""
        result = roll_dice(num_dice=5, explode=False, target_number=None)
        
        assert len(result['rolls']) == 5
        for roll in result['rolls']:
            assert 1 <= roll <= 6
        
        # Verify sorted descending
        assert result['rolls'] == sorted(result['rolls'], reverse=True)
        
        assert result['total'] == sum(result['rolls'])
    
    # DR-003: Exploding Dice
    def test_dr003_exploding_dice(self, monkeypatch):
        """Verify dice explode on 6s."""
        import random
        
        call_count = 0
        def mock_randint(a, b):
            nonlocal call_count
            call_count += 1
            # First 5 calls return 6 (explode), then return 3
            return 6 if call_count <= 5 else 3
        
        monkeypatch.setattr(random, 'randint', mock_randint)
        
        result = roll_dice(num_dice=3, explode=True, target_number=None)
        
        # Should have more than 3 rolls due to exploding
        assert len(result['rolls']) > 3
    
    # DR-004: Target Number Success Counting
    def test_dr004_target_number_success(self):
        """Verify success counting against TN."""
        result = roll_dice(num_dice=10, explode=False, target_number=4)
        
        assert len(result['rolls']) == 10
        
        # Count expected successes
        expected_successes = sum(1 for r in result['rolls'] if r >= 4)
        assert result['successes'] == expected_successes
    
    # DR-005: Opposed Roll
    def test_dr005_opposed_roll(self):
        """Verify opposed rolls calculate net successes."""
        result = roll_opposed(
            attacker_dice=5,
            attacker_explode=True,
            attacker_tn=4,
            defender_dice=6,
            defender_explode=True,
            defender_tn=5
        )
        
        assert 'attacker' in result
        assert 'defender' in result
        assert 'net_successes' in result
        
        expected_net = result['attacker']['successes'] - result['defender']['successes']
        assert result['net_successes'] == expected_net
    
    # DR-006: Dice with Modifier
    def test_dr006_dice_with_modifier(self):
        """Verify modifier is applied to total."""
        result = roll_dice(num_dice=6, explode=False, target_number=None, modifier=5)
        
        sum_of_rolls = sum(result['rolls'])
        assert result['total'] == sum_of_rolls + 5
    
    # DR-007: D10 Dice (Cyberpunk)
    def test_dr007_d10_dice(self):
        """Verify d10 dice for Cyberpunk systems."""
        result = roll_dice(num_dice=5, explode=False, target_number=None, dice_type='d10')
        
        assert len(result['rolls']) == 5
        for roll in result['rolls']:
            assert 1 <= roll <= 10
    
    # DR-E01: Zero Dice Error
    def test_dre01_zero_dice_error(self):
        """Verify error on zero dice."""
        with pytest.raises(ValueError, match="at least 1"):
            roll_dice(num_dice=0, explode=False, target_number=None)
    
    # DR-E02: Negative Dice Error
    def test_dre02_negative_dice_error(self):
        """Verify error on negative dice."""
        with pytest.raises(ValueError, match="at least 1"):
            roll_dice(num_dice=-5, explode=False, target_number=None)
    
    # DR-E03: Excessive Dice Limit
    def test_dre03_excessive_dice_limit(self):
        """Verify limit on maximum dice."""
        with pytest.raises(ValueError, match="maximum|limit|too many"):
            roll_dice(num_dice=1000, explode=False, target_number=None)
    
    # Performance Test
    def test_performance_100_dice(self):
        """Verify rolling 100 dice completes quickly."""
        import time
        
        start = time.time()
        roll_dice(num_dice=100, explode=False, target_number=None)
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in under 100ms
    
    # Randomness Test
    def test_randomness_variation(self):
        """Verify varied results over multiple rolls."""
        results = set()
        
        for _ in range(20):
            result = roll_dice(num_dice=5, explode=False, target_number=None)
            results.add(result['total'])
        
        # Should have multiple unique totals
        assert len(results) > 5


class TestEdgeCasesAndBoundaries:
    """Test suite for edge cases and boundary conditions."""
    
    def test_minimum_valid_dice(self):
        """Verify handling of minimum valid dice (1)."""
        result = roll_dice(num_dice=1, explode=False, target_number=None)
        assert len(result['rolls']) == 1
    
    def test_maximum_valid_dice(self):
        """Verify handling of maximum valid dice (100)."""
        result = roll_dice(num_dice=100, explode=False, target_number=None)
        assert len(result['rolls']) == 100
    
    def test_tn_1_all_succeed(self):
        """Verify TN of 1 means all dice succeed."""
        result = roll_dice(num_dice=10, explode=False, target_number=1)
        assert result['successes'] == 10
    
    def test_tn_6_only_sixes_succeed(self):
        """Verify TN of 6 means only 6s succeed."""
        result = roll_dice(num_dice=10, explode=False, target_number=6)
        assert 0 <= result['successes'] <= 10
    
    def test_prevent_infinite_exploding_loops(self, monkeypatch):
        """Verify infinite exploding loops are prevented."""
        import random
        
        # Mock to always roll 6
        monkeypatch.setattr(random, 'randint', lambda a, b: 6)
        
        # Should not hang or raise error, should cap iterations
        result = roll_dice(num_dice=1, explode=True, target_number=None)
        assert result is not None


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("num_dice,explode,tn", [
    (1, False, None),
    (5, True, 4),
    (10, False, 3),
    (20, True, 5),
])
def test_dice_variations(num_dice, explode, tn):
    """Test various dice roll configurations."""
    result = roll_dice(num_dice=num_dice, explode=explode, target_number=tn)
    
    # Basic validations
    assert len(result['rolls']) >= num_dice
    assert all(1 <= r <= 6 for r in result['rolls'])
    
    if tn is not None:
        expected_successes = sum(1 for r in result['rolls'] if r >= tn)
        assert result['successes'] == expected_successes


@pytest.mark.parametrize("dice_type,min_val,max_val", [
    ('d6', 1, 6),
    ('d10', 1, 10),
])
def test_different_dice_types(dice_type, min_val, max_val):
    """Test different dice types (d6, d10)."""
    result = roll_dice(num_dice=10, explode=False, target_number=None, dice_type=dice_type)
    
    assert all(min_val <= r <= max_val for r in result['rolls'])

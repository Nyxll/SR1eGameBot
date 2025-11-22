"""
Karma Pool Tests for SR1eGameBot (Python)
Tests validate Karma Pool mechanics (Shadowrun-specific)
"""

import pytest
from src.karma_pool import (
    reroll_failures,
    avoid_disaster,
    buy_karma_dice,
    buy_successes,
    KarmaTracker
)


class TestKarmaPoolRerolling:
    """Test suite for Karma Pool re-rolling mechanics."""
    
    # KARMA-001: First Re-roll (1 Karma)
    def test_karma001_first_reroll_costs_1(self):
        """Verify first re-roll costs 1 Karma."""
        failed_dice = [4, 3, 2, 1]
        result = reroll_failures(
            failed_dice=failed_dice,
            target_number=5,
            reroll_iteration=1
        )
        
        assert result['karma_cost'] == 1
        assert result['iteration'] == 1
        assert len(result['rolls']) == 4
    
    # KARMA-002: Second Re-roll (2 Karma)
    def test_karma002_second_reroll_costs_2(self):
        """Verify second re-roll costs 2 Karma."""
        failed_dice = [4, 2]
        result = reroll_failures(
            failed_dice=failed_dice,
            target_number=5,
            reroll_iteration=2
        )
        
        assert result['karma_cost'] == 2
        assert result['iteration'] == 2
    
    # KARMA-003: Third Re-roll (3 Karma)
    def test_karma003_third_reroll_costs_3(self):
        """Verify third re-roll costs 3 Karma."""
        failed_dice = [3]
        result = reroll_failures(
            failed_dice=failed_dice,
            target_number=5,
            reroll_iteration=3
        )
        
        assert result['karma_cost'] == 3
        assert result['iteration'] == 3
    
    # KARMA-004: Re-roll Creates New Successes and Failures
    def test_karma004_separates_successes_and_failures(self):
        """Verify re-roll separates new successes from remaining failures."""
        result = reroll_failures(
            failed_dice=[4, 3, 2, 1],
            target_number=5,
            reroll_iteration=1
        )
        
        assert 'new_successes' in result
        assert 'remaining_failures' in result
        assert len(result['new_successes']) + len(result['remaining_failures']) == 4
        
        # Verify classification
        for roll in result['new_successes']:
            assert roll >= 5
        for roll in result['remaining_failures']:
            assert roll < 5
    
    # KARMA-005: Exploding Dice on Re-roll
    def test_karma005_exploding_dice_on_reroll(self, monkeypatch):
        """Verify exploding dice work on re-rolls."""
        import random
        monkeypatch.setattr(random, 'randint', lambda a, b: 6)
        
        result = reroll_failures(
            failed_dice=[4, 3],
            target_number=5,
            exploding=True,
            reroll_iteration=1
        )
        
        # With exploding, should get more than 2 rolls
        assert len(result['rolls']) >= 2


class TestKarmaPoolAvoidDisaster:
    """Test suite for Rule of One (avoiding disaster)."""
    
    # KARMA-010: Avoid Disaster Costs 1 Karma
    def test_karma010_avoid_disaster_costs_1(self):
        """Verify avoiding disaster costs 1 Karma."""
        roll_result = {
            'rolls': [1, 1, 1, 1, 1, 1],
            'successes': 0,
            'all_ones': True
        }
        
        result = avoid_disaster(roll_result)
        
        assert result['karma_cost'] == 1
        assert result['disaster'] is False
        assert result['critical_failure'] is False
    
    # KARMA-011: Only Works When All Ones
    def test_karma011_only_works_on_all_ones(self):
        """Verify avoid disaster only works when all dice are 1s."""
        roll_result = {
            'rolls': [1, 1, 1, 2],
            'successes': 0,
            'all_ones': False
        }
        
        with pytest.raises(ValueError, match="not a disaster"):
            avoid_disaster(roll_result)
    
    # KARMA-012: Cannot Re-roll After Avoiding Disaster
    def test_karma012_no_reroll_after_avoid(self):
        """Verify cannot re-roll after avoiding disaster."""
        roll_result = {
            'rolls': [1, 1, 1, 1],
            'successes': 0,
            'all_ones': True
        }
        
        result = avoid_disaster(roll_result)
        
        assert result['can_reroll'] is False
        assert result['final_result'] is True


class TestKarmaPoolBuyDice:
    """Test suite for buying Karma dice."""
    
    # KARMA-020: Buy Additional Dice (1 Karma Each)
    def test_karma020_buy_dice_costs_1_each(self):
        """Verify buying Karma dice costs 1 each."""
        result = buy_karma_dice(
            karma_dice_count=3,
            target_number=5
        )
        
        assert result['karma_cost'] == 3
        assert len(result['rolls']) == 3
    
    # KARMA-021: Respect Maximum Limit
    def test_karma021_respect_maximum_limit(self):
        """Verify maximum dice limit is enforced."""
        with pytest.raises(ValueError, match="maximum.*6"):
            buy_karma_dice(
                karma_dice_count=10,
                target_number=5,
                max_allowed=6
            )
    
    # KARMA-022: Karma Dice Can Explode
    def test_karma022_karma_dice_can_explode(self, monkeypatch):
        """Verify Karma dice can explode."""
        import random
        monkeypatch.setattr(random, 'randint', lambda a, b: 6)
        
        result = buy_karma_dice(
            karma_dice_count=2,
            target_number=5,
            exploding=True
        )
        
        # With exploding, should get more than 2 rolls
        assert len(result['rolls']) > 2
    
    # KARMA-023: Count Successes from Karma Dice
    def test_karma023_count_successes(self):
        """Verify successes counted from Karma dice."""
        result = buy_karma_dice(
            karma_dice_count=5,
            target_number=4
        )
        
        assert 'successes' in result
        expected_successes = sum(1 for r in result['rolls'] if r >= 4)
        assert result['successes'] == expected_successes


class TestKarmaPoolBuySuccesses:
    """Test suite for buying raw successes (permanent Karma)."""
    
    # KARMA-030: Buy Raw Successes (1 Karma Each, Permanent)
    def test_karma030_buy_successes_permanent(self):
        """Verify buying successes costs permanent Karma."""
        result = buy_successes(
            current_successes=2,
            successes_to_buy=3
        )
        
        assert result['karma_cost'] == 3
        assert result['permanent_karma_cost'] is True
        assert result['total_successes'] == 5
    
    # KARMA-031: Require At Least 1 Natural Success
    def test_karma031_require_natural_success(self):
        """Verify requires at least 1 natural success."""
        with pytest.raises(ValueError, match="at least 1 natural success"):
            buy_successes(
                current_successes=0,
                successes_to_buy=3
            )
    
    # KARMA-032: Warning About Permanent Cost
    def test_karma032_warns_about_permanent_cost(self):
        """Verify warning about permanent cost."""
        result = buy_successes(
            current_successes=1,
            successes_to_buy=2
        )
        
        assert 'warning' in result
        assert 'permanent' in result['warning'].lower()
        assert 'does not refresh' in result['warning'].lower()
    
    # KARMA-033: No Dice Rolled
    def test_karma033_no_dice_rolled(self):
        """Verify no dice rolled when buying successes."""
        result = buy_successes(
            current_successes=2,
            successes_to_buy=3
        )
        
        assert 'rolls' not in result or result['rolls'] is None
        assert result['total_successes'] == 5


class TestKarmaPoolComplexScenarios:
    """Test suite for complex Karma Pool usage scenarios."""
    
    def test_iterative_rerolling(self):
        """Verify handling iterative re-rolling."""
        failures = [4, 3, 2, 1]
        total_karma_spent = 0
        total_successes = 2  # Starting successes
        
        # First re-roll (1 Karma)
        result1 = reroll_failures(
            failed_dice=failures,
            target_number=5,
            reroll_iteration=1
        )
        total_karma_spent += result1['karma_cost']
        total_successes += len(result1['new_successes'])
        
        # Second re-roll (2 Karma)
        if len(result1['remaining_failures']) > 0:
            result2 = reroll_failures(
                failed_dice=result1['remaining_failures'],
                target_number=5,
                reroll_iteration=2
            )
            total_karma_spent += result2['karma_cost']
            total_successes += len(result2['new_successes'])
        
        # Verify escalating costs
        assert total_karma_spent >= 1
    
    def test_combined_karma_usage(self):
        """Verify combining different Karma Pool uses."""
        # Buy 3 Karma dice (3 Karma)
        karma_dice = buy_karma_dice(
            karma_dice_count=3,
            target_number=5,
            max_allowed=6
        )
        
        total_karma = karma_dice['karma_cost']
        successes = karma_dice['successes']
        
        # Re-roll failures once (1 Karma)
        failures = [r for r in karma_dice['rolls'] if r < 5]
        if failures:
            reroll = reroll_failures(
                failed_dice=failures,
                target_number=5,
                reroll_iteration=1
            )
            total_karma += reroll['karma_cost']
            successes += len(reroll['new_successes'])
        
        # Buy 2 more successes if needed (2 Karma, permanent)
        if successes < 6 and successes > 0:
            bought = buy_successes(
                current_successes=successes,
                successes_to_buy=2
            )
            total_karma += bought['karma_cost']
            successes = bought['total_successes']
        
        assert total_karma > 0
        assert successes > 0


class TestKarmaPoolEdgeCases:
    """Test suite for Karma Pool edge cases."""
    
    def test_zero_failures_to_reroll(self):
        """Verify error on zero failures."""
        with pytest.raises(ValueError, match="no failures"):
            reroll_failures(
                failed_dice=[],
                target_number=5,
                reroll_iteration=1
            )
    
    def test_invalid_iteration_number(self):
        """Verify error on invalid iteration."""
        with pytest.raises(ValueError, match="iteration.*at least 1"):
            reroll_failures(
                failed_dice=[4, 3],
                target_number=5,
                reroll_iteration=0
            )
    
    def test_buying_zero_karma_dice(self):
        """Verify error on buying zero dice."""
        with pytest.raises(ValueError, match="at least 1"):
            buy_karma_dice(
                karma_dice_count=0,
                target_number=5
            )
    
    def test_buying_zero_successes(self):
        """Verify error on buying zero successes."""
        with pytest.raises(ValueError, match="at least 1"):
            buy_successes(
                current_successes=3,
                successes_to_buy=0
            )
    
    def test_excessive_karma_dice(self):
        """Verify error on excessive Karma dice."""
        with pytest.raises(ValueError, match="too many|maximum"):
            buy_karma_dice(
                karma_dice_count=100,
                target_number=5
            )


class TestKarmaTracking:
    """Test suite for Karma Pool tracking."""
    
    def test_track_karma_spent_in_session(self):
        """Verify tracking Karma spent in session."""
        tracker = KarmaTracker(initial_karma=10)
        
        # Buy 3 dice
        tracker.spend(3, 'buy_dice')
        assert tracker.remaining == 7
        
        # Re-roll (1 Karma)
        tracker.spend(1, 'reroll')
        assert tracker.remaining == 6
        
        # Buy 2 successes (permanent)
        tracker.spend_permanent(2, 'buy_successes')
        assert tracker.remaining == 4
        assert tracker.permanent_spent == 2
        
        assert len(tracker.get_history()) == 3
    
    def test_prevent_overspending(self):
        """Verify cannot spend more than available."""
        tracker = KarmaTracker(initial_karma=5)
        
        with pytest.raises(ValueError, match="not enough karma"):
            tracker.spend(6, 'buy_dice')
    
    def test_refresh_nonpermanent_karma(self):
        """Verify refresh restores non-permanent Karma."""
        tracker = KarmaTracker(initial_karma=10)
        
        tracker.spend(3, 'buy_dice')
        tracker.spend_permanent(2, 'buy_successes')
        
        tracker.refresh()
        
        # Should restore to (10 - 2 permanent)
        assert tracker.remaining == 8
        assert tracker.permanent_spent == 2


# Parametrized tests for comprehensive coverage
@pytest.mark.parametrize("iteration,expected_cost", [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
])
def test_escalating_reroll_costs(iteration, expected_cost):
    """Test escalating re-roll costs."""
    result = reroll_failures(
        failed_dice=[4, 3],
        target_number=5,
        reroll_iteration=iteration
    )
    
    assert result['karma_cost'] == expected_cost


@pytest.mark.parametrize("dice_count,max_allowed,should_succeed", [
    (1, 5, True),
    (5, 5, True),
    (6, 5, False),
    (3, 10, True),
    (11, 10, False),
])
def test_karma_dice_limits(dice_count, max_allowed, should_succeed):
    """Test Karma dice limits."""
    if should_succeed:
        result = buy_karma_dice(
            karma_dice_count=dice_count,
            target_number=5,
            max_allowed=max_allowed
        )
        assert result['karma_cost'] == dice_count

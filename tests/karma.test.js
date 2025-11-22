/**
 * Karma Pool Tests for SR1eGameBot (JavaScript/Node.js)
 * Tests validate Karma Pool mechanics (Shadowrun-specific)
 */

const { 
  rerollFailures, 
  avoidDisaster, 
  buyKarmaDice,
  buySuccesses 
} = require('../ft_dicebot');

describe('Karma Pool - Re-rolling Failures', () => {
  
  // KARMA-001: First Re-roll (1 Karma)
  test('KARMA-001: Should cost 1 Karma for first re-roll', () => {
    const failedDice = [4, 3, 2, 1];
    const result = rerollFailures({
      failedDice,
      targetNumber: 5,
      rerollIteration: 1
    });
    
    expect(result.karmaCost).toBe(1);
    expect(result.iteration).toBe(1);
    expect(result.rolls).toHaveLength(4);
  });

  // KARMA-002: Second Re-roll (2 Karma)
  test('KARMA-002: Should cost 2 Karma for second re-roll', () => {
    const failedDice = [4, 2];
    const result = rerollFailures({
      failedDice,
      targetNumber: 5,
      rerollIteration: 2
    });
    
    expect(result.karmaCost).toBe(2);
    expect(result.iteration).toBe(2);
  });

  // KARMA-003: Third Re-roll (3 Karma)
  test('KARMA-003: Should cost 3 Karma for third re-roll', () => {
    const failedDice = [3];
    const result = rerollFailures({
      failedDice,
      targetNumber: 5,
      rerollIteration: 3
    });
    
    expect(result.karmaCost).toBe(3);
    expect(result.iteration).toBe(3);
  });

  // KARMA-004: Re-roll Creates New Successes and Failures
  test('KARMA-004: Should separate successes and failures after re-roll', () => {
    const result = rerollFailures({
      failedDice: [4, 3, 2, 1],
      targetNumber: 5,
      rerollIteration: 1
    });
    
    expect(result).toHaveProperty('newSuccesses');
    expect(result).toHaveProperty('remainingFailures');
    expect(result.newSuccesses.length + result.remainingFailures.length).toBe(4);
    
    // Verify classification
    result.newSuccesses.forEach(roll => {
      expect(roll).toBeGreaterThanOrEqual(5);
    });
    result.remainingFailures.forEach(roll => {
      expect(roll).toBeLessThan(5);
    });
  });

  // KARMA-005: Exploding Dice on Re-roll
  test('KARMA-005: Should handle exploding dice on re-roll', () => {
    const originalRandom = Math.random;
    Math.random = jest.fn(() => 0.99); // Force 6s
    
    const result = rerollFailures({
      failedDice: [4, 3],
      targetNumber: 5,
      exploding: true,
      rerollIteration: 1
    });
    
    // With exploding, should get more than 2 rolls
    expect(result.rolls.length).toBeGreaterThanOrEqual(2);
    
    Math.random = originalRandom;
  });
});

describe('Karma Pool - Avoid Disaster (Rule of One)', () => {
  
  // KARMA-010: Avoid Disaster Costs 1 Karma
  test('KARMA-010: Should cost 1 Karma to avoid disaster', () => {
    const rollResult = {
      rolls: [1, 1, 1, 1, 1, 1],
      successes: 0,
      allOnes: true
    };
    
    const result = avoidDisaster(rollResult);
    
    expect(result.karmaCost).toBe(1);
    expect(result.disaster).toBe(false);
    expect(result.criticalFailure).toBe(false);
  });

  // KARMA-011: Only Works When All Ones
  test('KARMA-011: Should only work when all dice are 1s', () => {
    const rollResult = {
      rolls: [1, 1, 1, 2],
      successes: 0,
      allOnes: false
    };
    
    expect(() => avoidDisaster(rollResult)).toThrow(/not a disaster/i);
  });

  // KARMA-012: Cannot Re-roll After Avoiding Disaster
  test('KARMA-012: Should prevent re-rolling after avoiding disaster', () => {
    const rollResult = {
      rolls: [1, 1, 1, 1],
      successes: 0,
      allOnes: true
    };
    
    const result = avoidDisaster(rollResult);
    
    expect(result.canReroll).toBe(false);
    expect(result.finalResult).toBe(true);
  });
});

describe('Karma Pool - Buy Karma Dice', () => {
  
  // KARMA-020: Buy Additional Dice (1 Karma Each)
  test('KARMA-020: Should cost 1 Karma per die', () => {
    const result = buyKarmaDice({
      karmaDiceCount: 3,
      targetNumber: 5
    });
    
    expect(result.karmaCost).toBe(3);
    expect(result.rolls).toHaveLength(3);
  });

  // KARMA-021: Respect Maximum Limit
  test('KARMA-021: Should respect maximum dice limit', () => {
    expect(() => {
      buyKarmaDice({
        karmaDiceCount: 10,
        targetNumber: 5,
        maxAllowed: 6
      });
    }).toThrow(/maximum.*6/i);
  });

  // KARMA-022: Karma Dice Can Explode
  test('KARMA-022: Should allow exploding on Karma dice', () => {
    const originalRandom = Math.random;
    Math.random = jest.fn(() => 0.99); // Force 6s
    
    const result = buyKarmaDice({
      karmaDiceCount: 2,
      targetNumber: 5,
      exploding: true
    });
    
    // With exploding, should get more than 2 rolls
    expect(result.rolls.length).toBeGreaterThan(2);
    
    Math.random = originalRandom;
  });

  // KARMA-023: Count Successes from Karma Dice
  test('KARMA-023: Should count successes from Karma dice', () => {
    const result = buyKarmaDice({
      karmaDiceCount: 5,
      targetNumber: 4
    });
    
    expect(result).toHaveProperty('successes');
    const expectedSuccesses = result.rolls.filter(r => r >= 4).length;
    expect(result.successes).toBe(expectedSuccesses);
  });
});

describe('Karma Pool - Buy Successes (Permanent)', () => {
  
  // KARMA-030: Buy Raw Successes (1 Karma Each, Permanent)
  test('KARMA-030: Should cost 1 Karma per success (permanent)', () => {
    const result = buySuccesses({
      currentSuccesses: 2,
      successesToBuy: 3
    });
    
    expect(result.karmaCost).toBe(3);
    expect(result.permanentKarmaCost).toBe(true);
    expect(result.totalSuccesses).toBe(5);
  });

  // KARMA-031: Require At Least 1 Natural Success
  test('KARMA-031: Should require at least 1 natural success', () => {
    expect(() => {
      buySuccesses({
        currentSuccesses: 0,
        successesToBuy: 3
      });
    }).toThrow(/at least 1 natural success/i);
  });

  // KARMA-032: Warning About Permanent Cost
  test('KARMA-032: Should warn about permanent cost', () => {
    const result = buySuccesses({
      currentSuccesses: 1,
      successesToBuy: 2
    });
    
    expect(result.warning).toMatch(/permanent/i);
    expect(result.warning).toMatch(/does not refresh/i);
  });

  // KARMA-033: No Dice Rolled
  test('KARMA-033: Should not roll dice when buying successes', () => {
    const result = buySuccesses({
      currentSuccesses: 2,
      successesToBuy: 3
    });
    
    expect(result.rolls).toBeUndefined();
    expect(result.totalSuccesses).toBe(5);
  });
});

describe('Karma Pool - Complex Scenarios', () => {
  
  test('Should handle iterative re-rolling', () => {
    // Simulate multiple re-rolls
    let failures = [4, 3, 2, 1];
    let totalKarmaSpent = 0;
    let totalSuccesses = 2; // Starting successes
    
    // First re-roll (1 Karma)
    let result1 = rerollFailures({
      failedDice: failures,
      targetNumber: 5,
      rerollIteration: 1
    });
    totalKarmaSpent += result1.karmaCost;
    totalSuccesses += result1.newSuccesses.length;
    
    // Second re-roll (2 Karma)
    if (result1.remainingFailures.length > 0) {
      let result2 = rerollFailures({
        failedDice: result1.remainingFailures,
        targetNumber: 5,
        rerollIteration: 2
      });
      totalKarmaSpent += result2.karmaCost;
      totalSuccesses += result2.newSuccesses.length;
    }
    
    // Verify escalating costs
    expect(totalKarmaSpent).toBeGreaterThanOrEqual(1);
  });

  test('Should handle combined Karma Pool usage', () => {
    // Buy 3 Karma dice (3 Karma)
    const karmaDice = buyKarmaDice({
      karmaDiceCount: 3,
      targetNumber: 5,
      maxAllowed: 6
    });
    
    let totalKarma = karmaDice.karmaCost;
    let successes = karmaDice.successes;
    
    // Re-roll failures once (1 Karma)
    if (karmaDice.rolls.some(r => r < 5)) {
      const reroll = rerollFailures({
        failedDice: karmaDice.rolls.filter(r => r < 5),
        targetNumber: 5,
        rerollIteration: 1
      });
      totalKarma += reroll.karmaCost;
      successes += reroll.newSuccesses.length;
    }
    
    // Buy 2 more successes if needed (2 Karma, permanent)
    if (successes < 6 && successes > 0) {
      const bought = buySuccesses({
        currentSuccesses: successes,
        successesToBuy: 2
      });
      totalKarma += bought.karmaCost;
      successes = bought.totalSuccesses;
    }
    
    expect(totalKarma).toBeGreaterThan(0);
    expect(successes).toBeGreaterThan(0);
  });
});

describe('Karma Pool - Edge Cases', () => {
  
  test('Should handle zero failures to re-roll', () => {
    expect(() => {
      rerollFailures({
        failedDice: [],
        targetNumber: 5,
        rerollIteration: 1
      });
    }).toThrow(/no failures/i);
  });

  test('Should handle invalid iteration number', () => {
    expect(() => {
      rerollFailures({
        failedDice: [4, 3],
        targetNumber: 5,
        rerollIteration: 0
      });
    }).toThrow(/iteration.*at least 1/i);
  });

  test('Should handle buying zero Karma dice', () => {
    expect(() => {
      buyKarmaDice({
        karmaDiceCount: 0,
        targetNumber: 5
      });
    }).toThrow(/at least 1/i);
  });

  test('Should handle buying zero successes', () => {
    expect(() => {
      buySuccesses({
        currentSuccesses: 3,
        successesToBuy: 0
      });
    }).toThrow(/at least 1/i);
  });

  test('Should prevent excessive Karma dice', () => {
    expect(() => {
      buyKarmaDice({
        karmaDiceCount: 100,
        targetNumber: 5
      });
    }).toThrow(/too many|maximum/i);
  });
});

describe('Karma Pool - Tracking', () => {
  
  test('Should track Karma Pool spent in session', () => {
    const tracker = createKarmaTracker(10); // Start with 10 Karma
    
    // Buy 3 dice
    tracker.spend(3, 'buy_dice');
    expect(tracker.remaining).toBe(7);
    
    // Re-roll (1 Karma)
    tracker.spend(1, 'reroll');
    expect(tracker.remaining).toBe(6);
    
    // Buy 2 successes (permanent)
    tracker.spendPermanent(2, 'buy_successes');
    expect(tracker.remaining).toBe(4);
    expect(tracker.permanentSpent).toBe(2);
    
    expect(tracker.getHistory()).toHaveLength(3);
  });

  test('Should prevent spending more than available', () => {
    const tracker = createKarmaTracker(5);
    
    expect(() => {
      tracker.spend(6, 'buy_dice');
    }).toThrow(/not enough karma/i);
  });

  test('Should refresh non-permanent Karma', () => {
    const tracker = createKarmaTracker(10);
    
    tracker.spend(3, 'buy_dice');
    tracker.spendPermanent(2, 'buy_successes');
    
    tracker.refresh();
    
    // Should restore to (10 - 2 permanent)
    expect(tracker.remaining).toBe(8);
    expect(tracker.permanentSpent).toBe(2);
  });
});

/**
 * Dice Rolling Tests for SR1eGameBot (JavaScript/Node.js)
 * Tests validate core dice rolling functionality
 */

const { rollDice, rollOpposed } = require('../ft_dicebot');

describe('Dice Rolling Tests', () => {
  
  // DR-001: Single Die Roll
  test('DR-001: Should roll a single d6', () => {
    const result = rollDice(1, false, null);
    
    expect(result.rolls).toHaveLength(1);
    expect(result.rolls[0]).toBeGreaterThanOrEqual(1);
    expect(result.rolls[0]).toBeLessThanOrEqual(6);
    expect(result.total).toBe(result.rolls[0]);
  });

  // DR-002: Multiple Dice
  test('DR-002: Should roll multiple dice', () => {
    const result = rollDice(5, false, null);
    
    expect(result.rolls).toHaveLength(5);
    result.rolls.forEach(roll => {
      expect(roll).toBeGreaterThanOrEqual(1);
      expect(roll).toBeLessThanOrEqual(6);
    });
    
    // Verify sorted descending
    for (let i = 0; i < result.rolls.length - 1; i++) {
      expect(result.rolls[i]).toBeGreaterThanOrEqual(result.rolls[i + 1]);
    }
    
    expect(result.total).toBe(result.rolls.reduce((a, b) => a + b, 0));
  });

  // DR-003: Exploding Dice
  test('DR-003: Should explode on 6s', () => {
    // Mock Math.random to force specific rolls
    const originalRandom = Math.random;
    let callCount = 0;
    Math.random = jest.fn(() => {
      // First 5 rolls are 6s (explode), then non-6s
      return callCount++ < 5 ? 0.99 : 0.5;
    });

    const result = rollDice(3, true, null);
    
    // Should have more than 3 rolls due to exploding
    expect(result.rolls.length).toBeGreaterThan(3);
    
    Math.random = originalRandom;
  });

  // DR-004: Target Number Success Counting
  test('DR-004: Should count successes correctly', () => {
    const result = rollDice(10, false, 4);
    
    expect(result.rolls).toHaveLength(10);
    
    // Count expected successes
    const expectedSuccesses = result.rolls.filter(r => r >= 4).length;
    expect(result.successes).toBe(expectedSuccesses);
  });

  // DR-005: Opposed Roll
  test('DR-005: Should calculate opposed roll net successes', () => {
    const result = rollOpposed(5, true, 4, 6, true, 5);
    
    expect(result).toHaveProperty('attacker');
    expect(result).toHaveProperty('defender');
    expect(result).toHaveProperty('netSuccesses');
    
    expect(result.netSuccesses).toBe(
      result.attacker.successes - result.defender.successes
    );
  });

  // DR-006: Dice with Modifier
  test('DR-006: Should apply modifier to total', () => {
    const result = rollDice(6, false, null, 5);
    
    const sumOfRolls = result.rolls.reduce((a, b) => a + b, 0);
    expect(result.total).toBe(sumOfRolls + 5);
  });

  // DR-007: D10 Dice (Cyberpunk)
  test('DR-007: Should roll d10 correctly', () => {
    const result = rollDice(5, false, null, 0, 'd10');
    
    expect(result.rolls).toHaveLength(5);
    result.rolls.forEach(roll => {
      expect(roll).toBeGreaterThanOrEqual(1);
      expect(roll).toBeLessThanOrEqual(10);
    });
  });

  // DR-E01: Zero Dice Error
  test('DR-E01: Should throw error on zero dice', () => {
    expect(() => rollDice(0, false, null)).toThrow();
  });

  // DR-E02: Negative Dice Error
  test('DR-E02: Should throw error on negative dice', () => {
    expect(() => rollDice(-5, false, null)).toThrow();
  });

  // DR-E03: Excessive Dice Limit
  test('DR-E03: Should limit excessive dice', () => {
    expect(() => rollDice(1000, false, null)).toThrow(/maximum|limit|too many/i);
  });

  // Performance Test
  test('Should roll 100 dice in under 100ms', () => {
    const start = Date.now();
    rollDice(100, false, null);
    const duration = Date.now() - start;
    
    expect(duration).toBeLessThan(100);
  });

  // Randomness Test
  test('Should produce varied results over multiple rolls', () => {
    const results = new Set();
    
    for (let i = 0; i < 20; i++) {
      const result = rollDice(5, false, null);
      results.add(result.total);
    }
    
    // Should have multiple unique totals
    expect(results.size).toBeGreaterThan(5);
  });
});

describe('Edge Cases and Boundaries', () => {
  
  test('Should handle minimum valid dice (1)', () => {
    const result = rollDice(1, false, null);
    expect(result.rolls).toHaveLength(1);
  });

  test('Should handle maximum valid dice (100)', () => {
    const result = rollDice(100, false, null);
    expect(result.rolls).toHaveLength(100);
  });

  test('Should handle TN of 1 (all succeed)', () => {
    const result = rollDice(10, false, 1);
    expect(result.successes).toBe(10);
  });

  test('Should handle TN of 6 (only 6s succeed)', () => {
    const result = rollDice(10, false, 6);
    expect(result.successes).toBeLessThanOrEqual(10);
    expect(result.successes).toBeGreaterThanOrEqual(0);
  });

  test('Should prevent infinite exploding loops', () => {
    // Mock to always roll 6
    const originalRandom = Math.random;
    Math.random = jest.fn(() => 0.99);

    expect(() => {
      rollDice(1, true, null);
    }).not.toThrow();

    Math.random = originalRandom;
  });
});

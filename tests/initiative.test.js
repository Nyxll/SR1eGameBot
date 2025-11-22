/**
 * Initiative System Tests for SR1eGameBot (JavaScript/Node.js)
 * Tests validate initiative rolling and tracking
 */

const { 
  rollInitiative, 
  trackInitiative, 
  addPlayer, 
  removePlayer 
} = require('../ft_initiative');

describe('Initiative Setup Tests', () => {
  
  // INIT-001: Set GM
  test('INIT-001: Should set GM for initiative tracking', () => {
    const result = setGM('user123', 'channel456', 'gm789');
    
    expect(result.success).toBe(true);
    expect(result.gmId).toBe('gm789');
  });

  // INIT-002: Set Player Initiative Formula
  test('INIT-002: Should save player initiative formula', () => {
    const result = setPlayerFormula('user123', 'channel456', '1d6+4');
    
    expect(result.success).toBe(true);
    expect(result.formula).toMatchObject({
      dice: 1,
      modifier: 4
    });
  });

  // INIT-003: Set Player List (GM)
  test('INIT-003: Should set player list', () => {
    const players = ['player1', 'player2', 'player3'];
    const result = setPlayerList('gm123', 'channel456', players);
    
    expect(result.success).toBe(true);
    expect(result.players).toHaveLength(3);
    expect(result.players).toEqual(players);
  });

  // INIT-004: Add NPCs (GM)
  test('INIT-004: Should add NPCs with formulas', () => {
    const npcs = [
      { label: 'thug1', dice: 1, modifier: 3 },
      { label: 'thug2', dice: 1, modifier: 3 },
      { label: 'boss', dice: 2, modifier: 5 }
    ];
    
    const result = addNPCs('gm123', 'channel456', npcs);
    
    expect(result.success).toBe(true);
    expect(result.npcs).toHaveLength(3);
    expect(result.npcs[0].label).toBe('thug1');
    expect(result.npcs[2].dice).toBe(2);
  });
});

describe('Initiative Rolling Tests', () => {
  
  // INIT-010: Roll SR1e Initiative
  test('INIT-010: Should roll SR1e initiative correctly', () => {
    const characters = [
      { id: 'P1', dice: 1, modifier: 4 },
      { id: 'P2', dice: 1, modifier: 6 },
      { id: 'P3', dice: 1, modifier: 3 },
      { label: 'thug1', dice: 1, modifier: 2 },
      { label: 'thug2', dice: 1, modifier: 2 }
    ];
    
    const result = trackInitiative(characters, 'sr1e');
    
    // All combatants should have rolled
    expect(result.order).toHaveLength(5);
    
    // Should be sorted descending by initiative
    for (let i = 0; i < result.order.length - 1; i++) {
      expect(result.order[i].initiative).toBeGreaterThanOrEqual(
        result.order[i + 1].initiative
      );
    }
    
    // Each should have correct structure
    result.order.forEach(combatant => {
      expect(combatant).toHaveProperty('initiative');
      expect(combatant).toHaveProperty('rolls');
      expect(combatant.initiative).toBeGreaterThanOrEqual(
        combatant.modifier + combatant.rolls.length
      );
    });
  });

  // INIT-011: Roll SR3e Initiative with Multiple Passes
  test('INIT-011: Should handle SR3e multiple passes', () => {
    const characters = [
      { id: 'samurai', dice: 2, modifier: 10 },
      { id: 'mage', dice: 3, modifier: 8 }
    ];
    
    const result = trackInitiative(characters, 'sr3e');
    
    result.order.forEach(combatant => {
      // Should have phases array
      expect(combatant).toHaveProperty('phases');
      expect(Array.isArray(combatant.phases)).toBe(true);
      
      // Phases should be initiative, initiative-10, initiative-20, etc.
      const expectedPhases = [];
      let phase = combatant.initiative;
      while (phase > 0) {
        expectedPhases.push(phase);
        phase -= 10;
      }
      
      expect(combatant.phases).toEqual(expectedPhases);
    });
    
    // Should have phase breakdown
    expect(result).toHaveProperty('phaseOrder');
    expect(Array.isArray(result.phaseOrder)).toBe(true);
  });

  // INIT-012: Roll CP2020 Initiative (d10)
  test('INIT-012: Should use d10 for Cyberpunk 2020', () => {
    const characters = [
      { id: 'solo', dice: 1, modifier: 7 },
      { id: 'netrunner', dice: 1, modifier: 5 }
    ];
    
    const result = trackInitiative(characters, 'cp2020');
    
    result.order.forEach(combatant => {
      // Each roll should be 1-10 (d10)
      combatant.rolls.forEach(roll => {
        expect(roll).toBeGreaterThanOrEqual(1);
        expect(roll).toBeLessThanOrEqual(10);
      });
    });
  });
});

describe('Initiative Management Tests', () => {
  
  // INIT-020: Add Player Mid-Combat
  test('INIT-020: Should add player during initiative', () => {
    const existingInit = {
      order: [
        { id: 'P1', initiative: 15 },
        { id: 'P2', initiative: 12 }
      ]
    };
    
    const newPlayer = { id: 'P3', dice: 1, modifier: 8 };
    const result = addPlayerMidCombat(existingInit, newPlayer);
    
    expect(result.order).toHaveLength(3);
    expect(result.order.some(p => p.id === 'P3')).toBe(true);
    
    // Should still be sorted
    for (let i = 0; i < result.order.length - 1; i++) {
      expect(result.order[i].initiative).toBeGreaterThanOrEqual(
        result.order[i + 1].initiative
      );
    }
  });

  // INIT-021: Remove NPC
  test('INIT-021: Should remove NPC from initiative', () => {
    const existingInit = {
      order: [
        { id: 'P1', initiative: 15 },
        { label: 'thug1', initiative: 12 },
        { label: 'thug2', initiative: 10 }
      ]
    };
    
    const result = removeNPC(existingInit, 'thug1');
    
    expect(result.order).toHaveLength(2);
    expect(result.order.some(c => c.label === 'thug1')).toBe(false);
    expect(result.order.some(c => c.label === 'thug2')).toBe(true);
  });
});

describe('Initiative Tie-Breaking Tests', () => {
  
  test('Should break ties by higher modifier', () => {
    // Mock same initiative value
    const characters = [
      { id: 'P1', dice: 1, modifier: 10, rolls: [7] }, // init 17
      { id: 'P2', dice: 1, modifier: 8, rolls: [9] }   // init 17
    ];
    
    const result = trackInitiative(characters);
    
    // P1 has higher modifier, should come first
    const p1Index = result.order.findIndex(c => c.id === 'P1');
    const p2Index = result.order.findIndex(c => c.id === 'P2');
    
    expect(p1Index).toBeLessThan(p2Index);
  });

  test('Should handle multi-way ties', () => {
    const characters = [
      { id: 'P1', dice: 1, modifier: 10, rolls: [7] }, // init 17
      { id: 'P2', dice: 1, modifier: 8, rolls: [9] },  // init 17
      { id: 'P3', dice: 1, modifier: 6, rolls: [11] }  // init 17
    ];
    
    const result = trackInitiative(characters);
    
    // Should be ordered by modifier: P1 (10), P2 (8), P3 (6)
    expect(result.order[0].id).toBe('P1');
    expect(result.order[1].id).toBe('P2');
    expect(result.order[2].id).toBe('P3');
  });
});

describe('Initiative Edge Cases', () => {
  
  test('Should handle initiative dice never exploding', () => {
    // Even with ! notation, initiative dice don't explode
    const result = rollInitiative('2d6!+10');
    
    // Should have exactly 2 rolls
    expect(result.rolls).toHaveLength(2);
    
    // Each roll should be 1-6
    result.rolls.forEach(roll => {
      expect(roll).toBeGreaterThanOrEqual(1);
      expect(roll).toBeLessThanOrEqual(6);
    });
  });

  test('Should handle zero dice (attribute only)', () => {
    // Some characters may have 0 initiative dice
    const result = rollInitiative('0d6+5');
    
    expect(result.rolls).toHaveLength(0);
    expect(result.initiative).toBe(5);
  });

  test('Should handle negative modifiers', () => {
    const result = rollInitiative('1d6-2');
    
    expect(result.modifier).toBe(-2);
    expect(result.initiative).toBe(result.rolls[0] - 2);
  });

  test('Should prevent initiatives below 0', () => {
    // If roll + modifier < 0, should be 0
    const result = rollInitiative('1d6-10');
    
    if (result.initiative < 0) {
      expect(result.initiative).toBe(0);
    }
  });
});

describe('Phase Calculation Tests', () => {
  
  test('Should calculate correct phases for SR3e', () => {
    const testCases = [
      { init: 25, expected: [25, 15, 5] },
      { init: 19, expected: [19, 9] },
      { init: 8, expected: [] }, // Below 10, no second pass
      { init: 10, expected: [10] }
    ];
    
    testCases.forEach(({ init, expected }) => {
      const phases = calculatePhases(init);
      expect(phases).toEqual(expected);
    });
  });

  test('Should create phase order with all combatants', () => {
    const characters = [
      { id: 'P1', initiative: 19 },
      { id: 'P2', initiative: 17 },
      { id: 'P3', initiative: 8 }
    ];
    
    const phaseOrder = createPhaseOrder(characters);
    
    // Should have phases: 19, 17, 9, 8, 7
    expect(phaseOrder).toContainEqual({ phase: 19, actors: ['P1'] });
    expect(phaseOrder).toContainEqual({ phase: 17, actors: ['P2'] });
    expect(phaseOrder).toContainEqual({ phase: 9, actors: ['P1'] });
    expect(phaseOrder).toContainEqual({ phase: 8, actors: ['P3'] });
    expect(phaseOrder).toContainEqual({ phase: 7, actors: ['P2'] });
  });
});

describe('Performance Tests', () => {
  
  test('Should handle large initiative lists efficiently', () => {
    // Create 50 combatants
    const characters = Array.from({ length: 50 }, (_, i) => ({
      id: `char${i}`,
      dice: 1,
      modifier: Math.floor(Math.random() * 10)
    }));
    
    const start = Date.now();
    const result = trackInitiative(characters);
    const duration = Date.now() - start;
    
    expect(result.order).toHaveLength(50);
    expect(duration).toBeLessThan(100); // Should complete in under 100ms
  });
});

# SR1eGameBot - Test Specification

## Document Information
- **Perspective**: Quality Engineer
- **Date**: November 2025
- **Purpose**: Language-agnostic test specifications for both Node.js and Python implementations

---

## Test Summary

This document defines comprehensive test specifications that validate both the JavaScript/Node.js and Python implementations of SR1eGameBot. All tests are designed to be implementation-agnostic, ensuring feature parity between versions.

**Total Test Cases**: 50+ across 8 feature areas  
**Coverage Target**: 85% minimum, 100% for critical paths

---

## Test Categories

1. **Dice Rolling (DR)**: 15 test cases
2. **Initiative System (INIT)**: 10 test cases
3. **Macro System (MACRO)**: 6 test cases
4. **Scene Management (SCENE)**: 8 test cases
5. **GM Screen (GM)**: 4 test cases
6. **Reminder System (REM)**: 5 test cases
7. **Ammo Tracking (AMMO)**: 6 test cases
8. **Data Persistence (DATA)**: 8 test cases

---

## 1. Dice Rolling Tests (DR)

### DR-001: Single Die Roll
- **Input**: 1d6
- **Expected**: 1 roll, value 1-6, total equals roll
- **Priority**: Critical

### DR-002: Multiple Dice
- **Input**: 5d6
- **Expected**: 5 rolls, all 1-6, sorted descending, total = sum
- **Priority**: Critical

### DR-003: Exploding Dice
- **Input**: 10d6!
- **Expected**: ≥10 rolls, 6s reroll, max 100 iterations
- **Priority**: Critical

### DR-004: Target Number Success
- **Input**: 5d6 tn4
- **Expected**: successes = count(roll ≥ 4)
- **Priority**: Critical

### DR-005: Opposed Roll
- **Input**: 5d6! tn4 vs 6d6! tn5
- **Expected**: net_successes = attacker - defender
- **Priority**: High

### DR-006: Dice with Modifier
- **Input**: 6d6 total +5
- **Expected**: total = sum(rolls) + 5
- **Priority**: Medium

### DR-007: D10 Dice (Cyberpunk)
- **Input**: 5d10
- **Expected**: 5 rolls, all 1-10
- **Priority**: High

### DR-E01: Zero Dice Error
- **Input**: 0d6
- **Expected**: Error/Exception
- **Priority**: High

### DR-E02: Negative Dice Error
- **Input**: -5d6
- **Expected**: Error/Exception
- **Priority**: High

### DR-E03: Excessive Dice Limit
- **Input**: 1000d6
- **Expected**: Error or capped at max (e.g., 100)
- **Priority**: Medium

---

## 2. Initiative System Tests (INIT)

### INIT-001: Set GM
- **Input**: Set GM @User
- **Expected**: GM stored, can manage init
- **Priority**: Critical

### INIT-002: Set Player Formula
- **Input**: Player sets 1d6+4
- **Expected**: Formula stored, persists
- **Priority**: Critical

### INIT-003: Set Player List
- **Input**: GM sets @P1 @P2 @P3
- **Expected**: 3 players stored
- **Priority**: Critical

### INIT-004: Add NPCs
- **Input**: Add 2 thugs (1d6+3), 1 boss (2d6+5)
- **Expected**: 2 NPC entries with correct formulas
- **Priority**: Critical

### INIT-010: Roll SR1e Initiative
- **Input**: Init with 3 players, 2 NPCs
- **Expected**: All rolled, sorted descending
- **Priority**: Critical

### INIT-011: Roll SR3e Initiative
- **Input**: Init3 with multiple passes
- **Expected**: Passes calculated (-10 each), sorted
- **Priority**: High

### INIT-012: Roll CP2020 Initiative
- **Input**: InitCP
- **Expected**: Uses d10, sorted
- **Priority**: Medium

---

## 3. Macro System Tests (MACRO)

### MACRO-001: Save Macro
- **Input**: Save "attack" -> "8! tn4"
- **Expected**: Macro stored, user+channel scoped
- **Priority**: Critical

### MACRO-002: Execute Macro
- **Input**: Run macro "attack"
- **Expected**: Executes "8! tn4"
- **Priority**: Critical

### MACRO-003: List Macros
- **Input**: List command
- **Expected**: Shows all user macros in channel
- **Priority**: High

### MACRO-004: Delete Macro
- **Input**: Delete "attack"
- **Expected**: Macro removed permanently
- **Priority**: High

### MACRO-E01: Duplicate Name Overwrites
- **Input**: Save "attack" twice
- **Expected**: Second overwrites first
- **Priority**: Medium

---

## 4. Scene Management Tests (SCENE)

### SCENE-001: Create Scene
- **Input**: Create "warehouse" with description + music
- **Expected**: Scene stored with all data
- **Priority**: Critical

### SCENE-002: Deploy Scene
- **Input**: Get "warehouse"
- **Expected**: Description shown, music embedded
- **Priority**: Critical

### SCENE-003: List Scenes
- **Input**: List command
- **Expected**: All scene names shown
- **Priority**: High

### SCENE-004: Delete Scene
- **Input**: Delete "warehouse"
- **Expected**: Scene removed permanently
- **Priority**: High

---

## 5. Data Persistence Tests (DATA)

### DATA-001: User Data Isolation
- **Test**: Verify data scoped to server/channel/user
- **Priority**: Critical

### DATA-002: Encrypted Storage
- **Test**: Verify sensitive data encrypted at rest
- **Priority**: Critical

### DATA-003: Cache Consistency
- **Test**: Verify cache invalidation on updates
- **Priority**: High

### DATA-004: Database Reconnection
- **Test**: Verify graceful DB reconnection
- **Priority**: High

---

## Test Data Sets

### Common Test Data (test-data/common.json)
```json
{
  "users": {
    "gm": {"id": "100", "name": "GameMaster"},
    "player1": {"id": "101", "name": "Player1"},
    "player2": {"id": "102", "name": "Player2"}
  },
  "channels": {
    "play": {"id": "200", "name": "combat-channel"},
    "gm": {"id": "201", "name": "gm-channel"}
  },
  "servers": {
    "test": {"id": "300", "name": "test-server"}
  }
}
```

### Dice Test Data (test-data/dice-tests.json)
```json
{
  "DR-001": {
    "input": {"num_dice": 1, "explode": false, "tn": null},
    "validation": {"count": 1, "range": [1, 6]}
  },
  "DR-002": {
    "input": {"num_dice": 5, "explode": false, "tn": null},
    "validation": {"count": 5, "range": [1, 6], "sorted": true}
  }
}
```

---

## Implementation Notes

### For JavaScript/Node.js Tests
- Use **Jest** or **Mocha** + **Chai**
- Mock Discord.js client
- Use test database or mocks
- Seed test data before each suite

### For Python Tests
- Use **pytest**
- Mock discord.py client  
- Use pytest fixtures for setup/teardown
- Parametrize tests for variations

### Both Implementations Must
1. Pass all 50+ test cases
2. Achieve 85%+ code coverage
3. Complete in <60 seconds
4. Run in CI/CD pipeline
5. Generate coverage reports

---

## Test Execution

### Run All Tests
```bash
# JavaScript
npm test

# Python
pytest
```

### Run Specific Suite
```bash
# JavaScript
npm test -- dice

# Python
pytest tests/test_dice.py
```

### Generate Coverage
```bash
# JavaScript
npm run test:coverage

# Python
pytest --cov=src --cov-report=html
```

---

## Success Criteria

✅ All test cases pass  
✅ 85%+ code coverage achieved  
✅ Feature parity between JS and Python  
✅ Performance benchmarks met  
✅ No critical bugs found

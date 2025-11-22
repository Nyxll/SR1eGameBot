# SR1eGameBot Test Suite

This directory contains comprehensive tests for both the JavaScript/Node.js and Python implementations of SR1eGameBot.

## Test Philosophy

These tests are designed to:
1. **Ensure Feature Parity** - Both implementations pass the same tests
2. **Validate Requirements** - All functional requirements are tested
3. **Prevent Regressions** - Catch bugs before deployment
4. **Document Behavior** - Tests serve as executable documentation

## Test Structure

### JavaScript Tests (`*.test.js`)
- Framework: **Jest**
- Location: `tests/*.test.js`
- Run: `npm test`
- Coverage: `npm run test:coverage`

### Python Tests (`sr1egamebot-python/tests/test_*.py`)
- Framework: **pytest**
- Location: `sr1egamebot-python/tests/test_*.py`
- Run: `pytest`
- Coverage: `pytest --cov=src --cov-report=html`

## Running Tests

### JavaScript/Node.js

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- dice.test.js
```

### Python

```bash
# Install dependencies
cd sr1egamebot-python
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_dice.py

# Run specific test
pytest tests/test_dice.py::TestDiceRolling::test_dr001_single_die_roll
```

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Dice Rolling | 100% |
| Initiative System | 95% |
| Macro System | 95% |
| Scene Management | 90% |
| Data Persistence | 90% |
| **Overall** | **85%+** |

## Test Cases

See [TEST_SPECIFICATION.md](../TEST_SPECIFICATION.md) for complete test specifications.

### Dice Rolling (DR)
- DR-001 to DR-007: Core functionality
- DR-E01 to DR-E03: Error handling
- Performance and randomness tests

### Initiative System (INIT)
- INIT-001 to INIT-004: Setup
- INIT-010 to INIT-012: Rolling
- INIT-020 to INIT-021: Management

### Macro System (MACRO)
- MACRO-001 to MACRO-004: CRUD operations
- MACRO-E01: Edge cases

### Scene Management (SCENE)
- SCENE-001 to SCENE-004: CRUD operations
- SCENE-010 to SCENE-012: Content handling

## Writing New Tests

### JavaScript Example

```javascript
describe('New Feature Tests', () => {
  test('Should do something specific', () => {
    const result = newFeature(input);
    
    expect(result).toHaveProperty('expectedField');
    expect(result.value).toBe(expectedValue);
  });
});
```

### Python Example

```python
class TestNewFeature:
    def test_should_do_something_specific(self):
        """Test that new feature works correctly."""
        result = new_feature(input)
        
        assert 'expected_field' in result
        assert result['value'] == expected_value
```

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled daily builds

### CI Requirements
- All tests must pass
- Coverage must be ≥85%
- No security vulnerabilities
- Performance benchmarks met

## Troubleshooting

### JavaScript Tests Failing

```bash
# Clear Jest cache
npm test -- --clearCache

# Update snapshots (if using)
npm test -- -u

# Debug specific test
node --inspect-brk node_modules/.bin/jest tests/dice.test.js
```

### Python Tests Failing

```bash
# Clear pytest cache
pytest --cache-clear

# Verbose output
pytest -vv

# Debug with pdb
pytest --pdb

# Show print statements
pytest -s
```

## Test Data

Test data is stored in:
- `test-data/common.json` - Shared test data
- `test-data/dice-tests.json` - Dice rolling test data
- Mock objects in test files

## Performance Benchmarks

| Operation | Max Time | Current |
|-----------|----------|---------|
| Roll 100 dice | 100ms | ~20ms |
| Database query | 50ms | ~15ms |
| Command parse | 10ms | ~2ms |

## Contributing

When adding new features:
1. Write tests FIRST (TDD)
2. Ensure both JS and Python tests
3. Update TEST_SPECIFICATION.md
4. Verify coverage targets met
5. Run full test suite before PR

## Resources

- [Jest Documentation](https://jestjs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

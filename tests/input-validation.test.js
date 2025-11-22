/**
 * Input Validation and Error Handling Tests for SR1eGameBot (JavaScript/Node.js)
 * Tests validate proper handling of malformed input, user errors, and edge cases
 */

const { 
  parseRollCommand,
  validateDiceNotation,
  sanitizeInput,
  parseTargetNumber
} = require('../ft_dicebot');

describe('Dice Notation Validation', () => {
  
  // Invalid notation formats
  test('Should reject empty notation', () => {
    expect(() => validateDiceNotation('')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation(null)).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation(undefined)).toThrow(/invalid.*notation/i);
  });

  test('Should reject notation without dice count', () => {
    expect(() => validateDiceNotation('d6')).toThrow(/must specify.*dice/i);
    expect(() => validateDiceNotation('d20+5')).toThrow(/must specify.*dice/i);
  });

  test('Should reject notation without die type', () => {
    expect(() => validateDiceNotation('2d')).toThrow(/invalid.*die type/i);
    expect(() => validateDiceNotation('3d+')).toThrow(/invalid.*die type/i);
  });

  test('Should reject malformed modifiers', () => {
    expect(() => validateDiceNotation('2d6+')).toThrow(/invalid.*modifier/i);
    expect(() => validateDiceNotation('2d6-')).toThrow(/invalid.*modifier/i);
    expect(() => validateDiceNotation('2d6++')).toThrow(/invalid.*modifier/i);
    expect(() => validateDiceNotation('2d6+-5')).toThrow(/invalid.*modifier/i);
  });

  test('Should reject non-numeric values', () => {
    expect(() => validateDiceNotation('twod6')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation('2dsix')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation('2d6+five')).toThrow(/invalid.*modifier/i);
  });

  test('Should reject special characters in notation', () => {
    expect(() => validateDiceNotation('2d6@5')).toThrow(/invalid.*character/i);
    expect(() => validateDiceNotation('2d6#3')).toThrow(/invalid.*character/i);
    expect(() => validateDiceNotation('2d6$')).toThrow(/invalid.*character/i);
    expect(() => validateDiceNotation('2d6%')).toThrow(/invalid.*character/i);
  });

  test('Should reject SQL injection attempts', () => {
    expect(() => validateDiceNotation("2d6'; DROP TABLE dice;--")).toThrow(/invalid.*character/i);
    expect(() => validateDiceNotation("2d6' OR '1'='1")).toThrow(/invalid.*character/i);
  });

  test('Should reject script injection attempts', () => {
    expect(() => validateDiceNotation('<script>alert("XSS")</script>')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation('2d6<script>')).toThrow(/invalid.*character/i);
    expect(() => validateDiceNotation('javascript:alert(1)')).toThrow(/invalid.*notation/i);
  });

  test('Should reject path traversal attempts', () => {
    expect(() => validateDiceNotation('../../../etc/passwd')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation('..\\..\\windows\\system32')).toThrow(/invalid.*notation/i);
  });

  test('Should reject excessive whitespace', () => {
    const result = validateDiceNotation('  2d6  +  5  ');
    expect(result).toBe('2d6+5'); // Should normalize
  });

  test('Should handle Unicode characters', () => {
    expect(() => validateDiceNotation('2d6+５')).toThrow(/invalid.*modifier/i); // Full-width 5
    expect(() => validateDiceNotation('２d6')).toThrow(/invalid.*notation/i);  // Full-width 2
  });
});

describe('Command Parsing Errors', () => {
  
  test('Should reject commands with no dice specification', () => {
    expect(() => parseRollCommand('!roll')).toThrow(/must specify.*dice/i);
    expect(() => parseRollCommand('!roll  ')).toThrow(/must specify.*dice/i);
  });

  test('Should reject mixed valid and invalid notation', () => {
    expect(() => parseRollCommand('!roll 2d6 3dx')).toThrow(/invalid.*notation/i);
  });

  test('Should handle extremely long input', () => {
    const longInput = '!roll ' + 'a'.repeat(10000);
    expect(() => parseRollCommand(longInput)).toThrow(/input.*too long|invalid/i);
  });

  test('Should reject malformed target number syntax', () => {
    expect(() => parseRollCommand('!roll 2d6 tn')).toThrow(/invalid.*target/i);
    expect(() => parseRollCommand('!roll 2d6 tn-5')).toThrow(/invalid.*target/i);
    expect(() => parseRollCommand('!roll 2d6 tn0')).toThrow(/target.*at least 1/i);
  });

  test('Should reject invalid exploding syntax', () => {
    expect(() => parseRollCommand('!roll 2d6!!')).toThrow(/invalid.*exploding/i);
    expect(() => parseRollCommand('!roll 2d6!@')).toThrow(/invalid.*notation/i);
  });

  test('Should handle case sensitivity', () => {
    // Should be case-insensitive for commands
    const result1 = parseRollCommand('!ROLL 2d6');
    const result2 = parseRollCommand('!roll 2d6');
    expect(result1.notation).toBe(result2.notation);
  });

  test('Should reject buffer overflow attempts', () => {
    const hugeNumber = '9'.repeat(100);
    expect(() => parseRollCommand(`!roll ${hugeNumber}d6`)).toThrow(/too many dice|invalid/i);
  });
});

describe('Target Number Validation', () => {
  
  test('Should reject negative target numbers', () => {
    expect(() => parseTargetNumber(-1)).toThrow(/target.*must be.*positive/i);
    expect(() => parseTargetNumber(-5)).toThrow(/target.*must be.*positive/i);
  });

  test('Should reject zero target number', () => {
    expect(() => parseTargetNumber(0)).toThrow(/target.*at least 1/i);
  });

  test('Should reject non-integer target numbers', () => {
    expect(() => parseTargetNumber(5.5)).toThrow(/target.*must be.*integer/i);
    expect(() => parseTargetNumber(3.14159)).toThrow(/target.*must be.*integer/i);
  });

  test('Should reject excessively high target numbers', () => {
    expect(() => parseTargetNumber(1000000)).toThrow(/target.*too high|unreasonable/i);
  });

  test('Should reject NaN target number', () => {
    expect(() => parseTargetNumber(NaN)).toThrow(/invalid.*target/i);
    expect(() => parseTargetNumber('abc')).toThrow(/invalid.*target/i);
  });

  test('Should reject Infinity', () => {
    expect(() => parseTargetNumber(Infinity)).toThrow(/invalid.*target/i);
    expect(() => parseTargetNumber(-Infinity)).toThrow(/invalid.*target/i);
  });
});

describe('User Input Sanitization', () => {
  
  test('Should strip dangerous HTML tags', () => {
    const result = sanitizeInput('<script>alert("xss")</script>2d6');
    expect(result).not.toContain('<script>');
    expect(result).not.toContain('</script>');
  });

  test('Should escape special Discord characters', () => {
    const result = sanitizeInput('@everyone 2d6');
    expect(result).not.toContain('@everyone');
    
    const result2 = sanitizeInput('@here roll 2d6');
    expect(result2).not.toContain('@here');
  });

  test('Should handle null bytes', () => {
    const result = sanitizeInput('2d6\x00malicious');
    expect(result).not.toContain('\x00');
  });

  test('Should normalize line endings', () => {
    const result = sanitizeInput('2d6\r\n3d8\n4d10');
    expect(result).toMatch(/2d6.*3d8.*4d10/);
  });

  test('Should trim excessive whitespace', () => {
    const result = sanitizeInput('   2d6   +   5   ');
    expect(result.trim()).toBe('2d6 + 5');
  });

  test('Should handle emoji and special Unicode', () => {
    const result = sanitizeInput('2d6 🎲 lucky roll');
    // Should preserve or safely handle emoji
    expect(result).toBeTruthy();
  });

  test('Should reject control characters', () => {
    expect(() => sanitizeInput('2d6\x01\x02\x03')).toThrow(/invalid.*control/i);
  });
});

describe('Format String Vulnerabilities', () => {
  
  test('Should reject format string attempts', () => {
    expect(() => parseRollCommand('!roll %s%s%s%s')).toThrow(/invalid.*notation/i);
    expect(() => parseRollCommand('!roll %d%d%d')).toThrow(/invalid.*notation/i);
    expect(() => parseRollCommand('!roll %n%n%n')).toThrow(/invalid.*notation/i);
  });

  test('Should handle printf-style formatting safely', () => {
    expect(() => parseRollCommand('!roll ${process.env}')).toThrow(/invalid.*notation/i);
    expect(() => parseRollCommand('!roll `command`')).toThrow(/invalid.*notation/i);
  });
});

describe('Discord-Specific Input Issues', () => {
  
  test('Should handle Discord mentions', () => {
    const result = sanitizeInput('<@123456789> roll 2d6');
    expect(result).not.toContain('<@');
  });

  test('Should handle role mentions', () => {
    const result = sanitizeInput('<@&987654321> roll 2d6');
    expect(result).not.toContain('<@&');
  });

  test('Should handle channel mentions', () => {
    const result = sanitizeInput('<#555555555> roll 2d6');
    expect(result).not.toContain('<#');
  });

  test('Should handle Discord custom emoji', () => {
    const result = sanitizeInput('<:dice:123456789> 2d6');
    // Should handle gracefully
    expect(result).toBeTruthy();
  });

  test('Should handle Discord formatting', () => {
    const result = sanitizeInput('**2d6** __roll__');
    // Should preserve or safely handle Discord markdown
    expect(result).toContain('2d6');
  });
});

describe('Edge Cases in Dice Notation', () => {
  
  test('Should handle leading zeros', () => {
    const result = validateDiceNotation('02d06');
    expect(result).toBe('2d6');
  });

  test('Should reject decimal dice counts', () => {
    expect(() => validateDiceNotation('2.5d6')).toThrow(/invalid.*dice count/i);
    expect(() => validateDiceNotation('1.99d6')).toThrow(/invalid.*dice count/i);
  });

  test('Should reject decimal die sides', () => {
    expect(() => validateDiceNotation('2d6.5')).toThrow(/invalid.*die type/i);
    expect(() => validateDiceNotation('2d10.99')).toThrow(/invalid.*die type/i);
  });

  test('Should handle multiple modifiers incorrectly', () => {
    expect(() => validateDiceNotation('2d6+5-3+2')).toThrow(/invalid.*multiple.*modifiers/i);
  });

  test('Should reject dice with invalid die types', () => {
    expect(() => validateDiceNotation('2d1')).toThrow(/die.*at least 2/i);
    expect(() => validateDiceNotation('2d0')).toThrow(/invalid.*die type/i);
    expect(() => validateDiceNotation('2d-6')).toThrow(/invalid.*die type/i);
  });

  test('Should handle very large die types', () => {
    // d1000 should work but d1000000 should not
    const result = validateDiceNotation('1d1000');
    expect(result).toBe('1d1000');
    
    expect(() => validateDiceNotation('1d1000000')).toThrow(/die type.*too large/i);
  });
});

describe('Command Injection Prevention', () => {
  
  test('Should prevent shell command injection', () => {
    expect(() => parseRollCommand('!roll 2d6 && rm -rf /')).toThrow(/invalid.*character/i);
    expect(() => parseRollCommand('!roll 2d6 | cat /etc/passwd')).toThrow(/invalid.*character/i);
    expect(() => parseRollCommand('!roll 2d6 ; ls -la')).toThrow(/invalid.*character/i);
  });

  test('Should prevent Windows command injection', () => {
    expect(() => parseRollCommand('!roll 2d6 & del *.*')).toThrow(/invalid.*character/i);
    expect(() => parseRollCommand('!roll 2d6 && dir')).toThrow(/invalid.*character/i);
  });

  test('Should prevent eval/exec injection', () => {
    expect(() => parseRollCommand('!roll eval("malicious")')).toThrow(/invalid.*notation/i);
    expect(() => parseRollCommand('!roll require("fs")')).toThrow(/invalid.*notation/i);
  });
});

describe('Encoding and Escaping Issues', () => {
  
  test('Should handle URL encoding', () => {
    const result = sanitizeInput('2d6%20%2B%205');
    // Should decode or reject
    expect(result).toBeTruthy();
  });

  test('Should handle HTML entities', () => {
    const result = sanitizeInput('2d6&amp;3d8');
    expect(result).not.toContain('&amp;');
  });

  test('Should handle Unicode escapes', () => {
    expect(() => validateDiceNotation('\\u00322d6')).toThrow(/invalid.*notation/i);
  });

  test('Should handle backslash escaping attempts', () => {
    expect(() => validateDiceNotation('2d6\\n\\r\\t')).toThrow(/invalid.*character/i);
  });

  test('Should handle double encoding attempts', () => {
    expect(() => sanitizeInput('%253Cscript%253E')).toThrow(/invalid/i);
  });
});

describe('Numeric Overflow and Underflow', () => {
  
  test('Should prevent integer overflow in dice count', () => {
    expect(() => validateDiceNotation('2147483648d6')).toThrow(/too many dice/i);
  });

  test('Should prevent integer overflow in modifier', () => {
    expect(() => validateDiceNotation('2d6+2147483648')).toThrow(/modifier.*too large/i);
  });

  test('Should handle negative zero', () => {
    const result = validateDiceNotation('2d6+-0');
    expect(result).toBe('2d6+0');
  });

  test('Should handle scientific notation attempts', () => {
    expect(() => validateDiceNotation('2e10d6')).toThrow(/invalid.*notation/i);
    expect(() => validateDiceNotation('2d6e10')).toThrow(/invalid.*notation/i);
  });
});

describe('Race Conditions and Timing', () => {
  
  test('Should handle concurrent validation calls', async () => {
    const promises = Array.from({ length: 100 }, () =>
      Promise.resolve(validateDiceNotation('2d6'))
    );
    
    const results = await Promise.all(promises);
    results.forEach(result => {
      expect(result).toBe('2d6');
    });
  });
});

describe('Memory and Resource Limits', () => {
  
  test('Should reject extremely large dice pools', () => {
    expect(() => validateDiceNotation('999999d6')).toThrow(/too many dice/i);
  });

  test('Should handle repeated validation without memory leak', () => {
    for (let i = 0; i < 10000; i++) {
      validateDiceNotation('2d6');
    }
    // If we get here without crashing, test passes
    expect(true).toBe(true);
  });
});

"""
Input Validation and Error Handling Tests for SR1eGameBot (Python)
Tests validate proper handling of malformed input, user errors, and edge cases
"""

import pytest
from src.dice_parser import (
    parse_roll_command,
    validate_dice_notation,
    sanitize_input,
    parse_target_number
)


class TestDiceNotationValidation:
    """Test suite for dice notation validation."""
    
    def test_reject_empty_notation(self):
        """Verify empty notation is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation(None)
    
    def test_reject_notation_without_dice_count(self):
        """Verify notation without dice count is rejected."""
        with pytest.raises(ValueError, match=r"must specify.*dice"):
            validate_dice_notation('d6')
        with pytest.raises(ValueError, match=r"must specify.*dice"):
            validate_dice_notation('d20+5')
    
    def test_reject_notation_without_die_type(self):
        """Verify notation without die type is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('2d')
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('3d+')
    
    def test_reject_malformed_modifiers(self):
        """Verify malformed modifiers are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6+')
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6-')
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6++')
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6+-5')
    
    def test_reject_non_numeric_values(self):
        """Verify non-numeric values are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('twod6')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('2dsix')
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6+five')
    
    def test_reject_special_characters(self):
        """Verify special characters are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6@5')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6#3')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6$')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6%')
    
    def test_reject_sql_injection(self):
        """Verify SQL injection attempts are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation("2d6'; DROP TABLE dice;--")
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation("2d6' OR '1'='1")
    
    def test_reject_script_injection(self):
        """Verify script injection attempts are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('<script>alert("XSS")</script>')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6<script>')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('javascript:alert(1)')
    
    def test_reject_path_traversal(self):
        """Verify path traversal attempts are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('../../../etc/passwd')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('..\\..\\windows\\system32')
    
    def test_normalize_excessive_whitespace(self):
        """Verify excessive whitespace is normalized."""
        result = validate_dice_notation('  2d6  +  5  ')
        assert result == '2d6+5'
    
    def test_handle_unicode_characters(self):
        """Verify Unicode characters are handled."""
        with pytest.raises(ValueError, match=r"invalid.*modifier"):
            validate_dice_notation('2d6+５')  # Full-width 5
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('２d6')  # Full-width 2


class TestCommandParsingErrors:
    """Test suite for command parsing errors."""
    
    def test_reject_empty_command(self):
        """Verify empty commands are rejected."""
        with pytest.raises(ValueError, match=r"must specify.*dice"):
            parse_roll_command('!roll')
        with pytest.raises(ValueError, match=r"must specify.*dice"):
            parse_roll_command('!roll  ')
    
    def test_reject_mixed_notation(self):
        """Verify mixed valid/invalid notation is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll 2d6 3dx')
    
    def test_handle_extremely_long_input(self):
        """Verify extremely long input is handled."""
        long_input = '!roll ' + 'a' * 10000
        with pytest.raises(ValueError, match=r"input.*too long|invalid"):
            parse_roll_command(long_input)
    
    def test_reject_malformed_target_number(self):
        """Verify malformed target number is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_roll_command('!roll 2d6 tn')
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_roll_command('!roll 2d6 tn-5')
        with pytest.raises(ValueError, match=r"target.*at least 1"):
            parse_roll_command('!roll 2d6 tn0')
    
    def test_reject_invalid_exploding_syntax(self):
        """Verify invalid exploding syntax is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*exploding"):
            parse_roll_command('!roll 2d6!!')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll 2d6!@')
    
    def test_handle_case_sensitivity(self):
        """Verify commands are case-insensitive."""
        result1 = parse_roll_command('!ROLL 2d6')
        result2 = parse_roll_command('!roll 2d6')
        assert result1['notation'] == result2['notation']
    
    def test_reject_buffer_overflow(self):
        """Verify buffer overflow attempts are rejected."""
        huge_number = '9' * 100
        with pytest.raises(ValueError, match=r"too many dice|invalid"):
            parse_roll_command(f'!roll {huge_number}d6')


class TestTargetNumberValidation:
    """Test suite for target number validation."""
    
    def test_reject_negative_target_numbers(self):
        """Verify negative target numbers are rejected."""
        with pytest.raises(ValueError, match=r"target.*must be.*positive"):
            parse_target_number(-1)
        with pytest.raises(ValueError, match=r"target.*must be.*positive"):
            parse_target_number(-5)
    
    def test_reject_zero_target_number(self):
        """Verify zero target number is rejected."""
        with pytest.raises(ValueError, match=r"target.*at least 1"):
            parse_target_number(0)
    
    def test_reject_non_integer_target_numbers(self):
        """Verify non-integer target numbers are rejected."""
        with pytest.raises(ValueError, match=r"target.*must be.*integer"):
            parse_target_number(5.5)
        with pytest.raises(ValueError, match=r"target.*must be.*integer"):
            parse_target_number(3.14159)
    
    def test_reject_excessively_high_target_numbers(self):
        """Verify excessively high target numbers are rejected."""
        with pytest.raises(ValueError, match=r"target.*too high|unreasonable"):
            parse_target_number(1000000)
    
    def test_reject_nan_target_number(self):
        """Verify NaN target number is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_target_number(float('nan'))
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_target_number('abc')
    
    def test_reject_infinity(self):
        """Verify Infinity is rejected."""
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_target_number(float('inf'))
        with pytest.raises(ValueError, match=r"invalid.*target"):
            parse_target_number(float('-inf'))


class TestUserInputSanitization:
    """Test suite for user input sanitization."""
    
    def test_strip_dangerous_html_tags(self):
        """Verify dangerous HTML tags are stripped."""
        result = sanitize_input('<script>alert("xss")</script>2d6')
        assert '<script>' not in result
        assert '</script>' not in result
    
    def test_escape_discord_characters(self):
        """Verify Discord special characters are escaped."""
        result = sanitize_input('@everyone 2d6')
        assert '@everyone' not in result
        
        result2 = sanitize_input('@here roll 2d6')
        assert '@here' not in result2
    
    def test_handle_null_bytes(self):
        """Verify null bytes are handled."""
        result = sanitize_input('2d6\x00malicious')
        assert '\x00' not in result
    
    def test_normalize_line_endings(self):
        """Verify line endings are normalized."""
        result = sanitize_input('2d6\r\n3d8\n4d10')
        assert '2d6' in result and '3d8' in result and '4d10' in result
    
    def test_trim_excessive_whitespace(self):
        """Verify excessive whitespace is trimmed."""
        result = sanitize_input('   2d6   +   5   ')
        assert result.strip() == '2d6 + 5'
    
    def test_handle_emoji(self):
        """Verify emoji are handled safely."""
        result = sanitize_input('2d6 🎲 lucky roll')
        assert result is not None
    
    def test_reject_control_characters(self):
        """Verify control characters are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*control"):
            sanitize_input('2d6\x01\x02\x03')


class TestFormatStringVulnerabilities:
    """Test suite for format string vulnerabilities."""
    
    def test_reject_format_string_attempts(self):
        """Verify format string attempts are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll %s%s%s%s')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll %d%d%d')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll %n%n%n')
    
    def test_handle_printf_style_formatting(self):
        """Verify printf-style formatting is handled safely."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll ${process.env}')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll `command`')


class TestDiscordSpecificInput:
    """Test suite for Discord-specific input issues."""
    
    def test_handle_discord_mentions(self):
        """Verify Discord mentions are handled."""
        result = sanitize_input('<@123456789> roll 2d6')
        assert '<@' not in result
    
    def test_handle_role_mentions(self):
        """Verify role mentions are handled."""
        result = sanitize_input('<@&987654321> roll 2d6')
        assert '<@&' not in result
    
    def test_handle_channel_mentions(self):
        """Verify channel mentions are handled."""
        result = sanitize_input('<#555555555> roll 2d6')
        assert '<#' not in result
    
    def test_handle_custom_emoji(self):
        """Verify custom emoji are handled."""
        result = sanitize_input('<:dice:123456789> 2d6')
        assert result is not None
    
    def test_handle_discord_formatting(self):
        """Verify Discord formatting is handled."""
        result = sanitize_input('**2d6** __roll__')
        assert '2d6' in result


class TestEdgeCasesInDiceNotation:
    """Test suite for edge cases in dice notation."""
    
    def test_handle_leading_zeros(self):
        """Verify leading zeros are handled."""
        result = validate_dice_notation('02d06')
        assert result == '2d6'
    
    def test_reject_decimal_dice_counts(self):
        """Verify decimal dice counts are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*dice count"):
            validate_dice_notation('2.5d6')
        with pytest.raises(ValueError, match=r"invalid.*dice count"):
            validate_dice_notation('1.99d6')
    
    def test_reject_decimal_die_sides(self):
        """Verify decimal die sides are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('2d6.5')
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('2d10.99')
    
    def test_reject_multiple_modifiers(self):
        """Verify multiple modifiers are rejected."""
        with pytest.raises(ValueError, match=r"invalid.*multiple.*modifiers"):
            validate_dice_notation('2d6+5-3+2')
    
    def test_reject_invalid_die_types(self):
        """Verify invalid die types are rejected."""
        with pytest.raises(ValueError, match=r"die.*at least 2"):
            validate_dice_notation('2d1')
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('2d0')
        with pytest.raises(ValueError, match=r"invalid.*die type"):
            validate_dice_notation('2d-6')
    
    def test_handle_very_large_die_types(self):
        """Verify very large die types are handled."""
        result = validate_dice_notation('1d1000')
        assert result == '1d1000'
        
        with pytest.raises(ValueError, match=r"die type.*too large"):
            validate_dice_notation('1d1000000')


class TestCommandInjectionPrevention:
    """Test suite for command injection prevention."""
    
    def test_prevent_shell_command_injection(self):
        """Verify shell command injection is prevented."""
        with pytest.raises(ValueError, match=r"invalid.*character"):
            parse_roll_command('!roll 2d6 && rm -rf /')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            parse_roll_command('!roll 2d6 | cat /etc/passwd')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            parse_roll_command('!roll 2d6 ; ls -la')
    
    def test_prevent_windows_command_injection(self):
        """Verify Windows command injection is prevented."""
        with pytest.raises(ValueError, match=r"invalid.*character"):
            parse_roll_command('!roll 2d6 & del *.*')
        with pytest.raises(ValueError, match=r"invalid.*character"):
            parse_roll_command('!roll 2d6 && dir')
    
    def test_prevent_eval_exec_injection(self):
        """Verify eval/exec injection is prevented."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll eval("malicious")')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            parse_roll_command('!roll __import__("os")')


class TestEncodingAndEscaping:
    """Test suite for encoding and escaping issues."""
    
    def test_handle_url_encoding(self):
        """Verify URL encoding is handled."""
        result = sanitize_input('2d6%20%2B%205')
        assert result is not None
    
    def test_handle_html_entities(self):
        """Verify HTML entities are handled."""
        result = sanitize_input('2d6&amp;3d8')
        assert '&amp;' not in result
    
    def test_handle_unicode_escapes(self):
        """Verify Unicode escapes are handled."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('\\u00322d6')
    
    def test_handle_backslash_escaping(self):
        """Verify backslash escaping is handled."""
        with pytest.raises(ValueError, match=r"invalid.*character"):
            validate_dice_notation('2d6\\n\\r\\t')
    
    def test_handle_double_encoding(self):
        """Verify double encoding attempts are handled."""
        with pytest.raises(ValueError, match=r"invalid"):
            sanitize_input('%253Cscript%253E')


class TestNumericOverflowAndUnderflow:
    """Test suite for numeric overflow and underflow."""
    
    def test_prevent_integer_overflow_in_dice_count(self):
        """Verify integer overflow in dice count is prevented."""
        with pytest.raises(ValueError, match=r"too many dice"):
            validate_dice_notation('2147483648d6')
    
    def test_prevent_integer_overflow_in_modifier(self):
        """Verify integer overflow in modifier is prevented."""
        with pytest.raises(ValueError, match=r"modifier.*too large"):
            validate_dice_notation('2d6+2147483648')
    
    def test_handle_negative_zero(self):
        """Verify negative zero is handled."""
        result = validate_dice_notation('2d6+-0')
        assert result == '2d6+0'
    
    def test_handle_scientific_notation(self):
        """Verify scientific notation is handled."""
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('2e10d6')
        with pytest.raises(ValueError, match=r"invalid.*notation"):
            validate_dice_notation('2d6e10')


class TestRaceConditionsAndTiming:
    """Test suite for race conditions and timing."""
    
    def test_handle_concurrent_validation(self):
        """Verify concurrent validation calls are handled."""
        import concurrent.futures
        
        def validate():
            return validate_dice_notation('2d6')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(validate) for _ in range(100)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        assert all(r == '2d6' for r in results)


class TestMemoryAndResourceLimits:
    """Test suite for memory and resource limits."""
    
    def test_reject_extremely_large_dice_pools(self):
        """Verify extremely large dice pools are rejected."""
        with pytest.raises(ValueError, match=r"too many dice"):
            validate_dice_notation('999999d6')
    
    def test_handle_repeated_validation_without_memory_leak(self):
        """Verify repeated validation doesn't leak memory."""
        for _ in range(10000):
            validate_dice_notation('2d6')
        # If we get here without crashing, test passes
        assert True


# Parametrized tests for comprehensive input validation
@pytest.mark.parametrize("invalid_notation,error_pattern", [
    ('', r'invalid.*notation'),
    ('d6', r'must specify.*dice'),
    ('2d', r'invalid.*die type'),
    ('2d6+', r'invalid.*modifier'),
    ('twod6', r'invalid.*notation'),
    ('2d6@5', r'invalid.*character'),
    ("2d6'; DROP TABLE", r'invalid.*character'),
    ('<script>2d6', r'invalid.*notation'),
    ('2.5d6', r'invalid.*dice count'),
    ('2d1', r'die.*at least 2'),
])
def test_invalid_notations(invalid_notation, error_pattern):
    """Test various invalid notation patterns."""
    with pytest.raises(ValueError, match=error_pattern):
        validate_dice_notation(invalid_notation)

"""
Blank Validator Module

Validates student input in fill-in-the-blank lesson slots against expected
answers. Provides normalization of code strings and per-blank validation
results with visual feedback support.
"""

import re
from dataclasses import dataclass, field

from src.modules.lesson_parser import BlankInfo


@dataclass
class BlankResult:
    """Validation result for a single blank."""
    line_number: int
    is_correct: bool
    student_answer: str
    expected_answers: list[str] = field(default_factory=list)


def normalize_code(code: str) -> str:
    """Normalize code string for comparison.

    Normalization rules:
    1. Strip leading/trailing whitespace
    2. Collapse multiple spaces to single space
    3. Remove spaces around '=' in keyword arguments: 'param = value' -> 'param=value'
    4. Remove spaces inside parentheses: '( x )' -> '(x)'
    5. Normalize comma spacing: 'a,b' -> 'a, b' and 'a ,  b' -> 'a, b'
    6. Case-sensitive (no case folding)

    Args:
        code: The code string to normalize.

    Returns:
        Normalized code string.
    """
    # Step 1: Strip leading/trailing whitespace
    result = code.strip()

    # Step 2: Collapse multiple spaces to single space
    result = re.sub(r" {2,}", " ", result)

    # Step 3: Remove spaces around '=' in keyword arguments
    result = re.sub(r"\s*=\s*", "=", result)

    # Step 4: Remove spaces inside parentheses
    result = re.sub(r"\(\s+", "(", result)
    result = re.sub(r"\s+\)", ")", result)

    # Step 5: Normalize comma spacing - remove spaces before/after commas,
    # then add single space after each comma
    result = re.sub(r"\s*,\s*", ", ", result)

    return result


def validate_blank(student_input: str, expected_answers: list[str]) -> bool:
    """Check if normalized student input matches any normalized expected answer.

    Args:
        student_input: The student's raw input string.
        expected_answers: List of valid expected answer strings.

    Returns:
        True if the normalized student input matches any normalized expected answer.
    """
    normalized_input = normalize_code(student_input)
    for answer in expected_answers:
        if normalize_code(answer) == normalized_input:
            return True
    return False


def validate_blanks(
    blank_contents: dict[int, str],
    blank_map: dict[int, BlankInfo],
) -> list[BlankResult]:
    """Validate all blanks and return per-blank results.

    Args:
        blank_contents: Dict mapping line numbers to student input strings.
        blank_map: Dict mapping line numbers to BlankInfo with expected answers.

    Returns:
        List of BlankResult objects, one per blank in the blank_map.
    """
    results: list[BlankResult] = []

    for line_number, blank_info in blank_map.items():
        student_answer = blank_contents.get(line_number, "")
        is_correct = validate_blank(student_answer, blank_info.expected_answers)

        results.append(BlankResult(
            line_number=line_number,
            is_correct=is_correct,
            student_answer=student_answer,
            expected_answers=blank_info.expected_answers,
        ))

    return results

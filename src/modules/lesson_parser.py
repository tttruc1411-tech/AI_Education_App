"""
Lesson Parser Module

Parses lesson step files containing # __BLANK__ markers and produces
display-ready content with blank slot metadata for the fill-in-the-blank
lesson system.
"""

from dataclasses import dataclass, field
from pathlib import Path


BLANK_MARKER = "# __BLANK__"


@dataclass
class BlankInfo:
    """Metadata for a single blank slot."""
    line_number: int            # 0-based line index in display code
    indentation: str            # Leading whitespace preserved from marker line
    expected_answers: list[str] = field(default_factory=list)  # One or more valid answers


@dataclass
class ParsedStep:
    """Result of parsing a step file."""
    display_lines: list[str] = field(default_factory=list)    # Lines shown in editor
    blank_map: dict[int, BlankInfo] = field(default_factory=dict)  # line_number → BlankInfo
    is_challenge: bool = False   # True if no blanks found (free-form mode)
    raw_content: str = ""        # Original file content for challenge fallback


def _parse_blank_line(line: str, line_number: int) -> "BlankInfo | None":
    """Extract BlankInfo from a single line if it contains BLANK_MARKER.

    Args:
        line: A single line from the step file (without trailing newline).
        line_number: The 0-based line index.

    Returns:
        BlankInfo if the line contains a blank marker, None otherwise.
    """
    stripped = line.lstrip()
    if not stripped.startswith(BLANK_MARKER):
        return None

    # Preserve original indentation (leading whitespace before the marker)
    indentation = line[: len(line) - len(stripped)]

    # Extract the answer portion after "# __BLANK__"
    marker_end = stripped[len(BLANK_MARKER):]

    # Remove the leading space after the marker if present
    if marker_end.startswith(" "):
        answer_text = marker_end[1:]
    else:
        answer_text = marker_end

    # Parse pipe-separated alternatives
    if answer_text:
        expected_answers = [ans.strip() for ans in answer_text.split("|")]
    else:
        expected_answers = [""]

    return BlankInfo(
        line_number=line_number,
        indentation=indentation,
        expected_answers=expected_answers,
    )


def parse_step_file(file_path: str) -> ParsedStep:
    """Parse a step file, extract blank markers, return display-ready content.

    Reads the file, scans each line for the # __BLANK__ prefix, and builds
    a ParsedStep with display lines (blanks replaced with indentation-only
    empty lines), a blank_map of line metadata, and challenge detection.

    Args:
        file_path: Path to the step file to parse.

    Returns:
        ParsedStep with display_lines, blank_map, is_challenge, and raw_content.
    """
    path = Path(file_path)
    raw_content = path.read_text(encoding="utf-8", errors="replace")

    lines = raw_content.splitlines()
    display_lines: list[str] = []
    blank_map: dict[int, BlankInfo] = {}

    for line_number, line in enumerate(lines):
        blank_info = _parse_blank_line(line, line_number)
        if blank_info is not None:
            # Replace blank marker line with indentation-only empty line
            display_lines.append(blank_info.indentation)
            blank_map[line_number] = blank_info
        else:
            display_lines.append(line)

    is_challenge = len(blank_map) == 0

    return ParsedStep(
        display_lines=display_lines,
        blank_map=blank_map,
        is_challenge=is_challenge,
        raw_content=raw_content,
    )

"""SSE parsing utilities."""

import json


def parse_sse_line(line: str) -> tuple[str | None, str | None]:
    """Parse a single SSE line.

    Args:
        line: SSE line to parse

    Returns:
        Tuple of (field, value) or (None, None) if not a valid SSE line

    SSE Format:
        field: value
        :comment
        (empty line)
    """
    line = line.strip()

    # Skip empty lines
    if not line:
        return None, None

    # Skip comments
    if line.startswith(":"):
        return "comment", line[1:].lstrip()

    # Parse field:value
    if ":" in line:
        field, _, value = line.partition(":")
        return field, value.lstrip()

    return None, None


def parse_sse_data(data: str) -> dict:
    """Parse SSE data field as JSON.

    Args:
        data: Data string (should be JSON)

    Returns:
        Parsed dictionary or {"text": data} if not valid JSON
    """
    try:
        parsed: dict = json.loads(data)
        return parsed
    except json.JSONDecodeError:
        return {"text": data}

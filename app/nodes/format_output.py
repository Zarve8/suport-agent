"""Format the final graph result as titled response sections."""

import re

from app.context import TicketState


def format_output(state: TicketState) -> dict[str, object]:
    """Convert draft text into a list of `{title, text}` sections."""
    draft = state.get("draft_reply", "I could not prepare a response.").strip()
    sections: list[dict[str, str]] = []
    current_title = "Response"
    current_lines: list[str] = []
    for line in draft.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if heading:
            if current_lines:
                sections.append({"title": current_title, "text": " ".join(current_lines).strip()})
                current_lines = []
            current_title = heading.group(1).strip()
        elif line.strip():
            current_lines.append(line.strip().lstrip("- "))
    if current_lines or not sections:
        sections.append({"title": current_title, "text": " ".join(current_lines).strip()})
    return {"output_sections": sections}

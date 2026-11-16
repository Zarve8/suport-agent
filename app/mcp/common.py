"""Shared logging helper for local MCP stubs."""

import logging


def log_stub_call(name: str, **details: object) -> None:
    """Log a local MCP stub call.

    Called by every temporary MCP adapter. In production this helper is not a
    replacement for the remote service; the adapter must make an authenticated
    MCP/tool call to the corresponding system and log only safe audit metadata.
    """
    logging.getLogger(f"mcp.{name}").info("stub call details=%s", details)

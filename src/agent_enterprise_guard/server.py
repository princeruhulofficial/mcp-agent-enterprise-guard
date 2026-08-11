"""MCP server entry point for Agent Enterprise Guard."""

from __future__ import annotations

import logging
from os import getenv

from fastmcp import FastMCP

from .tools import (
    detect_silent_failures,
    evaluate_permission,
    generate_audit_report,
    score_agent_reliability,
)

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=getenv("LOG_LEVEL", "INFO"),
)
logger = logging.getLogger("agent-enterprise-guard")

mcp = FastMCP(
    name="mcp-agent-enterprise-guard",
    instructions=(
        "Pure-computation MCP server that scores AI agent reliability, "
        "detects silent failures, evaluates permission policies, and generates "
        "audit reports. All processing is local — no external APIs."
    ),
)


@mcp.tool()
def score_agent_reliability_tool(
    logs: list[dict],
    weights: dict | None = None,
) -> dict:
    """Compute overall reliability score (0-100) from tool-call logs.

    Each log entry should contain: tool_name, success (bool), latency_ms (number),
    is_error (bool), content (string or null).
    """
    return score_agent_reliability(logs, weights)


@mcp.tool()
def detect_silent_failures_tool(logs: list[dict]) -> dict:
    """Flag tool calls that returned empty or null content without an error flag."""
    return detect_silent_failures(logs)


@mcp.tool()
def evaluate_permission_tool(
    action: dict,
    policy_rules: list[dict],
) -> dict:
    """Evaluate whether an agent action is allowed under the given policy rules.

    Returns decision (allow/deny), matched rules, and risk score.
    """
    return evaluate_permission(action, policy_rules)


@mcp.tool()
def generate_audit_report_tool(
    logs: list[dict],
    scores: dict | None = None,
) -> dict:
    """Generate a markdown governance/audit report from logs (and optional pre-computed scores)."""
    return generate_audit_report(logs, scores)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

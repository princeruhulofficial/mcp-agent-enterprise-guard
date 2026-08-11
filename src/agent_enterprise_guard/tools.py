"""Pure computation tools for agent reliability, silent failures, and permission evaluation."""

from __future__ import annotations

from typing import Any
import statistics


def score_agent_reliability(
    logs: list[dict[str, Any]],
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Compute overall reliability score (0-100) from tool-call logs.

    Expected log item keys: tool_name, success (bool), latency_ms (float),
    is_error (bool), content (str or None).
    """
    if not logs:
        return {
            "score": 0,
            "status": "no_data",
            "breakdown": {},
            "recommendations": ["Provide at least one tool-call log entry."],
        }

    weights = weights or {
        "success_rate": 0.40,
        "silent_failure_rate": 0.30,
        "latency_health": 0.20,
        "error_rate": 0.10,
    }

    total = len(logs)
    successes = sum(1 for l in logs if l.get("success", False) and not l.get("is_error", False))
    errors = sum(1 for l in logs if l.get("is_error", False))
    silent = sum(
        1
        for l in logs
        if not l.get("is_error", False)
        and (l.get("content") is None or str(l.get("content", "")).strip() == "")
    )
    latencies = [float(l.get("latency_ms", 0)) for l in logs if "latency_ms" in l]

    success_rate = successes / total if total else 0
    silent_rate = silent / total if total else 0
    error_rate = errors / total if total else 0

    if latencies:
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        latency_health = max(0.0, min(1.0, 1.0 - (p95 / 2000.0)))
    else:
        latency_health = 0.5

    score = (
        weights["success_rate"] * success_rate * 100
        + weights["silent_failure_rate"] * (1 - silent_rate) * 100
        + weights["latency_health"] * latency_health * 100
        + weights["error_rate"] * (1 - error_rate) * 100
    )
    score = round(max(0, min(100, score)), 1)

    recommendations = []
    if silent_rate > 0.1:
        recommendations.append(f"Silent failure rate is high ({silent_rate:.0%}). Investigate empty responses.")
    if error_rate > 0.15:
        recommendations.append(f"Error rate is elevated ({error_rate:.0%}). Check tool implementations.")
    if latency_health < 0.6:
        recommendations.append("Latency p95 is high. Consider caching or optimizing slow tools.")
    if not recommendations:
        recommendations.append("Reliability looks healthy. Keep monitoring.")

    return {
        "score": score,
        "status": "healthy" if score >= 75 else "needs_attention" if score >= 50 else "critical",
        "breakdown": {
            "success_rate": round(success_rate, 3),
            "silent_failure_rate": round(silent_rate, 3),
            "error_rate": round(error_rate, 3),
            "latency_health": round(latency_health, 3),
            "total_calls": total,
        },
        "recommendations": recommendations,
    }


def detect_silent_failures(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Flag calls that returned empty/null without raising an error."""
    silent = []
    for i, l in enumerate(logs):
        content = l.get("content")
        is_empty = content is None or str(content).strip() == ""
        if is_empty and not l.get("is_error", False):
            silent.append(
                {
                    "index": i,
                    "tool_name": l.get("tool_name", "unknown"),
                    "latency_ms": l.get("latency_ms"),
                    "reason": "empty_or_null_content_without_error",
                }
            )
    total = len(logs) or 1
    return {
        "silent_count": len(silent),
        "silent_rate": round(len(silent) / total, 3),
        "silent_failures": silent,
        "message": f"Found {len(silent)} silent failures out of {len(logs)} calls.",
    }


def evaluate_permission(
    action: dict[str, Any],
    policy_rules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Simple rule engine: allow/deny based on matching policy rules."""
    matched = []
    decision = "allow"
    risk = 0.0

    for rule in policy_rules:
        match = True
        for k, v in rule.items():
            if k in ("decision", "reason", "risk"):
                continue
            if action.get(k) != v:
                match = False
                break
        if match:
            matched.append(rule)
            if rule.get("decision") == "deny":
                decision = "deny"
            risk = max(risk, float(rule.get("risk", 0.5)))

    return {
        "decision": decision,
        "matched_rules": matched,
        "risk_score": round(risk, 2),
        "action": action,
        "explanation": (
            "Denied by matching policy rule."
            if decision == "deny"
            else "Allowed (no deny rule matched)."
        ),
    }


def generate_audit_report(
    logs: list[dict[str, Any]],
    scores: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produce a simple human-readable governance report."""
    if scores is None:
        scores = score_agent_reliability(logs)
    silent = detect_silent_failures(logs)

    report_md = f"""# Agent Enterprise Guard — Audit Report

## Overall Reliability Score: {scores.get('score', 'N/A')}/100
**Status:** {scores.get('status', 'unknown')}

### Breakdown
- Success rate: {scores.get('breakdown', {}).get('success_rate', 'N/A')}
- Silent failure rate: {scores.get('breakdown', {}).get('silent_failure_rate', 'N/A')}
- Error rate: {scores.get('breakdown', {}).get('error_rate', 'N/A')}
- Total calls analysed: {scores.get('breakdown', {}).get('total_calls', 0)}

### Silent Failures
{silent.get('message', '')}

### Recommendations
"""
    for rec in scores.get("recommendations", []):
        report_md += f"- {rec}\n"

    report_md += "\n---\nGenerated by mcp-agent-enterprise-guard (Prevalid)\n"

    return {
        "report_markdown": report_md,
        "summary": {
            "score": scores.get("score"),
            "status": scores.get("status"),
            "silent_count": silent.get("silent_count"),
        },
    }

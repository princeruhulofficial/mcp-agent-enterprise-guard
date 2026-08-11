"""Basic unit tests for core computation tools."""

from agent_enterprise_guard.tools import (
    detect_silent_failures,
    evaluate_permission,
    score_agent_reliability,
)


def test_score_empty():
    result = score_agent_reliability([])
    assert result["score"] == 0
    assert result["status"] == "no_data"


def test_score_healthy():
    logs = [
        {"tool_name": "a", "success": True, "latency_ms": 50, "is_error": False, "content": "ok"},
        {"tool_name": "b", "success": True, "latency_ms": 80, "is_error": False, "content": "ok"},
    ]
    result = score_agent_reliability(logs)
    assert result["score"] >= 80
    assert result["status"] == "healthy"


def test_silent_detection():
    logs = [
        {"tool_name": "x", "is_error": False, "content": ""},
        {"tool_name": "y", "is_error": False, "content": "data"},
        {"tool_name": "z", "is_error": True, "content": None},
    ]
    result = detect_silent_failures(logs)
    assert result["silent_count"] == 1
    assert result["silent_failures"][0]["tool_name"] == "x"


def test_permission_deny():
    action = {"action": "write", "resource": "customer_data"}
    rules = [
        {"action": "write", "resource": "customer_data", "decision": "deny", "reason": "PII", "risk": 0.9}
    ]
    result = evaluate_permission(action, rules)
    assert result["decision"] == "deny"
    assert result["risk_score"] == 0.9

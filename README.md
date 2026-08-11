# mcp-agent-enterprise-guard

**Compute trust scores, permission decisions, and silent-failure risk for AI agents — pure local computation, zero API cost.**

Built for founders and teams who need lightweight AI governance (especially those validating products with Prevalid).

[![Available on MCPize](https://mcpize.com/badge/mcp-agent-enterprise-guard)](https://mcpize.com/servers/mcp-agent-enterprise-guard)

## Why this exists

AI agents often fail *silently*: they return empty results, pick the wrong tool, or violate simple policies without raising an error. Enterprise-style workflows (Salesforce, ServiceNow, internal data) make this painful and expensive.

This MCP server gives your agent (or your ops team) four practical tools that run entirely on the data you already have — no external APIs, no monthly data bills.

## Tools

| Tool | What it does |
|------|--------------|
| `score_agent_reliability_tool` | 0–100 reliability score + breakdown + recommendations |
| `detect_silent_failures_tool` | Finds empty/null responses that did not set `is_error` |
| `evaluate_permission_tool` | Simple allow/deny rule engine for agent actions |
| `generate_audit_report_tool` | Human-readable markdown governance report |

## Quick start (local)

```bash
git clone https://github.com/princeruhulofficial/mcp-agent-enterprise-guard.git
cd mcp-agent-enterprise-guard
pip install -e .
python -m agent_enterprise_guard.server
```

Or with FastMCP / Claude Desktop config:

```json
{
  "mcpServers": {
    "agent-enterprise-guard": {
      "command": "python",
      "args": ["-m", "agent_enterprise_guard.server"]
    }
  }
}
```

## Example usage

Feed your agent run logs (list of dicts with `tool_name`, `success`, `latency_ms`, `is_error`, `content`) and get a reliability score + silent-failure list in seconds.

## Monetization (MCPize)

Freemium model planned:
- Free: limited daily calls for testing
- Pro / Team / Enterprise tiers with higher limits and report export

## License

MIT

---

Made for the Prevalid community — build AI systems people can actually trust.

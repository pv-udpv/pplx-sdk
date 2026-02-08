#!/usr/bin/env bash
# Security gate for Copilot preToolUse hook.
# Reads hook input JSON from stdin and denies destructive system commands.

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('toolName',''))" 2>/dev/null || echo "")
TOOL_ARGS=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('toolArgs',''))" 2>/dev/null || echo "")

if [ "$TOOL_NAME" = "bash" ] && echo "$TOOL_ARGS" | grep -qE 'rm\s+-rf\s+/|mkfs|dd\s+if=|:()\{\s*:|>\s*/dev/sd'; then
  echo '{"permissionDecision":"deny","permissionDecisionReason":"Destructive system commands are not allowed"}'
else
  echo '{}'
fi

#!/usr/bin/env bash
# Session start hook: initialize workflow state and load context.
set -euo pipefail

STATE_DIR=".github/hooks/state"
STATE_FILE="$STATE_DIR/workflow-state.json"

mkdir -p "$STATE_DIR"

if [ ! -f "$STATE_FILE" ]; then
  cat > "$STATE_FILE" <<'EOF'
{
  "version": 1,
  "current_phase": "init",
  "phases_completed": [],
  "session_count": 0,
  "last_session_start": null,
  "last_session_end": null,
  "tool_calls": { "bash": 0, "edit": 0, "view": 0, "other": 0 },
  "errors": [],
  "checkpoints": []
}
EOF
fi

# Update session state
python3 -c "
import json, datetime
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
state['session_count'] = state.get('session_count', 0) + 1
state['last_session_start'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
if state.get('current_phase') == 'init':
    state['current_phase'] = 'ready'
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

echo "pplx-sdk session #$(python3 -c "import json; print(json.load(open('$STATE_FILE'))['session_count'])") initialized | phase: $(python3 -c "import json; print(json.load(open('$STATE_FILE'))['current_phase'])")"

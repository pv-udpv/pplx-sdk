#!/usr/bin/env bash
# Session end hook: capture results and advance workflow phase.
set -euo pipefail

STATE_FILE=".github/hooks/state/workflow-state.json"

[ -f "$STATE_FILE" ] || exit 0

python3 -c "
import json, datetime
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
state['last_session_end'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
# Add checkpoint
checkpoint = {
    'timestamp': state['last_session_end'],
    'phase': state.get('current_phase', 'unknown'),
    'session': state.get('session_count', 0),
    'tool_calls': dict(state.get('tool_calls', {}))
}
state.setdefault('checkpoints', []).append(checkpoint)
# Reset per-session tool counters
state['tool_calls'] = {'bash': 0, 'edit': 0, 'view': 0, 'other': 0}
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
print(f\"Session ended | phase: {state['current_phase']} | checkpoints: {len(state['checkpoints'])}\")
"

#!/usr/bin/env bash
# Post-tool-use hook: track tool calls and auto-advance workflow phases.
set -euo pipefail

STATE_FILE=".github/hooks/state/workflow-state.json"

[ -f "$STATE_FILE" ] || exit 0

INPUT=$(cat)

python3 -c "
import json, sys

input_data = json.loads('''$INPUT''') if '''$INPUT'''.strip() else {}
tool_name = input_data.get('toolName', 'other')

with open('$STATE_FILE', 'r') as f:
    state = json.load(f)

# Track tool usage
tool_calls = state.setdefault('tool_calls', {'bash': 0, 'edit': 0, 'view': 0, 'other': 0})
if tool_name in tool_calls:
    tool_calls[tool_name] += 1
else:
    tool_calls['other'] = tool_calls.get('other', 0) + 1

# Auto-advance phases based on activity
phase = state.get('current_phase', 'ready')
completed = set(state.get('phases_completed', []))

# Phase transitions based on tool activity
if phase == 'ready' and tool_calls.get('view', 0) >= 3:
    state['current_phase'] = 'exploring'
    completed.add('ready')
elif phase == 'exploring' and tool_calls.get('edit', 0) >= 1:
    state['current_phase'] = 'implementing'
    completed.add('exploring')
elif phase == 'implementing' and tool_calls.get('bash', 0) >= 2:
    state['current_phase'] = 'testing'
    completed.add('implementing')
elif phase == 'testing':
    state['current_phase'] = 'reviewing'
    completed.add('testing')

state['phases_completed'] = sorted(completed)

with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null || true

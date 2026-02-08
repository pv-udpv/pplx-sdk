#!/usr/bin/env bash

# Install GitHub Copilot Skills from github/awesome-copilot
# This script installs curated skills to enhance development workflow

set -euo pipefail

echo "🚀 Installing GitHub Copilot Skills from github/awesome-copilot..."
echo ""

# Array of skills to install
SKILLS=(
    "github/awesome-copilot@git-commit"
    "github/awesome-copilot@gh-cli"
    "github/awesome-copilot@refactor"
    "github/awesome-copilot@prd"
    "github/awesome-copilot@github-issues"
    "github/awesome-copilot@chrome-devtools"
)

# Counter for tracking progress
TOTAL=${#SKILLS[@]}
CURRENT=0

# Install each skill
for skill in "${SKILLS[@]}"; do
    ((CURRENT++))
    echo "[$CURRENT/$TOTAL] Installing: $skill"
    
    if npx --yes skills add "$skill"; then
        echo "✅ Successfully installed: $skill"
    else
        echo "❌ Failed to install: $skill" >&2
        exit 1
    fi
    
    echo ""
done

echo "🎉 All Copilot skills installed successfully!"
echo ""
echo "Installed skills:"
for skill in "${SKILLS[@]}"; do
    echo "  - ${skill##*/}"
done

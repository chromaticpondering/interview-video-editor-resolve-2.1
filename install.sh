#!/usr/bin/env bash
# Install the interview-video-editor-resolve skill for AI coding assistants.
#
# Usage:
#   ./install.sh                      # Install globally for Antigravity, Claude Code, and .agents
#   ./install.sh --workspace <dir>    # Install project-locally in <dir>/.agents/skills/
#   ./install.sh --antigravity        # Install only for Google Antigravity
#   ./install.sh --claude             # Install only for Claude Code
#   ./install.sh --agents             # Install only for ~/.agents/skills/
set -euo pipefail

SKILL_NAME="interview-video-editor-resolve"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$SCRIPT_DIR/$SKILL_NAME"

if [ ! -f "$SRC/SKILL.md" ]; then
  # Fallback if executed from inside the skill folder
  if [ -f "$SCRIPT_DIR/SKILL.md" ]; then
    SRC="$SCRIPT_DIR"
  else
    echo "Error: SKILL.md not found in $SRC"
    exit 1
  fi
fi

TARGET_DIRS=()
WORKSPACE_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE_DIR="$2"
      shift 2
      ;;
    --antigravity)
      TARGET_DIRS+=("$HOME/.gemini/config/skills" "$HOME/.gemini/antigravity/skills")
      shift
      ;;
    --claude)
      TARGET_DIRS+=("$HOME/.claude/skills")
      shift
      ;;
    --agents)
      TARGET_DIRS+=("$HOME/.agents/skills")
      shift
      ;;
    --all)
      TARGET_DIRS+=("$HOME/.gemini/config/skills" "$HOME/.gemini/antigravity/skills" "$HOME/.agents/skills" "$HOME/.claude/skills")
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--workspace <path> | --all | --antigravity | --claude | --agents]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

if [ -n "$WORKSPACE_DIR" ]; then
  TARGET_DIRS+=("$WORKSPACE_DIR/.agents/skills" "$WORKSPACE_DIR/.agent/skills")
fi

if [ ${#TARGET_DIRS[@]} -eq 0 ]; then
  # Default: Install to all active/standard global agent skill roots
  TARGET_DIRS=(
    "$HOME/.gemini/config/skills"
    "$HOME/.agents/skills"
    "$HOME/.claude/skills"
  )
fi

echo "=========================================================="
echo "Installing $SKILL_NAME"
echo "Source: $SRC"
echo "=========================================================="

installed_count=0
for dest_root in "${TARGET_DIRS[@]}"; do
  target_path="$dest_root/$SKILL_NAME"
  mkdir -p "$dest_root"

  if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
    bak_path="$target_path.bak-$(date +%Y%m%d-%H%M%S)"
    mv "$target_path" "$bak_path"
    echo "  [backup] Moved existing directory to $bak_path"
  fi

  rm -rf "$target_path"
  cp -R "$SRC" "$target_path"
  chmod +x "$target_path/scripts/"*.py "$target_path/scripts/"*.sh 2>/dev/null || true
  echo "  [ok] Installed to: $target_path"
  ((installed_count++))
done

echo "----------------------------------------------------------"
echo "Successfully installed $SKILL_NAME to $installed_count location(s)."
echo ""
echo "Next Steps:"
echo "1. Verify requirements: bash \"$SRC/scripts/setup_check.sh\""
echo "2. Ensure DaVinci Resolve is running and the 'davinci-resolve' MCP server is configured."
echo "3. Restart your AI assistant session, then prompt:"
echo "   'Use the interview-video-editor-resolve skill to edit footage in ./footage'"
echo "=========================================================="

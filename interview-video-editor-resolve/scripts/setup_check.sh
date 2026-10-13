#!/usr/bin/env bash
# setup_check.sh - Verify DaVinci Resolve, Resolve MCP schemas, and companion tools for interview-video-editor-resolve.
req_fail=0
ok()   { printf "  [ok]      %s\n" "$1"; }
warn() { printf "  [missing] %s  (%s)\n" "$1" "$2"; }
need() { printf "  [MISSING] %s  (%s)\n" "$1" "$2"; req_fail=1; }

echo "DaVinci Resolve & MCP"
if [ -d "/Applications/DaVinci Resolve/DaVinci Resolve.app" ]; then
  ok "DaVinci Resolve.app installed"
else
  need "DaVinci Resolve.app" "Install DaVinci Resolve in /Applications/DaVinci Resolve/"
fi

if [ -d "$HOME/.gemini/antigravity/mcp/davinci-resolve" ]; then
  tool_count=$(ls -1 "$HOME/.gemini/antigravity/mcp/davinci-resolve/"*.json 2>/dev/null | wc -l | tr -d ' ')
  ok "davinci-resolve MCP server configured ($tool_count tools)"
else
  need "davinci-resolve MCP" "Configure the davinci-resolve MCP server in Antigravity"
fi

echo "Required System Binaries"
command -v ffmpeg  >/dev/null && ok "ffmpeg: $(ffmpeg -version | head -1 | cut -d' ' -f3)" || need ffmpeg "install from ffmpeg.org or brew install ffmpeg"
command -v ffprobe >/dev/null && ok ffprobe || need ffprobe "ships with ffmpeg"
command -v python3 >/dev/null && ok "python3: $(python3 --version 2>&1 | cut -d' ' -f2)" || need python3 "3.10+"
if command -v node >/dev/null; then
  v=$(node --version | sed 's/v//;s/\..*//'); [ "$v" -ge 22 ] && ok "node: $(node --version)" || need "node $(node --version)" "HyperFrames sidecar needs Node 22+"
else need node "install Node 22+"; fi
command -v npx >/dev/null && ok npx || need npx "ships with Node"

echo "Python Packages (per-project venv recommended)"
for m in opentimelineio; do python3 -c "import $m" 2>/dev/null && ok "$m" || warn "$m" "pip install opentimelineio opentimelineio-plugins"; done
for m in whisperx faster_whisper; do python3 -c "import $m" 2>/dev/null && ok "$m" || true; done
python3 -c "import whisperx" 2>/dev/null || python3 -c "import faster_whisper" 2>/dev/null || warn "whisperx / faster-whisper" "pip install faster-whisper  (or use Resolve MCP media_pool_item.transcribe_audio)"

[ $req_fail -eq 0 ] && echo "All REQUIRED tools for interview-video-editor-resolve are ready." || echo "Some REQUIRED tools are missing."
exit $req_fail

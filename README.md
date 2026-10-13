# DaVinci Resolve MCP Interview & Testimonial Video Editor (v2.1)

[![Version: 2.1](https://img.shields.io/badge/Version-2.1-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![DaVinci Resolve](https://img.shields.io/badge/DaVinci%20Resolve-19.x%20--%2021.x-orange.svg)](https://www.blackmagicdesign.com/products/davinciresolve)
[![Protocol](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()

> An autonomous, senior-level AI video editor and colorist skill that operates **natively inside DaVinci Resolve** via the Model Context Protocol (MCP).

Turns folders of raw interview, testimonial, or talking-head footage into polished, word-by-word captioned, motion-graphics-rich, color-graded videos—with an interactive human-in-the-loop SRT review checkpoint, alternating jump-cut punch-ins, Fairlight stem ducking, and complete `.drp` / `.drt` / `.xml` / `.fcpxml` deliverables.

---

## What's New in v2.1 🚀

Based on real-world production runs on multi-take corporate interview footage:

1. **100% Native, Editable DaVinci Resolve Text Layers:**
   - **No pre-rendered transparent MOV or PNG files for text.** Every caption on Track `V4`, behind-subject focus word on Track `V2`, lower-third, and hook badge on Track `V5` is generated as a native DaVinci Resolve `Text` or `Text+` layer.
   - Any editor can open Resolve, click any caption clip on the timeline, and immediately edit words, fonts, tracking, or colors directly inside the **Inspector panel**.
2. **Lean & Real-Time (Text/Text+ Preferred, Minimal Fusion):**
   - Kept node graphs clean and lightweight: standard `Text+` titles are used directly on timeline tracks, reserving Fusion node graphs only for keying (DeltaKeyer / Magic Mask). Real-time 60fps timeline playback with zero caching lag.
3. **High Context Efficiency & Token Optimization:**
   - Solved token bloat caused by repetitive conversational tool calls. Batch timeline creation and title population (50–100 caption clips) is offloaded to `scripts/build_resolve_timeline.py`, building the complete multi-track timeline directly in DaVinci Resolve in **~1 second** with minimal token usage.
4. **Autonomous Non-English Spoken Language Protocol:**
   - Automatically detects and transcribes non-English speech via `faster-whisper` (`large-v3`) or Resolve AI transcription.
   - Explicitly asks the user in Step 0 Intake how they want the transcript and captions formatted:
     - **(A) Native Script** (e.g., Hindi Devanagari, Tamil, Malayalam, Spanish, Japanese, German)
     - **(B) Romanized / Transliterated** (Latin-alphabet transliteration for high-retention social reels)
     - **(C) English Translation** (Translated into English while preserving spoken sentence timing)
     - **(D) Dual Captions** (Top line: Native script; Bottom line: English translation)
5. **Standardized Text Placement, Alignment & Spacing:**
   - **Lower-Third Safe Zone:** Captions sit at `Center Y = 0.28 to 0.33` (Line 1: `0.33`, Line 2: `0.265`), leaving the speaker's face, neck, and upper chest completely clear.
   - **Ultra-Tight Zero-Gap Line Spacing:** Vertical line offset is `~0.065`, creating tight stacked headline typography with zero vertical gap.
   - **High-Contrast Styling:** Pure White text (`#FFFFFF`) with a thin dark border and a gentle, soft drop shadow (`Opacity: 0.65`, `Softness: 0.020`, `Offset: 0.003`) ensuring 100% readability on any background.
   - **Behind-Subject Focus Words:** Automatically analyzes the transcript and places 4–6 high-impact key words/metrics behind the speaker on Track `V2` (`Center Y ~0.64`, `Size: 0.17–0.24`, Pure White) with `V3` speaker matte cutout.
6. **Strict Style Reference Adherence:**
   - Follows the user's provided **text style reference image** strictly (fonts, case, pill/badge/tape styling, outlines, and brand colors).

---

## Standard Layered Timeline Standard (`04_Master_Publish`)

| Track | Name | Function (All Text Native & Editable in Resolve) |
|---|---|---|
| **ST1** | `ST1_SUBTITLES` | Native Resolve Subtitle Track (`<project>_captions.srt`) |
| **V5** | `V5_FRONT_GFX_TITLES` | Native `Text+` lower-thirds, hook badges, and CTA end cards |
| **V4** | `V4_CAPTIONS_ANIMATED` | **Native Resolve `Text+` word-by-word caption clips** (Lower-Third, ultra-tight line spacing, pure white, soft drop shadow, orange clip color) |
| **V3** | `V3_SPEAKER_ROTO_MATTE` | Duplicated speaker cutout via Resolve **Magic Mask** or DeltaKeyer (Purple clip color) |
| **V2** | `V2_BEHIND_SUBJECT_GFX` | **Native Resolve `Text+` behind-subject focus words** (`Center Y ~0.64`, Teal clip color) and full-opacity B-roll |
| **V1** | `V1_A_ROLL_CAMERA` | Graded primary camera cuts with alternating punch-ins (`106%–112%`) on jump cuts |
| **A1** | `A1_DIALOGUE_CLEAN` | Mastered, denoised, EQ'd, `-14 LUFS` / `-16 LUFS` normalized dialogue spine |
| **A2** | `A2_RAW_DIALOGUE_DISABLED` | Original unbaked camera audio cuts (**disabled** for instant Fairlight repair/reference) |
| **A3** | `A3_MUSIC_BED` | User's music file (or licensed track) sidechain-ducked `12–18 dB` under speech |
| **A4** | `A4_SFX_TRANSITIONS` | Subtle transition whooshes and graphic accent hits (`-18` to `-24 dB` below speech) |

---

## Installation

### Method 1: Using the Skills CLI (Recommended)
```bash
npx skills add <your-github-username>/interview-video-editor-resolve -g
```

### Method 2: One-Click Installer Script

Clone the repository and run the installer:

**macOS / Linux:**
```bash
git clone https://github.com/<your-github-username>/interview-video-editor-resolve.git
cd interview-video-editor-resolve
chmod +x install.sh
./install.sh                      # Installs globally for Antigravity, Claude Code, and .agents
./install.sh --workspace /path    # Installs into a specific project workspace
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/<your-github-username>/interview-video-editor-resolve.git
cd interview-video-editor-resolve
.\install.ps1                     # Installs globally
.\install.ps1 -Workspace C:\path  # Installs into a specific project workspace
```

### Method 3: Manual Installation
Copy the `interview-video-editor-resolve/` folder directly to your agent's skills directory:
- **Google Antigravity:** `~/.gemini/config/skills/interview-video-editor-resolve`
- **Universal Agents:** `~/.agents/skills/interview-video-editor-resolve`
- **Claude Code:** `~/.claude/skills/interview-video-editor-resolve`

---

## Workflow Overview

```
Phase 0: Ingest & Audit ──────► Scan local music, verify Resolve MCP, create project & bins
       │
Phase 1: Transcribe & Analyze ─► Autonomous non-English transcription, ask user for format (Q9), stamp clip markers
       │
Phase 2: Assembly Edit ────────► Strip fluff, 2-6 frame audio fades, alternating jump-cut punch-ins (108%)
       │
Phase 2.5: Review Gate ────────► [STOP] 720p cut + sentence SRT -> You edit SRT -> Agent diffs & rebuilds
       │
Phase 2.6: Style Proof ────────► [STOP] 10-15s vertical slice (captions + graphics + roto + grade)
       │
Phase 3: Word-by-Word Captions ─► 1-2 word chunks, native Text+ on V4, lower-third zone, tight line spacing
       │
Phase 4: Behind-Subject Words ─► 4-6 key focus words on V2 (Center Y ~0.64) with Text+ lower-thirds on V5
       │
Phase 5: Roto / Behind-Speaker ─► Resolve Magic Mask or DeltaKeyer speaker cutout on V3 (V2 behind V3)
       │
Phase 6: Fairlight Audio Mix ──► -14 LUFS dialogue (A1), raw cuts (A2 disabled), ducked music (A3), SFX (A4)
       │
Phase 7: Color Page Grade ─────► Color Groups, Log-to-Rec.709, CDL balance, before/after stills
       │
Phase 8: Quality Control ──────► detect_gaps_overlaps (0/0), timeline_frame visual audit, verify native Text+ clips
       │
Phase 9: Render & Deliver ─────► Resolve Deliver queue MP4 + .drp + .drt + .xml + .fcpxml + SRTs
```

---

## Deliverables Package

Every project delivers a complete, professional turnover package in `<project>_delivery/`:

```text
<project>_delivery/
├── <project>_final.mp4                      # Rendered from DaVinci Resolve Deliver queue
├── <project>.drp                            # Full DaVinci Resolve Project export (stills & LUTs included)
├── <project>_master.drt                     # DaVinci Resolve Timeline export
├── <project>_cuts.xml                       # FCP7 XML (Premiere Pro & DaVinci Resolve)
├── <project>_cuts.fcpxml                    # FCPXML v1.9+ (Final Cut Pro & DaVinci Resolve)
├── <project>_cuts.otio                      # OpenTimelineIO interchange file
├── <project>_captions.srt                   # Word-by-word chunked caption SRT
├── <project>_transcript.srt                 # Full-sentence readable transcript SRT
├── grade_before_after/                      # Color page before/after stills & frame captures
├── review_rounds/                           # review_v1.srt, user edits, diff reports, review cuts
├── edit_log.md                              # Story plan, what was cut and why, take scores, EDL
├── music_license.md                         # License terms or "user-supplied file"
├── asset_log.csv                            # Provenance log of all SVGs/icons/Lottie assets
├── credits.md                               # Attribution lines for video description / end-card
├── licenses.md                              # Open-source libraries and engine licenses
├── engine_log.md                            # Track-by-track engine breakdown & MCP run IDs
├── resolve_mcp_execution_report.md          # Full Resolve MCP execution audit report
├── README.md                                # Relink guide and track map for human editors
└── project_source/                          # Project scripts and assets
```

---

## Folder Layout

```text
interview-video-editor-resolve/
├── SKILL.md                          # Main workflow instructions read by AI coding agents (v2.1)
├── references/
│   ├── resolve-mcp-tools.md          # Complete Resolve MCP API operations, token rules & coordinate math
│   ├── libraries.md                  # Hybrid stack & native Text+ title engine documentation
│   ├── music-sources.md              # Music scan rules, free music libraries, and Fairlight ducking
│   └── svg-sources.md                # SVG/Lottie sourcing, SVGO cleaning, and asset logging
├── scripts/
│   ├── build_resolve_timeline.py     # Batch builds multi-track timeline & native Text+ clips in Resolve
│   ├── build_resolve_plan.py         # Frame math (source_fps vs timeline_fps), punch-ins, caption chunks
│   ├── export_xml.py                 # FCP7 XML and FCPXML generator & validator
│   ├── find_music.py                 # Scans folders for .mp3/.wav files and classifies music vs voice
│   ├── setup_check.sh                # Verifies Resolve app, MCP server, FFmpeg, Node, and Python
│   └── srt_tools.py                  # SRT chunking, difflib diffing, word alignment, and validation
└── assets/
    └── README.md                     # Instructions for style references, fonts, logos, and music
```

---

## License

Released under the [MIT License](LICENSE).
Third-party video footage, music tracks, and graphic assets retain their respective licenses and are logged automatically in `asset_log.csv` and `music_license.md`.

---
name: interview-video-editor-resolve
description: End-to-end editing of interview and testimonial footage natively inside DaVinci Resolve using the DaVinci Resolve MCP server (v2.1). Use when the user supplies raw talking-head or interview footage and wants DaVinci Resolve to perform the entire edit—ingest, bin organization, autonomous transcription (with explicit handling for non-English languages), removing fluff/back takes/mistakes/dead air/pre-roll instructions, an interactive SRT review checkpoint (diffing user SRT edits and rebuilding the Resolve timeline), 100% native editable DaVinci Resolve Text/Text+ word-by-word captions (never transparent MOV/PNG overlays), behind-the-speaker focus words, lower-thirds, transitions, Fairlight audio mix, Color page grading, and native Resolve rendering. Highly token-optimized by offloading timeline and title generation to fast local Resolve scripts.
---

# DaVinci Resolve MCP Interview & Testimonial Video Editor (v2.1)

This skill runs **natively inside DaVinci Resolve via the `davinci-resolve` MCP server**. **DaVinci Resolve is the primary NLE, compositor, color grading suite, and render engine** throughout every phase.

### Core Architectural Rules for v2.1 (Non-Negotiable)
1. **100% Native, Editable Text Layers:** **ALL text layers (word-by-word captions on `V4`, behind-subject focus words on `V2`, lower-thirds, hook badges, and CTA end cards on `V5`) MUST be native DaVinci Resolve `Text` or `Text+` layers.** Never use pre-rendered transparent MOV or PNG files for text. Every caption and title clip on the timeline must be directly clickable and editable by a human editor in DaVinci Resolve's Inspector.
2. **Use Text or Text+ Wherever Possible; Minimal Fusion:** Use native `Text` or `Text+` titles directly on timeline tracks. Use Fusion node graphs only when absolutely necessary (e.g., DeltaKeyer / keying). Do not over-engineer complex multi-node Fusion trees for standard text.
3. **Token Optimization & Offloading:** Do not burn hundreds of thousands of LLM context tokens making dozens of repetitive conversational tool calls (e.g. inserting 80 titles one-by-one). Instead, offload batch timeline construction to `scripts/build_resolve_timeline.py` which executes directly in Resolve in ~1 second. Keep conversational summaries compact and never dump massive raw transcripts or redundant images into context.
4. **Non-English Spoken Language Protocol:** If the spoken language is not English, the agent transcribes the native speech autonomously using `faster-whisper` or Resolve AI transcription, and explicitly asks the user in Step 0 Intake how they want the transcript and captions formatted (Native script, Romanized/transliterated, English translation, or Dual captions).
5. **Text Placement, Alignment & Spacing Standards:**
   - **Lower-Third Zone:** Spoken captions must sit in the lower-third zone (`Center Y ~0.28 to 0.33` for vertical 9:16; `0.18 to 0.25` for landscape 16:9) leaving the speaker's face, neck, and upper torso completely unobstructed.
   - **Ultra-Tight Line Spacing (Zero Gap):** In 2-line stacked phrases, vertical line offset must be `~0.065` (virtually zero gap) so words read as cohesive headline typography.
   - **High-Contrast Legibility:** Default to **Pure White (`#FFFFFF`)** text with a thin dark outline (`Thickness ~0.004`) and a soft, subtle drop shadow (`Opacity ~0.65`, `Softness ~0.020`, `Offset ~0.003`) so captions stay legible across any background.
   - **Behind-Subject Focus Words:** Analyze the transcript and place 4–6 high-impact hook/metric words behind the speaker on Track `V2` (`Center Y ~0.64`, `Size 0.17 to 0.24`, Pure White) with speaker matte cutout on `V3`.
6. **Strict Style Reference Adherence:** Strictly follow the user's provided **text style reference image** (font family, weight, case, pill/badge/tape backgrounds, outlines, and brand colors).

---

## Bundled References & Helper Scripts

- [references/resolve-mcp-tools.md](references/resolve-mcp-tools.md): Playbook for all 37 Resolve MCP tools, coordinate/frame rules, and API workarounds.
- [references/libraries.md](references/libraries.md): Hybrid stack, token optimization, and licensing rules.
- [references/music-sources.md](references/music-sources.md): Pre-intake local music scan, user-music-only rule, free music/SFX libraries, and Fairlight ducking.
- [references/svg-sources.md](references/svg-sources.md): Sourcing SVG/Lottie/icon assets and asset logging.

Helper scripts in `scripts/`:
- **[scripts/build_resolve_timeline.py](scripts/build_resolve_timeline.py)** *(v2.1)*: High-performance local script that connects to Resolve and builds the complete multi-track timeline (`V1`–`V5`, `A1`–`A4`), places native `Text+` captions on `V4`, focus words on `V2`, camera cuts on `V1`, audio crossfades, and alternating punch-ins in 1 second.
- **[scripts/build_resolve_plan.py](scripts/build_resolve_plan.py)** *(v2.1)*: Generates the structured cut plan JSON, jump-cut transforms, 1–2 word caption chunks with micro-gap bridging, and review manifests.
- **[scripts/srt_tools.py](scripts/srt_tools.py)**: `chunk`, `diff`, `align`, and `validate`.
- **[scripts/export_xml.py](scripts/export_xml.py)**: FCP7 XML (`.xml`) and FCPXML (`.fcpxml`) generator/validator.
- **[scripts/find_music.py](scripts/find_music.py)**: Scans for `.mp3`/`.wav` files and classifies music vs. voice.
- **[scripts/setup_check.sh](scripts/setup_check.sh)**: Verifies Resolve app, MCP configuration, FFmpeg, Node, and Python.

---

## STEP 0: INTAKE (MANDATORY — DO THIS FIRST)

### Silent Pre-Intake Scan
Before sending your first message to the user:
1. Run `python3 scripts/find_music.py "$PROJECT_DIR" "$FOOTAGE_DIR"` to detect `.mp3`/`.wav` music files so you can report them in Question 7.
2. Probe Resolve MCP status non-destructively: `resolve_control(action="get_version")` and `project_manager(action="get_current")`.

### Intake Questions (Ask in a Single Message)
Do not start Phase 0 until the user answers or says to use defaults. Confirm any details already stated in the prompt rather than re-asking.

**Required Questions**
1. **Footage location & Resolve Project:** Path to footage folder, target Resolve project name (new project or use existing open project?), and speaker names/roles for lower-thirds.
2. **Aspect ratio:** `16:9`, `9:16`, `1:1`, `4:5`, or multiple deliverable timelines (e.g. 16:9 master + 9:16 vertical via Smart Reframe).
3. **Resolution and frame rate:** e.g., `1920x1080` or `3840x2160`, `24` / `25` / `29.97` / `30` fps (default: match primary camera source).
4. **Target length:** Exact duration, a range, or "as short and punchy as the story allows".
5. **Brand fonts, colors & templates:** Font families, hex colors, logo files, and any installed PowerBins or title templates.
6. **Reference images:** The **text style reference** (captions) and **element style reference** (graphics).
7. **Music and sound effects:** Report any `.mp3`/`.wav` music file found during the pre-intake scan. **Hard rule:** If a music file was found in their folder, it is the ONLY music that will be used. If none was provided, ask if they want free-licensed music (give mood/genre) and transition SFX.
8. **Output formats:** Final MP4, Resolve Project (`.drp`), Resolve Timeline (`.drt`), Cut XML (`.xml` + `.fcpxml`), and SRT files (`_captions.srt` and `_transcript.srt`).
9. **Spoken language & transcript format (Crucial for Non-English):**
   - What is the spoken language?
   - **If the spoken language is NOT English, how do you want the transcript and captions formatted?**
     - **(A) Native Script** (e.g., Hindi Devanagari, Tamil, Malayalam, Spanish, Japanese, etc.)
     - **(B) Romanized / Transliterated** (e.g., Hinglish or Latin-alphabet transliteration for high-retention social viewing)
     - **(C) English Translation** (Translated into English while preserving spoken sentence timing)
     - **(D) Dual Captions** (Top line: Native script; Bottom line: English translation)
10. **Review gates:** Confirm **Phase 2.5 Review Checkpoint** (Resolve assembly cut + sentence-level SRT review before styling; default **YES**) and **Phase 2.6 Style Proof** (10–15s fully finished Resolve slice; default **YES**).
11. **Destination platform(s):** YouTube, Instagram/Reels, TikTok, LinkedIn, website, ad. Sets safe zones, blanking, and target loudness (`-14 LUFS` social vs. `-16` to `-18 LUFS` web).
12. **Text & Graphic layers:** Confirm that all captions, titles, and behind-subject focus text will be generated as **100% native editable DaVinci Resolve Text/Text+ layers** on the timeline (never transparent MOV/PNG files).
13. **Attribution:** Is it OK to use free assets/music requiring credit (with logged credits in `credits.md` and end card), or strictly no-attribution sources only?

Save the confirmed answers to `project_brief.md`.

---

## 5-VIDEO / 4-AUDIO / 1-SUBTITLE LAYERED TIMELINE STANDARD

Every master timeline (`04_Master_Publish`) in DaVinci Resolve MUST be built with clean, named, editable tracks:

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

## PHASE 0: INGEST, AUDIT & PROJECT SETUP

1. **Verify Environment & Connect:** Run `bash scripts/setup_check.sh`. Call `resolve_control(action="get_version")` and `resolve_control(action="begin_execution")`. Record versions in `engine_log.md`.
2. **Probe Source Media:** Run `ffprobe` on all footage files. Note duration, resolution, FPS, codecs, audio channels, and log/color profiles.
3. **Setup Resolve Project:** Call `project_manager(action="safe_project_create")` or `load`, set timeline frame rate and resolution via `project_manager(action="safe_set_project_settings")`, create bins (`01_Raw_Footage`, `02_Audio`, `03_Graphics`, `04_Roto_Mattes`, `05_Timelines`, `06_Review_Exports`), and import footage into `01_Raw_Footage`.
4. **Read Clip IDs:** Call `folder(action="get_clips")` and record each clip's `clip_id`, `source_fps`, and duration in `asset_manifest.json`.

---

## PHASE 1: TRANSCRIBE & ANALYZE (AUTONOMOUS NON-ENGLISH HANDLING)

1. **Autonomous Transcription:**
   - If footage is non-English, detect language and transcribe the native speech using `faster-whisper` (large-v3) or Resolve AI transcription (`media_pool_item.transcribe_audio`).
   - Format the words and transcript according to the user's choice from Intake Q9 (Native script, Romanized transliteration, English translation, or Dual captions).
   - Lift caps via `media_analysis(action="set_caps_preset", params={"preset": "unlimited"})` during analysis and restore to `standard` when done.
   - Save word-level timestamps (`word`, `start`, `end`, `confidence`) to `assembly_words.json`.
2. **Take Scoring & Fluff Detection:**
   - Detect and classify: Pre-roll instructions, dead air / pauses > `0.8s`, fillers/stumbles, back takes, and post-roll chatter.
   - Score each take on delivery clarity, energy, completeness, and framing.
3. **Annotate Media Pool Clips:**
   - Add markers to Media Pool clips via `media_pool_item_markers(action="add")`: `Green` = Hero Take, `Blue` = Alternate, `Red` = Cut (Pre-roll/Back take/Flub), `Yellow` = Dead air.

---

## PHASE 2: ASSEMBLY EDIT IN DAVINCI RESOLVE (STORY FIRST)

1. **Build Narrative Arc:** Keep only the best take of any repeated line; strip pre-roll, post-roll, stumbles, and dead air. Keep `150–250 ms` natural breathing room around phrases.
2. **Generate Cut Plan & Timeline Payload:**
   - Write `rough_cut_list.json` and run:
     ```bash
     python3 scripts/build_resolve_plan.py rough_cut_list.json --out resolve_assembly_plan.json
     ```
3. **Construct Assembly Timeline (`02_Assembly_v1`) in Resolve:**
   - Execute `scripts/build_resolve_timeline.py resolve_assembly_plan.json --timeline 02_Assembly_v1`.
   - In 1 second, the script builds the timeline, places camera cuts on `V1`, applies 2–6 frame audio crossfades, and applies alternating subtle punch-ins (`106%–112%`) on same-camera jump cuts.
4. **Dialogue Cleanup & Audio Prep:**
   - Enable Resolve AI Voice Isolation on dialogue (`timeline.set_voice_isolation_state`).
   - Render a master dialogue stem (`-14 LUFS` social / `-16 LUFS` web, `-1 dBTP` true peak) and ducked music bed (`A3`).
5. **Verify:** Check `timeline(action="detect_gaps_overlaps")` returns `0 / 0`.

---

## PHASE 2.5: REVIEW CHECKPOINT (STOP AND WAIT FOR USER)

1. **Duplicate to `02_Review_v1`:** Call `timeline(action="duplicate", params={"name": "02_Review_v1"})`.
2. **Generate Sentence-Level Review Package:**
   - `review_v1.srt`: Sentence-level cues (`1–6s`, max 2 lines, ~42 chars/line).
   - `review_manifest_v1.json`: Maps cue IDs (`C001`, `C002`...) to timeline and source clip frames.
   - `removed_sections_v1.md`: Every cut section (`R01`, `R02`...) with timecode, text, and reason.
   - `review_notes_v1.md`: Language notes, low-confidence words, and take decisions.
3. **Render `review_cut_v1.mp4`:** Render a 720p proxy with plain sentence captions and cue ID (`C001`) burned in top-left corner.
4. **STOP and wait for the user:** Instruct the user to edit wording, delete cues/words, or trim in `review_v1.srt` and reply.
5. **Diff & Rebuild:**
   - When the user returns `review_v2.srt`, run `python3 scripts/srt_tools.py diff review_v1.srt review_v2.srt --out-md review_diff_report_v2.md` and `scripts/srt_tools.py align`.
   - Update `approved_cut_list.json`, run `scripts/build_resolve_plan.py`, and rebuild `02_Review_v2` / `03_Approved_Lock` via `scripts/build_resolve_timeline.py`.
   - Freeze `approved_cut_list.json` and `approved_captions.srt` upon approval.

---

## PHASE 2.6: STYLE PROOF SLICE (10–15s GATE)

Before building the full video, build a 10–15s slice on `03_Style_Proof` demonstrating:
1. Native `Text+` word-by-word animated captions matching the **text style reference image** (`V4`).
2. Native `Text+` lower-third and hook badge (`V5`).
3. Behind-subject focus word (`V2`) with speaker matte cutout (`V3`).
4. 1 transition + SFX (`A4`).
5. Color page grade on `V1` with before/after frame captures (`timeline_frame.capture` and `gallery_stills.grab_and_export`).

Render `style_proof_slice.mp4`, present to user, and wait for style approval before full rollout.

---

## PHASE 3: NATIVE WORD-BY-WORD CAPTIONS ON TRACK V4

1. **Break Down into Punchy 1–2 Word Phrases:**
   - Never leave long sentences lingering on screen. Group words into punchy **1–2 word stacked phrases** (max 3 words).
   - Bridge micro-gaps (`< 0.22s`) between consecutive phrases so captions never flicker to black between words.
2. **Lower-Third Zone Placement:**
   - For vertical 9:16: **Line 1 at `Center Y = 0.33`**, **Line 2 at `Center Y = 0.265`** (single line at `0.30`).
   - For landscape 16:9: `Center Y = 0.20 to 0.25`.
   - Leaves the speaker's face, mouth, neck, and upper chest completely clear.
3. **Ultra-Tight Zero-Gap Line Spacing:**
   - Vertical line offset between lines 1 and 2 is `~0.065`, creating cohesive, stacked headline typography.
4. **High-Contrast Text Styling:**
   - Text color: **Pure White (`#FFFFFF`)** by default.
   - Outline: Thin dark navy/black border (`Enabled2 = 1`, `Thickness = 0.004`, `OutsideOnly = 1`).
   - Shadow: Soft, subtle drop shadow (`Enabled3 = 1`, `Opacity = 0.65`, `Softness = 0.020`, `Offset = 0.003`).
5. **100% Native DaVinci Resolve Text+:**
   - Placed on Track `V4_CAPTIONS_ANIMATED` by `scripts/build_resolve_timeline.py`.
   - Each clip has its name set to the spoken phrase and clip color set to `Orange`.
   - A human editor can click any caption on Track V4, open the **Inspector**, and modify text, fonts, colors, or tracking directly in DaVinci Resolve!

---

## PHASE 4: MOTION GRAPHICS & BEHIND-SUBJECT FOCUS WORDS

1. **Behind-Subject Cinematic Focus Words (Tracks `V2` & `V3`):**
   - Extract 4–6 high-impact hook/metric words from the transcript (e.g. *"TWICE"*, *"20 MINS"*, *"DUPLICATES"*, *"INSTANT"*).
   - Place as native `Text+` titles on Track `V2_BEHIND_SUBJECT_GFX` in large display type (`Size 0.17 to 0.24`, `Center Y ~0.64`, Pure White, soft shadow).
   - Duplicate the camera clip on Track `V3_SPEAKER_ROTO_MATTE` directly above `V2` and isolate the speaker using Resolve AI **Magic Mask** or DeltaKeyer.
2. **Lower-Thirds & Front Titles (Track `V5_FRONT_GFX_TITLES`):**
   - Speaker lower-third (`ANJANA KRISHNAKUMAR • CITO RAZORPAY`), top hook badges, and CTA cards built as native Resolve `Text+` clips.
   - Minimal Fusion node graphs: Keep tools simple (`TextPlus` -> `Merge` -> `MediaOut`).
   - If complex hand-drawn Lottie / SVG paths are needed, render non-text vector graphics to ProRes 4444 alpha clips, while keeping all associated text as native Resolve `Text+` titles.

---

## PHASE 5: ROTO & SUBJECT SEPARATION ON TRACK V3

1. **Speaker Cutout Isolation:**
   - Use DaVinci Resolve Studio AI **Magic Mask** (`timeline_item_color.create_magic_mask`) on `V3_SPEAKER_ROTO_MATTE` clips, or DeltaKeyer / SAM 2 external alpha matte fallback.
2. **Mandatory Visual Inspection:**
   - Capture frames using `timeline_frame(action="capture", params={"quality": "frame"})` to verify clean edges, no hair halos, and identical color grading between `V1` and `V3`.

---

## PHASE 6: FAIRLIGHT AUDIO MIX & MUSIC DUCKING

1. **Strict Music Licensing Rule:**
   - If a local music file was found during Step 0, use **ONLY** that file.
   - If none was provided, source from approved free libraries per [references/music-sources.md](references/music-sources.md) and log in `music_license.md`.
2. **Audio Track Architecture:**
   - **`A1_DIALOGUE_CLEAN`:** Mastered dialogue with Resolve AI Voice Isolation, normalized to `-14 LUFS` social / `-16 LUFS` web, `-1 dBTP` true peak.
   - **`A2_RAW_DIALOGUE_DISABLED`:** Original camera audio cuts, disabled for instant NLE reference.
   - **`A3_MUSIC_BED`:** Music bed sidechain-ducked `12–18 dB` under speech with smooth `1.5–3s` tail fade.
   - **`A4_SFX_TRANSITIONS`:** Transition whooshes/hits gain-staged `-18` to `-24 dB` below speech.

---

## PHASE 7: COLOR GRADE ON DAVINCI RESOLVE'S COLOR PAGE

1. **Evidence First:** Switch to Color page (`resolve_control.open_page`) and call `timeline_item_color.grade_evidence_base`.
2. **Color Groups:** Group all camera clips (`V1` and `V3`) into a Color Group (`color_group.create`) so base CST / Log-to-Rec.709 LUT and look grades apply identically to both background and foreground cutout.
3. **Grade Versions & Primary Balance:** Add version `01_Baseline_Rec709` and `02_Hero_Grade`, apply CDL balance via `timeline_item_color.safe_set_cdl`, and export before/after stills via `gallery_stills.grab_and_export` and `timeline_frame.capture`.

---

## PHASE 8: QUALITY CONTROL

1. **Project & Timeline Health:** Call `timeline.detect_gaps_overlaps` (must return `0 / 0`) and `timeline.detect_missing_media`.
2. **Visual Frame Audit:** Capture 6 key frames with `timeline_frame.capture`: (1) Opening hook, (2) Lower-third, (3) Lower-third caption, (4) Behind-subject focus word, (5) Jump-cut punch-in, (6) CTA end card.
3. **Verify Text Layers are Native:** Confirm all clips on `V4`, `V2`, and `V5` are native Resolve `Text+` titles and inspectable in the GUI.

---

## PHASE 9: RENDER & DELIVER

1. **Native Deliver Queue Render:** Prepare and start job via `render(action="prepare_render_job")` and `render(action="start")`. Verify output file with `render.verify_output`.
2. **Export Resolve Project & Timelines:** Save project (`project_manager.save`), export `.drp` (`project_manager.safe_project_export`), and export `.drt` (`timeline.export_timeline_checked`).
3. **Export Interchange XMLs & SRTs:** Export FCP7 XML (`.xml`), FCPXML (`.fcpxml`), OTIO (`.otio`), `<project>_captions.srt` (chunked), and `<project>_transcript.srt` (sentences).
4. **Final Package Layout:**

```text
<project>_delivery/
├── <project>_final.mp4                      # Native DaVinci Resolve render
├── <project>.drp                            # Complete Resolve project archive (with stills & LUTs)
├── <project>_master.drt                     # Multi-track Master Timeline archive
├── <project>_cuts.xml                       # FCP7 XML interchange
├── <project>_cuts.fcpxml                    # FCPXML v1.9 interchange
├── <project>_cuts.otio                      # OpenTimelineIO interchange
├── <project>_captions.srt                   # Word-by-word chunked caption SRT
├── <project>_transcript.srt                 # Full-sentence readable transcript SRT
├── grade_before_after/                      # Color page before/after stills
├── review_rounds/                           # review_v1.srt, diff reports, review cuts
├── edit_log.md                              # Story plan, what was cut and why, EDL
├── music_license.md                         # Music license verification
├── asset_log.csv                            # Provenance log of all assets
├── credits.md                               # Attribution lines
├── licenses.md                              # Engine and library licenses
├── engine_log.md                            # Track-by-track engine breakdown & MCP run IDs
├── resolve_mcp_execution_report.md          # Full Resolve MCP audit report
├── README.md                                # Relink guide and track map for human editors
└── project_source/                          # Project scripts and assets
```

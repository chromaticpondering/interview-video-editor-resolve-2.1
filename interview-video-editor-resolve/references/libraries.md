# Libraries & Engines Reference (DaVinci Resolve MCP Hybrid Stack v2.1)

Read this in **Phase 0**. It lists DaVinci Resolve (driven via MCP) and the companion open-source engines/libraries this skill uses, what each is best at, its license, and how they integrate onto the Resolve timeline.

**Legend**
- ✔ = checked against the project's own page/README/license during research.
- ◇ = from general knowledge, verify on the site.

**General Rules for v2.1**
- **DaVinci Resolve is the primary NLE, timeline assembler, color suite, audio host, and final renderer.**
- **All Text Layers MUST be Native DaVinci Resolve Text / Text+ Titles:** Never pre-render captions, lower-thirds, or focus words into transparent MOV or PNG files. All text must be live, editable `Text+` clips on tracks `V4`, `V2`, and `V5`.
- **Token Optimization:** Offload batch timeline and caption construction to `scripts/build_resolve_timeline.py`. Do not waste conversation context tokens calling MCP title insertion 80 times in a row.
- **Transparent MOV/PNG is strictly limited to complex non-text graphics:** (e.g. multi-frame hand-drawn Lottie vectors, particle canvas wipes) when not natively feasible in Fusion.
- On first use of any library, open its LICENSE and record the name, version, and license in `licenses.md`.
- Record all versions (including DaVinci Resolve build & edition) in `engine_log.md`.

---

## 1. Primary NLE & Native Title Engines

### DaVinci Resolve + `davinci-resolve` MCP ✔ (Primary NLE, Color, Fusion, Fairlight & Deliver)
- **What:** Professional non-linear editing, Fusion node compositing, Color page grading, Fairlight audio mixing, and Deliver queue rendering controlled live via the 37 tools of the `davinci-resolve` MCP server.
- **Edition Notes:**
  - **DaVinci Resolve Studio:** Supports external Python scripting natively, AI Magic Mask (`timeline_item_color.create_magic_mask`), AI Voice Isolation (`timeline.set_voice_isolation_state`), Smart Reframe, and AI audio classification/transcription.
  - **DaVinci Resolve Free (up to 21.0.x):** Accessible via the in-app bridge (`Workspace > Scripts > resolve_bridge`). Where Studio-only AI features (Magic Mask, Voice Isolation) are unavailable, fall back automatically to the open-source Python tools below (DeltaKeyer / SAM 2 / BiRefNet for roto; FFmpeg `afftdn` / DeepFilterNet for audio cleanup; `faster-whisper` for transcription).
- **Use here for:** Project & bin organization, clip marker annotations, story assembly, J/L-cuts & audio crossfades, alternating jump-cut punch-ins, native `ST1` subtitles, native `Text+` lower-third word-by-word captions (`V4`), behind-subject focus words (`V2`), speaker matte cutout (`V3`), lower-thirds (`V5`), Color Groups & CDL/LUT/DRX/DCTL grading, Fairlight stem ducking, Deliver queue MP4/ProRes rendering, and native `.drp` / `.drt` / `.xml` / `.fcpxml` / `.otio` exports.

---

## 2. Speech, Transcription & Take Analysis

| Task | Tool | License | Notes |
|---|---|---|---|
| Word-level transcription | **faster-whisper** (model: `large-v3`) ◇ + Resolve `media_pool_item.transcribe_audio` ✔ | MIT / BSD-2 | Autonomous non-English transcription producing `assembly_words.json` (`word`, `start`, `end`, `confidence`). |
| Speech vs. silence / VAD | **Silero VAD** ◇ + Resolve `edit_engine.plan_silence_ripple` ✔ | MIT | Detect pre-roll, dead air, and classify `.mp3`/`.wav` files as music vs. speech. |
| Non-English formatting | `scripts/srt_tools.py` | Python stdlib | Formats captions per user choice in Step 0 Intake (Native script, Romanized, English translation, Dual captions). |
| SRT chunking, diffing, alignment | `scripts/srt_tools.py` (`difflib`) | Python stdlib | Deterministic Phase 2.5 SRT diffing, word alignment, and Phase 3 1–2 word chunking with micro-gap bridging. |

---

## 3. Audio & Fairlight Mastering

- **Resolve Native Audio Tools:**
  - `timeline(action="set_voice_isolation_state", params={"track_index": 1, "enabled": true})` (Resolve Studio AI Voice Isolation).
  - `timeline(action="normalize_audio_level", params={"item_ids": [...]})` (Resolve 21.1+ clip normalization).
- **Dual-Stem + Raw-Reference Fairlight Layout:**
  - Resolve's Scripting API does not honour per-clip volume/EQ property writes (`timeline.safe_set_audio_properties` returns `known_limitation`).
  - Therefore, generate mastered stems with FFmpeg (`afftdn`, highpass `80Hz`, presence EQ, `loudnorm` to `-14 LUFS` social / `-16 to -18 LUFS` web, `-1 dBTP` true peak, and `sidechaincompress` ducking music `12–18 dB` under speech) and place them on **`A1_DIALOGUE_CLEAN`** and **`A3_MUSIC_BED`**, while keeping the raw frame-matched camera audio cuts disabled on **`A2_RAW_DIALOGUE_DISABLED`** for manual Fairlight tweaking.
- **pyloudnorm** ◇ (MIT) & **librosa** ◇ (ISC): Verify integrated LUFS / true peak and detect music beats so cuts and graphic hits can align to bars/beats.

---

## 4. Subject Separation & Roto (`V3_SPEAKER_ROTO_MATTE`)

| Tool | License | Best Use Case in Resolve Pipeline |
|---|---|---|
| **Resolve AI Magic Mask** (`timeline_item_color.create_magic_mask`) ✔ | Resolve Studio | **Primary choice on Resolve Studio.** Native person/object mask directly on the `V3_SPEAKER_ROTO_MATTE` clip (`mode="F"` or `"B"`). |
| **DeltaKeyer (Fusion)** ✔ | Built into Resolve | Native, fast chroma/luma keyer in Fusion when shooting against a studio wall/backdrop (e.g. blue wall in Razorpay shoot). |
| **SAM 2 (Segment Anything 2)** ◇ | Apache-2.0 | High-accuracy temporal video segmentation when on Resolve Free or when hair/fast movement needs an external matte. |
| **BiRefNet** ◇ | MIT | High-resolution portrait matting with crisp hair detail; combine with temporal smoothing. |

---

## 5. NLE Interchange & Project Archiving

- **Resolve Native Exports (`project_manager` & `timeline`):**
  - `.drp` (Full DaVinci Resolve Project): `project_manager(action="safe_project_export", params={"with_stills_and_luts": true})`
  - `.drt` (DaVinci Resolve Timeline): `timeline(action="export_timeline_checked", params={"export_type": "DRT"})`
  - `.xml` (FCP7 XML for Premiere/Resolve): `timeline(action="export_timeline_checked", params={"export_type": "FCP_7_XML"})`
  - `.fcpxml` (FCPXML v1.9+ for Final Cut/Resolve): `timeline(action="export_timeline_checked", params={"export_type": "FCPXML_1_9"})`
  - `.otio` (OpenTimelineIO): `timeline(action="export_timeline_checked", params={"export_type": "OTIO"})`
- **Cross-Validation (`scripts/export_xml.py`):**
  - Uses `opentimelineio` and `opentimelineio-plugins` (`pip install opentimelineio opentimelineio-plugins`) to independently build and validate `.xml` and `.fcpxml` from `approved_cut_list.json`.

---

## 6. Color Grading (`timeline_item_color`, `graph`, `color_group`, `lut`, `dctl`)

- **Color Groups (`color_group`):** Group all cuts from the same camera (`V1` and `V3` roto) so shared Pre-Clip (Log-to-Rec.709 CST / Input LUT) and Post-Clip (Look) nodes stay identical across every cut.
- **CDL & DRX (`timeline_item_color`):** Apply primary balance via `safe_set_cdl` (`slope`, `offset`, `power`, `saturation`) and reusable still grades via `safe_apply_drx`, saving non-destructive grade versions (`add_version`).
- **DCTL (`dctl`) & LUTs (`lut`):** Validate (`dctl.validate_native`) and install custom DCTLs or 3D LUTs under Resolve's master LUT root.
- **Verification (`gallery_stills` & `timeline_frame`):** Capture before/after frame-exact images (`timeline_frame(action="capture", params={"quality": "frame"})` and `gallery_stills(action="grab_and_export")`).

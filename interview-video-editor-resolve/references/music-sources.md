# Music & SFX Sourcing Reference (DaVinci Resolve MCP)

**Legend:** ✔ = license terms confirmed in at least one 2026 source during research (secondary sources, so open the site's own license page before relying on it); ◇ = from general knowledge, verify on the site.

## 1. Step One: Look in the User's Directory (ALWAYS FIRST)

1. Search the project folder, the footage folder, and common sub-folders (`music`, `audio`, `bgm`, `soundtrack`, `assets`) up to 3 levels deep for `.mp3` and `.wav` files using `scripts/find_music.py`:
   ```bash
   python3 scripts/find_music.py "$PROJECT_DIR" "$FOOTAGE_DIR" --maxdepth 3
   ```
2. Classify each hit as **music** or **voice recording** and ignore the voice recordings:
   - Skip a file that shares its name stem with a video file (sidecar audio), or sits in the footage folders with interview/testimonial/mic-style names.
   - Run `ffprobe` for duration and a quick speech check (Silero VAD or a short Whisper pass). If a large share of the file is speech, it is a voice recording, not music.
   - Prefer files in folders named `music`/`audio`/`bgm`/`soundtrack`, or with names like `"track"`, `"bgm"`, `"theme"`, `"score"`.
3. Decide:
   - **One music file found:** It is the music. Use **ONLY** this file. Do not search any library and do not mix in other music.
   - **Several music files found:** Ask the user which one to use, unless the user already named it. Use only the chosen one.
   - **None found:** Go to §2.
   - **A file exists but the user said "no music":** Ask once to confirm before using or ignoring it.
4. Record the result (path, duration, or `"none"`) in `project_brief.md`, and write `music_license.md` with `"user-supplied file, license/rights are the user's responsibility"`.

**Using the user's file:** Trim, loop (crossfade at a beat/bar boundary), fade in/out, and duck it under speech as needed. Editing it for length is fine; adding other music is not.

---

## 2. If No Music File Was Provided and the User Wants Music

1. Get the mood/genre and destination platform (Intake Q7 and Q11) and the attribution setting (Q13).
2. Pick 2–3 candidate tracks from the libraries in §3, in the stated order. Match mood, tempo, and energy to the video; prefer instrumental, low-density tracks that will not fight the voice (steady rhythm, no vocals, few dynamic swells).
3. For each candidate, open the track page and read its license. Reject it if:
   - it is NonCommercial (`NC`) or No-Derivatives (`ND`) and the video is commercial or will be edited
   - it is YouTube-only and the destination is not YouTube
   - it requires attribution and the user said no (Q13)
   - the license text is missing or unclear
4. Download the `.mp3` or `.wav` with the browser tool the way a person would. No bulk downloading, no scraping. If the site needs a login or CAPTCHA you cannot complete, ask the user to download the chosen track into the project folder.
5. Write `music_license.md` (template in §5) and add attribution text to `credits.md` if required.
6. Tell the user which track you picked, why, and its license, and offer the runner-up.

---

## 3. Free Music Libraries (Use in This Order)

| # | Library | URL | License / Terms | Attribution | Notes for the Agent |
|---|---|---|---|---|---|
| 1 | **Pixabay Music** ✔ | pixabay.com/music | Pixabay Content License: free for commercial and non-commercial use | Not required | Largest no-credit catalog. Some artists register tracks in Content ID, so a claim is possible: save the track page/license screenshot as proof. Filter by mood, genre, duration. |
| 2 | **Mixkit** (Envato) ✔ | mixkit.co/free-stock-music | Mixkit License: free commercial and personal use | Not required | Smaller but curated, no account needed. Also has free SFX. |
| 3 | **Free Music Archive** ✔ | freemusicarchive.org | Per-track Creative Commons | Depends on the track | Filter to CC0 (no credit) or CC BY (credit). Avoid NC and ND for commercial or edited use. Open each track's license line. |
| 4 | **YouTube Audio Library** ✔ | studio.youtube.com (Audio Library) | YouTube Audio Library License | Some tracks require it (per track flag) | Needs a YouTube account. Licensed for use on YouTube; do not use for other platforms unless the track's terms say so. Use only when the destination is YouTube. |
| 5 | **Uppbeat** ✔ | uppbeat.io | Free plan license | Required on free plan | Free tier is for personal projects and social platforms with attribution; check terms for client/commercial use. Credit exactly as the site instructs. |
| 6 | **Musopen** ✔ | musopen.org | Public-domain classical recordings | Not required (check each recording) | Classical/orchestral only. |
| 7 | **Incompetech** (Kevin MacLeod) ◇ | incompetech.com | Creative Commons BY | Required | Large catalog; credit text is provided on each track page. |
| 8 | **ccMixter** ◇ | ccmixter.org | Per-track Creative Commons | Depends on the track | Check each track's license. |
| 9 | **Bensound** ◇ | bensound.com | Free with attribution; paid license removes it | Required on free | Read the current free-license terms first. |
| 10 | **Pexels** ◇ | pexels.com | Pexels is known mainly for photos and video | n/a | Check whether the site currently offers a music section. If it does not, skip it and use the libraries above. |

**Do not use:**
- **Jamendo** ✔ free tier: free use is non-commercial only; commercial use needs a purchased license.
- Any track from a streaming service, a "no copyright" YouTube channel, or a site with no license text.
- Paid-library previews or watermarked files.

---

## 4. SFX Libraries (Only if the User Asked for Sound Effects)

| Library | URL | License | Notes |
|---|---|---|---|
| **Mixkit SFX** ✔ | mixkit.co/free-sound-effects | Mixkit License, no attribution | Whooshes, hits, risers, UI sounds. |
| **Pixabay Sound Effects** ✔ | pixabay.com/sound-effects | Pixabay Content License | Large selection. |
| **Freesound** ◇ | freesound.org | Per-file CC0 / CC BY / CC BY-NC | Needs an account to download. Pick CC0 or CC BY only. |
| **YouTube Audio Library** ✔ | studio.youtube.com | see §3 | Sound effects tab; YouTube-only terms. |

Keep SFX subtle: whooshes at transition hits, soft impacts on emphasis graphics, all well below the voice (`-18` to `-24 dB` under speech).

---

## 5. `music_license.md` Template

```markdown
# Music license record
- Source: user-supplied file | <library name>
- File: <path>
- Title / artist: <...>
- Track URL: <...>
- License: <license name, link to license text>
- Attribution required: yes/no
- Attribution text: "<exact credit text>"
- Platform restrictions: <none | YouTube only | ...>
- Date accessed: <YYYY-MM-DD>
- Notes: <Content ID warning, runner-up track, etc.>
```

---

## 6. Mixing & Placing Audio in DaVinci Resolve (Fairlight + MCP)

1. **Ensure Project Frame Rate Is Set First:**
   - Standalone `.wav`/`.mp3` files freeze the project's `timelineFrameRate` at import time in DaVinci Resolve. Confirm `timelineFrameRate` is set before calling `media_storage(action="import_to_pool")` into `Master/02_Audio/Music` and `Master/02_Audio/SFX`.
2. **Sidechain Ducking & LUFS Mastering (Overcoming Resolve API Volume Limitations):**
   - Resolve's Scripting API does not honour per-clip volume/EQ property writes (`timeline.safe_set_audio_properties` returns `known_limitation`).
   - Therefore:
     - Master the dialogue track to `-14 LUFS` (social) or `-16` to `-18 LUFS` (web) with true peak `< -1.0 dBTP` and place on **`A1_DIALOGUE_CLEAN`** (and run `timeline(action="normalize_audio_level")` / `set_voice_isolation_state`).
     - Keep the raw unbaked camera dialogue cuts synced to `V1` on **`A2_RAW_DIALOGUE_DISABLED`** (disabled via `timeline(action="set_track_enable", params={"track_type": "audio", "index": 2, "enable": false})`).
     - Trim/loop the music track to the exact timeline duration (looping at a bar boundary with a short crossfade and ending with a `1–3s` fade-out via `timeline_item(action="set_fades")`), pre-duck it `12–18 dB` under speech using FFmpeg `sidechaincompress` keyed against `A1_DIALOGUE_CLEAN`, import into `Master/02_Audio/Music`, and place on **`A3_MUSIC_BED`**.
     - Place individual SFX hits on **`A4_SFX_TRANSITIONS`** at exact transition/graphic frames, gain-staged `-18` to `-24 dB` below speech.
   - Optional: detect tempo/beats with `librosa` and snap graphic entrances or B-roll cuts to land on musical beats.

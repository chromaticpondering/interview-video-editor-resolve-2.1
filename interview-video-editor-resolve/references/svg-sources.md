# SVG / Lottie / Icon / Illustration Sourcing Reference (DaVinci Resolve MCP)

**Legend:** ✔ = license terms confirmed in at least one 2026 source during research (secondary sources, so read the site's own license page before relying on it); ◇ = from general knowledge, verify on the site.

## 1. Sourcing Procedure (Per Planned Element)

1. **Describe the element** from the transcript moment (e.g., "underline under 'trust'", "rising arrow for growth", "heart", "checkmark badge", "speech bubble", "sparkle burst") plus the style notes from the element style reference (stroke weight, corner treatment, doodle vs. geometric, filled vs. outline, palette).
2. **Make 3–5 English search keywords** (the term, synonyms, a style word such as `"hand drawn"`, `"doodle"`, `"outline"`, `"sticker"`).
3. **Search in this order** and stop when a candidate matches the style:
   1. Open-license icon sets (§2) via Iconify's search API or the set's own site
   2. SVG Repo, Pixabay Vectors (§3)
   3. LottieFiles for animated assets (§4)
   4. Illustration libraries (§5)
   5. Attribution-required libraries: Flaticon, Freepik, Storyset, The Noun Project (§6), when the style fits better and attribution is allowed (Intake Q13)
   6. Backgrounds, shapes, and patterns (§7) for backdrops
   7. Emoji/sticker sets (§8)
   8. Author a custom SVG (Rough.js, rough-notation, p5/brush, hand-built paths, or native Resolve Fusion shape/Text+ nodes) when nothing suitable exists
4. **Shortlist 2–3 candidates**, check each asset's license on its page, and pick the one that best matches the reference style and stays consistent with the assets already chosen. Keep one visual language across the video.
5. **Download** the SVG (or Lottie JSON) using the browser tool as a person would. Never bulk-download or scrape. If a download needs a login or CAPTCHA you cannot complete, ask the user to download it into the project folder or pick another source.
6. **Normalize** (§9), animate and convert to a Resolve-ready layer (§10), import into `Master/03_Graphics_SVG_Alpha` via `media_storage(action="import_to_pool")`, and place onto `V2_BEHIND_SUBJECT_GFX` or `V5_FRONT_GFX_TITLES`.
7. **Log** the asset in `asset_log.csv` (§11) and add attribution text to `credits.md` if required.

---

## 2. Open-License Icon Sets (No Attribution; Best for UI-like Glyphs, Arrows, Checks, Hearts, Stars)

| Set | URL | License | Style |
|---|---|---|---|
| **Lucide** ✔ | lucide.dev | ISC | clean outline, consistent stroke |
| **Phosphor Icons** ✔ | phosphoricons.com | MIT | six weights (thin to fill, duotone) |
| **Tabler Icons** ✔ | tabler.io/icons | MIT | 5,000+ outline and filled |
| **Heroicons** ✔ | heroicons.com | MIT | outline/solid |
| **Material Symbols** ✔ | fonts.google.com/icons | Apache-2.0 | Google style, variable weight |
| **Remix Icon** ✔ | remixicon.com | Apache-2.0 | line and fill |
| **Bootstrap Icons** ✔ | icons.getbootstrap.com | MIT | simple glyphs |
| **Iconoir** ✔ | iconoir.com | MIT | outline |
| **Feather** ✔ | feathericons.com | MIT | minimal outline |
| **Iconify** ✔ (aggregator) | iconify.design | varies per icon set (open source) | one API over 100+ sets; each set carries its own license, so read the set's license field before use |

Iconify tip: search endpoint `https://api.iconify.design/search?query=<term>` returns `set:name` identifiers; fetch an SVG with `https://api.iconify.design/<set>/<name>.svg`. Read the set license from `https://api.iconify.design/collection?prefix=<set>`.

---

## 3. Large SVG Search Sites

| Site | URL | License | Notes |
|---|---|---|---|
| **SVG Repo** ✔ | svgrepo.com | open licenses, shown per asset (500,000+ SVGs) | Great discovery. The license differs per asset (CC0, MIT, Apache, CC BY...). Read it and log it. |
| **Pixabay Vectors** ◇ | pixabay.com/vectors | Pixabay Content License | Free commercial use; filter to SVG. |
| **Openclipart** ◇ | openclipart.org | public domain (CC0) | Older clip-art style; verify the site's current status and terms. |
| **Public Domain Vectors** ◇ | publicdomainvectors.org | public domain | Verify per asset. |
| **Wikimedia Commons** ◇ | commons.wikimedia.org | varies per file | Strictly check each file's license; avoid logos/trademarks. |

---

## 4. Animated Assets (Lottie)

| Site | URL | License | Notes |
|---|---|---|---|
| **LottieFiles** ✔ | lottiefiles.com | Lottie Simple License for public animations: commercial use, no attribution | Filter to Free. Download Lottie JSON (or dotLottie). Play with lottie-web's SVG renderer and seek frame-by-frame. Check each animation's page for its license and creator. |
| **Flaticon animated icons** ✔ | flaticon.com | free downloads need the attribution link; paid removes it | Credit exactly as Flaticon instructs. |
| **IconScout** ◇ | iconscout.com | free tier licenses vary per asset (some no-attribution, some attribution) | Read each asset's license badge. |
| **LottieFlow / Lordicon** ◇ | lottieflow.com / lordicon.com | free tiers vary | Verify free-tier terms before use. |

---

## 5. Illustration Libraries (Scenes, Characters, Spot Illustrations)

| Site | URL | License | Attribution |
|---|---|---|---|
| **unDraw** ✔ | undraw.co | free for commercial use; custom permissive license | not required; read undraw.co/license |
| **Storyset (Freepik)** ✔ | storyset.com | free with attribution; premium removes it | required on free |
| **DrawKit** ✔ | drawkit.com | free packs plus paid | check each pack's license |
| **Open Peeps / Open Doodles / Humaaans** ◇ | openpeeps.com / opendoodles.com / humaaans.com | typically CC0 | verify per site |
| **Streamline free packs** ✔ | streamlinehq.com | free with attribution (per sources); paid for more | verify pack license |

---

## 6. Attribution-Required Libraries (Use When Style Fits and Q13 Allows Credits)

| Site | URL | Free-Tier Terms | What to Do |
|---|---|---|---|
| **Flaticon** ✔ | flaticon.com | Free use requires attribution; Premium removes it. | Copy the attribution text into `credits.md`. Prefer SVG downloads. |
| **Freepik** ✔ | freepik.com | Free license requires attribution; avoid Premium assets. | Credit the author and Freepik as instructed on the asset page. |
| **Storyset** ✔ | storyset.com | see §5 | Credit as instructed. |
| **The Noun Project** ◇ | thenounproject.com | free downloads under CC BY with attribution | Credit creator and title as shown. |

---

## 7. Backgrounds, Shapes, Blobs and Patterns (◇ Verify Each Site's Terms)

| Site | URL | Use |
|---|---|---|
| **Haikei** | haikei.app | generators for waves, blobs, layered shapes (SVG export) |
| **SVG Backgrounds** | svgbackgrounds.com | repeating patterns and backdrops |
| **Hero Patterns** | heropatterns.com | subtle tiling patterns (typically CC BY 4.0, so credit) |
| **Blobmaker** | blobmaker.app | organic blob shapes |

---

## 8. Emoji and Sticker Sets (◇ Verify Licenses)

| Set | URL | License (check) | Notes |
|---|---|---|---|
| **Fluent Emoji (Microsoft)** | github.com/microsoft/fluentui-emoji | MIT | flat SVG variants available |
| **Noto Emoji (Google)** | github.com/googlefonts/noto-emoji | Apache-2.0 / OFL | monochrome SVG and color assets |
| **Twemoji** | github.com/jdecked/twemoji | CC BY 4.0 graphics | attribution required |

---

## 9. Normalizing Assets Before Animation

1. Run **SVGO** to strip metadata, editor junk, and unused `defs`. Keep `viewBox`; remove fixed `width`/`height`. Keep IDs needed for animation.
2. Reject or fix SVGs that embed raster images, reference external files/fonts, or use unsupported filters. Convert text to outlines.
3. **Recolor** to the brand palette.
4. **Match stroke weight and corner treatment** to the element style reference (`stroke-linecap`, `stroke-linejoin`, `vector-effect: non-scaling-stroke`).
5. Save the cleaned SVG in `assets/svg/<element>-<source>-<id>.svg`.

---

## 10. Bringing Animated SVGs onto the DaVinci Resolve Timeline

DaVinci Resolve edits best when every motion graphic is an independent, repositionable clip on `V2_BEHIND_SUBJECT_GFX` (behind the roto'd speaker) or `V5_FRONT_GFX_TITLES` (in front of the speaker):

1. **Method A — Pre-Keyed ProRes 4444 Alpha Clips (Best for GSAP DrawSVG / MorphSVG / Rough.js / Lottie):**
   - Animate the normalized SVG on a transparent canvas (`rgba(0,0,0,0)`) at the timeline's exact resolution and FPS (or a crisp callout canvas positioned in frame coordinates) using GSAP (`DrawSVGPlugin`, `MorphSVGPlugin`, `CustomEase` overshoot) or `lottie-web` (`goToAndStop(frame, true)`).
   - Export to **ProRes 4444 with Alpha (`yuva444p10le`)**:
     ```bash
     ffmpeg -y -r <FPS> -i frames/%05d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le -vendor apl0 assets/overlays/<element>_<id>.mov
     ```
   - Import into Resolve's `Master/03_Graphics_SVG_Alpha` bin via `media_storage(action="import_to_pool")` and place at the exact beat `record_frame` via `media_pool(action="append_to_timeline")` on `track_index: 5` (front) or `track_index: 2` (behind speaker).
   - Fine-tune scale or position directly in Resolve at any time via `timeline_item(action="set_transform")`!

2. **Method B — Native Resolve Fusion Comps (`fusion_comp`):**
   - Insert a Fusion composition (`timeline(action="insert_fusion_composition")`) on `V5` or `V2`, add shape/text/transform/glow tools via `fusion_comp(action="safe_add_tool")`, and keyframe via `fusion_comp(action="add_keyframe")`.

3. **Visual Check in Resolve:**
   - Capture the frame at peak animation via `timeline_frame(action="capture", params={"timecode": ..., "quality": "preview"})` to confirm clean alpha transparency, legibility, and zero collision with the speaker's face or captions.

---

## 11. `asset_log.csv`

One row per downloaded or generated asset:

```csv
asset_id,element,source_site,asset_url,creator,license,attribution_required,attribution_text,date_accessed,file_path,resolve_track,used_at_timecode
```

## 12. Hard Rules

- Prefer no-attribution sources; use attribution-required ones only when needed and when Q13 allows.
- Never use brand logos, trademarked characters, or assets marked editorial-only or Premium-only.
- Never remove or hide required attribution.
- Do not bulk-scrape or hammer a site; download only what the video uses.
- Re-check a site's license page at the time of use; terms change.

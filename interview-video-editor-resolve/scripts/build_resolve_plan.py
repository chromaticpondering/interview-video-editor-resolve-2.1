#!/usr/bin/env python3
"""build_resolve_plan.py - Convert a cut list JSON into frame-exact DaVinci Resolve MCP payloads (v2.1).

Solves the key DaVinci Resolve scripting coordinate traps & v2.1 requirements:
1. Source frames (`start_frame`, `end_frame`) are counted in the SOURCE clip's native FPS (`source_fps`),
   with `end_frame` EXCLUSIVE (`duration_source_frames = end_frame - start_frame`).
2. Record frames (`record_frame`) on the timeline are counted in the TIMELINE's FPS (`fps`),
   offset by `timeline_start_frame` (default 01:00:00:00 = 3600 * fps) when `record_frame_mode="absolute"`.
3. Consecutive clips from the same `clip_id` (same camera angle) create visible jump cuts unless
   every second consecutive cut alternates a subtle punch-in (`zoom_x: 1.08, zoom_y: 1.08`).
4. Generates punchy 1-2 word caption chunks for Track V4 (with Lower-Third Y coordinates, ultra-tight line spacing,
   pure white text, and micro-gap bridging to prevent black flicker).
5. Detects or maps high-impact focus words for Track V2 (behind speaker) and Track V3 (speaker matte).

Input cut list JSON format:
{
  "name": "04_Master_Publish",
  "fps": 25.0,
  "timeline_start_tc": "01:00:00:00",
  "punch_in_zoom": 1.08,
  "punch_in_y": -15.0,
  "audio_fade_frames": 3,
  "font": "Mulish",
  "focus_words": [
    {"word": "TWICE", "start_time": 7.60, "end_time": 8.88, "size": 0.22, "y": 0.64}
  ],
  "clips": [
    {
      "clip_id": "uuid-from-resolve-media-pool",
      "source": "/abs/path/cam_a.mp4",
      "source_fps": 25.0,
      "src_in": 12.40,
      "src_out": 19.80,
      "speaker": "Speaker 1",
      "beat": "hook",
      "text": "Optional sentence transcript for this segment",
      "words": [{"word": "Hello", "start": 12.40, "end": 12.75}]
    }
  ]
}
"""
import argparse
import json
import math
import sys


def fmt_srt_tc(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{ss:02d},{ms:03d}"


def frames_to_smpte(frames: int, fps: float) -> str:
    ifps = int(round(fps))
    f = int(round(frames))
    s_total, ff = divmod(f, ifps)
    m_total, ss = divmod(s_total, 60)
    hh, mm = divmod(m_total, 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"


def parse_smpte_to_frames(tc: str, fps: float) -> int:
    parts = [int(x) for x in tc.strip().replace(";", ":").split(":")]
    if len(parts) != 4:
        raise ValueError(f"Expected HH:MM:SS:FF timecode, got {tc!r}")
    hh, mm, ss, ff = parts
    ifps = int(round(fps))
    return ((hh * 3600 + mm * 60 + ss) * ifps) + ff


def build_plan(cut: dict) -> dict:
    tl_name = cut.get("name", "04_Master_Publish")
    tl_fps = float(cut.get("fps", 25.0))
    start_tc = cut.get("timeline_start_tc", "01:00:00:00")
    tl_start_frame = int(cut.get("timeline_start_frame", parse_smpte_to_frames(start_tc, tl_fps)))
    zoom = float(cut.get("punch_in_zoom", 1.08))
    pos_y = float(cut.get("punch_in_y", -15.0))
    fade_frames = int(cut.get("audio_fade_frames", 3))
    font_name = cut.get("font", "Mulish")

    clip_infos_relative = []
    clip_infos_absolute = []
    transform_calls = []
    fade_calls = []
    marker_calls = []
    review_cues = []
    retimed_words = []

    record_offset_frames = 0
    prev_clip_id = None
    consecutive_same_cam = 0

    for idx, c in enumerate(cut.get("clips", [])):
        clip_id = c["clip_id"]
        src_fps = float(c.get("source_fps") or tl_fps)
        src_in_s = float(c["src_in"])
        src_out_s = float(c["src_out"])
        if src_out_s <= src_in_s:
            raise ValueError(f"Clip {idx} ({clip_id}): src_out ({src_out_s}) <= src_in ({src_in_s})")

        # Source frame coordinates in source_fps (end_frame exclusive)
        src_start_frame = int(round(src_in_s * src_fps))
        src_end_frame = int(round(src_out_s * src_fps))
        src_dur_frames = max(1, src_end_frame - src_start_frame)

        # Duration on timeline in timeline_fps
        dur_seconds = src_dur_frames / src_fps
        tl_dur_frames = max(1, int(round(dur_seconds * tl_fps)))

        rel_record_frame = record_offset_frames
        abs_record_frame = tl_start_frame + record_offset_frames

        clip_infos_relative.append({
            "clip_id": clip_id,
            "start_frame": src_start_frame,
            "end_frame": src_end_frame,
            "record_frame": rel_record_frame,
        })
        clip_infos_absolute.append({
            "clip_id": clip_id,
            "start_frame": src_start_frame,
            "end_frame": src_end_frame,
            "record_frame": abs_record_frame,
            "record_frame_mode": "absolute",
        })

        # Audio crossfade on each clip
        fade_calls.append({
            "tool": "timeline_item",
            "action": "set_fades",
            "params": {
                "track_type": "audio",
                "track_index": 1,
                "item_index": idx,
                "fade_in": fade_frames,
                "fade_out": fade_frames,
            },
        })

        # Same-shot jump-cut detection -> alternate subtle punch-in on V1
        if clip_id == prev_clip_id:
            consecutive_same_cam += 1
        else:
            consecutive_same_cam = 0
        prev_clip_id = clip_id

        is_punched_in = (consecutive_same_cam % 2 == 1)
        if is_punched_in:
            transform_calls.append({
                "tool": "timeline_item",
                "action": "set_transform",
                "params": {
                    "track_type": "video",
                    "track_index": 1,
                    "item_index": idx,
                    "zoom_x": zoom,
                    "zoom_y": zoom,
                    "position_x": 0.0,
                    "position_y": pos_y,
                },
                "reason": f"Conceal same-camera jump cut at item_index={idx} ({frames_to_smpte(abs_record_frame, tl_fps)})",
            })

        # Beat marker if present
        if c.get("beat"):
            marker_calls.append({
                "tool": "timeline_markers",
                "action": "add",
                "params": {
                    "frame": rel_record_frame,
                    "color": "Cyan" if c["beat"].lower() == "hook" else "Green",
                    "name": f"Beat: {c['beat']}",
                    "note": c.get("text", "")[:120],
                },
            })

        # Retime words from source time to assembled timeline time
        tl_in_s = rel_record_frame / tl_fps
        tl_out_s = (rel_record_frame + tl_dur_frames) / tl_fps
        clip_words = []
        for w in c.get("words", []):
            ws_src = float(w["start"])
            we_src = float(w["end"])
            if we_src < src_in_s or ws_src > src_out_s:
                continue
            ws_tl = max(tl_in_s, tl_in_s + (ws_src - src_in_s))
            we_tl = min(tl_out_s, tl_in_s + (we_src - src_in_s))
            rw = {
                "word": w["word"],
                "start": round(ws_tl, 3),
                "end": round(max(ws_tl + 0.04, we_tl), 3),
                "source_start": ws_src,
                "source_end": we_src,
                "clip_id": clip_id,
                "source": c.get("source", ""),
                "confidence": w.get("confidence", 1.0),
            }
            clip_words.append(rw)
            retimed_words.append(rw)

        cue_id = f"C{idx + 1:03d}"
        cue_text = c.get("text") or " ".join(w["word"] for w in clip_words)
        review_cues.append({
            "cue_id": cue_id,
            "index": idx + 1,
            "timeline_start": round(tl_in_s, 3),
            "timeline_end": round(tl_out_s, 3),
            "timeline_start_tc": frames_to_smpte(abs_record_frame, tl_fps),
            "timeline_end_tc": frames_to_smpte(abs_record_frame + tl_dur_frames, tl_fps),
            "record_start_frame": abs_record_frame,
            "record_end_frame": abs_record_frame + tl_dur_frames,
            "clip_id": clip_id,
            "source": c.get("source", ""),
            "source_fps": src_fps,
            "src_in": src_in_s,
            "src_out": src_out_s,
            "src_start_frame": src_start_frame,
            "src_end_frame": src_end_frame,
            "speaker": c.get("speaker", ""),
            "punched_in": is_punched_in,
            "text": cue_text.strip(),
            "words": clip_words,
        })

        record_offset_frames += tl_dur_frames

    total_duration_s = round(record_offset_frames / tl_fps, 3)

    # -------------------------------------------------------------
    # Build 1-2 Word Punchy Caption Chunks for Track V4
    # -------------------------------------------------------------
    caption_chunks = []
    i = 0
    while i < len(retimed_words):
        w1 = retimed_words[i]
        w1_txt = w1["word"].strip()
        has_punct = any(w1_txt.endswith(p) for p in [",", ".", "?", "!"])
        if not has_punct and i + 1 < len(retimed_words):
            w2 = retimed_words[i + 1]
            gap = w2["start"] - w1["end"]
            dur = w2["end"] - w1["start"]
            if gap < 0.35 and dur < 1.8:
                sf = tl_start_frame + int(round(w1["start"] * tl_fps))
                ef = tl_start_frame + int(round(w2["end"] * tl_fps))
                caption_chunks.append({
                    "start_frame": sf,
                    "end_frame": ef,
                    "line1": w1_txt,
                    "line2": w2["word"].strip(),
                    "text": f"{w1_txt} {w2['word'].strip()}",
                    "font": font_name,
                })
                i += 2
                continue

        sf = tl_start_frame + int(round(w1["start"] * tl_fps))
        ef = tl_start_frame + int(round(w1["end"] * tl_fps))
        caption_chunks.append({
            "start_frame": sf,
            "end_frame": ef,
            "line1": w1_txt,
            "line2": "",
            "text": w1_txt,
            "font": font_name,
        })
        i += 1

    # Bridge micro-gaps (< 0.22s = ~5 frames) to prevent black flicker between consecutive chunks
    max_gap_frames = int(round(0.22 * tl_fps))
    for idx in range(len(caption_chunks) - 1):
        cur = caption_chunks[idx]
        nxt = caption_chunks[idx + 1]
        gap_frames = nxt["start_frame"] - cur["end_frame"]
        if 0 < gap_frames <= max_gap_frames:
            cur["end_frame"] = nxt["start_frame"]

    # -------------------------------------------------------------
    # Build Behind-Subject Focus Words for Track V2 & V3
    # -------------------------------------------------------------
    focus_words = []
    if cut.get("focus_words"):
        for fw in cut["focus_words"]:
            st = float(fw.get("start_time", 0.0))
            et = float(fw.get("end_time", st + 1.2))
            focus_words.append({
                "word": fw["word"].upper(),
                "start_frame": tl_start_frame + int(round(st * tl_fps)),
                "end_frame": tl_start_frame + int(round(et * tl_fps)),
                "size": float(fw.get("size", 0.20)),
                "y": float(fw.get("y", 0.64)),
                "font": font_name,
            })
    else:
        # Heuristic: highlight numbers / metrics or uppercase words > 3 letters
        for w in retimed_words:
            raw = w["word"].strip(".,!?:;\"'()[]{}")
            if any(char.isdigit() for char in raw) or (raw.isupper() and len(raw) >= 3):
                sf = tl_start_frame + int(round(w["start"] * tl_fps))
                ef = tl_start_frame + int(round((w["end"] + 0.4) * tl_fps))
                focus_words.append({
                    "word": raw.upper(),
                    "start_frame": sf,
                    "end_frame": ef,
                    "size": 0.20,
                    "y": 0.64,
                    "font": font_name,
                })
        # Limit to max 6 focus words
        focus_words = focus_words[:6]

    return {
        "timeline_name": tl_name,
        "timeline_fps": tl_fps,
        "timeline_start_tc": start_tc,
        "timeline_start_frame": tl_start_frame,
        "total_timeline_frames": record_offset_frames,
        "total_duration_seconds": total_duration_s,
        "clip_count": len(clip_infos_relative),
        "font": font_name,
        "clip_infos_relative": clip_infos_relative,
        "clip_infos_absolute": clip_infos_absolute,
        "transform_calls": transform_calls,
        "fade_calls": fade_calls,
        "marker_calls": marker_calls,
        "review_manifest": review_cues,
        "retimed_words": retimed_words,
        "caption_chunks": caption_chunks,
        "focus_words": focus_words,
    }


def write_review_srt(cues: list) -> str:
    blocks = []
    for c in cues:
        if not c["text"]:
            continue
        spk = f"[{c['speaker']}] " if c.get("speaker") else ""
        blocks.append(
            f"{c['index']}\n"
            f"{fmt_srt_tc(c['timeline_start'])} --> {fmt_srt_tc(c['timeline_end'])}\n"
            f"{spk}{c['text']}\n"
        )
    return "\n".join(blocks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cutlist", help="Path to input cut list JSON")
    ap.add_argument("--out", required=True, help="Output Resolve plan JSON path")
    ap.add_argument("--out-review-srt", help="Optional output path for sentence-level review_v1.srt")
    ap.add_argument("--out-review-manifest", help="Optional output path for review_manifest_v1.json")
    ap.add_argument("--out-words", help="Optional output path for retimed words.json")
    args = ap.parse_args()

    with open(args.cutlist, encoding="utf-8") as f:
        cut = json.load(f)

    plan = build_plan(cut)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    if args.out_review_srt:
        with open(args.out_review_srt, "w", encoding="utf-8") as f:
            f.write(write_review_srt(plan["review_manifest"]))

    if args.out_review_manifest:
        with open(args.out_review_manifest, "w", encoding="utf-8") as f:
            json.dump(plan["review_manifest"], f, ensure_ascii=False, indent=2)

    if args.out_words:
        with open(args.out_words, "w", encoding="utf-8") as f:
            json.dump(plan["retimed_words"], f, ensure_ascii=False, indent=2)

    print(
        f"Built Resolve plan v2.1: {plan['clip_count']} A-roll clips, "
        f"{len(plan['caption_chunks'])} native caption chunks, "
        f"{len(plan['focus_words'])} behind-subject focus words, "
        f"{plan['total_timeline_frames']} frames ({plan['total_duration_seconds']}s) -> {args.out}"
    )


if __name__ == "__main__":
    main()

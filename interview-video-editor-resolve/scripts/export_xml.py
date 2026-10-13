#!/usr/bin/env python3
"""export_xml.py - export the final cut list as FCP7 XML (Premiere/Resolve) and FCPXML (Final Cut/Resolve).

Requires:  pip install opentimelineio opentimelineio-plugins
Cut list JSON:
{
  "name": "project", "fps": 25,
  "clips": [{"source": "/abs/path/a.mp4", "src_in": 12.5, "src_out": 20.3,
             "source_duration": 612.0, "name": "A_take2", "has_audio": true}],
  "markers": [{"before_clip": 3, "name": "removed: back take", "note": "00:01:10-00:01:25 src b.mp4"}]
}
Times are seconds. source_duration is optional (ffprobe is used if available, else src_out).
"""
import argparse, copy, json, os, shutil, subprocess, sys
from pathlib import Path

try:
    import opentimelineio as otio
except ImportError:
    sys.exit("opentimelineio is not installed. Run: pip install opentimelineio opentimelineio-plugins")


def probe_duration(path):
    if not shutil.which("ffprobe") or not os.path.exists(path):
        return None
    try:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], text=True)
        return float(out.strip())
    except Exception:
        return None


def rt(sec, fps):
    return otio.opentime.RationalTime(round(sec * fps), fps)


def build(cut):
    fps = float(cut.get("fps", 25))
    tl = otio.schema.Timeline(name=cut.get("name", "cut"))
    tl.global_start_time = otio.opentime.RationalTime(0, fps)
    vt = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    at = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
    tl.tracks.append(vt)
    tl.tracks.append(at)
    markers = {}
    for m in cut.get("markers", []):
        markers.setdefault(int(m["before_clip"]), []).append(m)
    for i, c in enumerate(cut["clips"]):
        src = c["source"]
        dur = c.get("source_duration") or probe_duration(src) or c["src_out"]
        ref = otio.schema.ExternalReference(
            target_url=Path(src).resolve().as_uri() if os.path.isabs(src) or os.path.exists(src) else src,
            available_range=otio.opentime.TimeRange(rt(0, fps), rt(dur, fps)))
        sr = otio.opentime.TimeRange(rt(c["src_in"], fps), rt(c["src_out"] - c["src_in"], fps))
        clip = otio.schema.Clip(name=c.get("name") or Path(src).stem, media_reference=ref, source_range=sr)
        for m in markers.get(i, []):
            clip.markers.append(otio.schema.Marker(name=m["name"], marked_range=otio.opentime.TimeRange(rt(0, fps), rt(0, fps)),
                                                  comment=m.get("note", "")))
        vt.append(clip)
        if c.get("has_audio", True):
            at.append(copy.deepcopy(clip))
    return tl, fps


def total_frames(tl):
    return max(sum(c.source_range.duration.value for c in t if isinstance(c, otio.schema.Clip)) for t in tl.tracks)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cutlist"); ap.add_argument("--out-dir", default="."); ap.add_argument("--formats", default="fcp_xml,fcpx_xml")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args()
    cut = json.load(open(a.cutlist, encoding="utf-8"))
    tl, fps = build(cut)
    name = cut.get("name", "cut")
    ext = {"fcp_xml": ".xml", "fcpx_xml": ".fcpxml"}
    os.makedirs(a.out_dir, exist_ok=True)
    exp_clips, exp_frames = len(cut["clips"]), total_frames(tl)
    rc = 0
    for fmt in [f.strip() for f in a.formats.split(",") if f.strip()]:
        path = os.path.join(a.out_dir, f"{name}_cuts{ext[fmt]}")
        try:
            otio.adapters.write_to_file(tl, path, adapter_name=fmt)
        except Exception as e:
            print(f"[{fmt}] write failed: {e}"); rc = 1; continue
        print(f"[{fmt}] wrote {path}")
        if a.validate:
            try:
                back = otio.adapters.read_from_file(path, adapter_name=fmt)
                vclips = [c for t in back.tracks if t.kind == "Video" for c in t if isinstance(c, otio.schema.Clip)]
                vframes = sum(c.source_range.duration.rescaled_to(fps).value for c in vclips)
                ok = len(vclips) == exp_clips and abs(vframes - exp_frames) <= 1
                print(f"[{fmt}] validate: clips {len(vclips)}/{exp_clips}, frames {vframes:.0f}/{exp_frames:.0f} -> {'OK' if ok else 'MISMATCH'}")
                rc = rc or (0 if ok else 1)
            except Exception as e:
                print(f"[{fmt}] validate could not re-read the file: {e}"); rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()

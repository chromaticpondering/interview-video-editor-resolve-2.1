#!/usr/bin/env python3
"""find_music.py - scan folders for .mp3/.wav files and classify them as music, voice or unknown.

Usage: python3 find_music.py DIR [DIR ...] [--maxdepth 3]
Prints JSON. Heuristics only: for 'unknown' files run a speech check (Silero VAD / short Whisper pass).
"""
import argparse, json, os, shutil, subprocess

VIDEO = {".mp4", ".mov", ".mxf", ".mkv", ".avi", ".m4v", ".mts", ".webm", ".braw", ".r3d"}
MUSIC_DIRS = {"music", "audio", "bgm", "soundtrack", "score", "songs", "track", "tracks"}
VOICE_WORDS = ("interview", "testimonial", "mic", "lav", "voice", "vo_", "take", "rec_", "zoom", "tascam", "recording", "rode")
MUSIC_WORDS = ("music", "bgm", "track", "theme", "score", "song", "instrumental", "background")


def duration(path):
    if not shutil.which("ffprobe"):
        return None
    try:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], text=True).strip())
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dirs", nargs="+"); ap.add_argument("--maxdepth", type=int, default=3)
    a = ap.parse_args()
    found, video_stems = {}, set()
    for root in a.dirs:
        base = os.path.abspath(root); depth0 = base.rstrip(os.sep).count(os.sep)
        for dp, dn, fn in os.walk(base):
            if dp.rstrip(os.sep).count(os.sep) - depth0 >= a.maxdepth:
                dn[:] = []
            for f in fn:
                stem, ext = os.path.splitext(f)
                if ext.lower() in VIDEO:
                    video_stems.add((dp, stem.lower()))
                elif ext.lower() in (".mp3", ".wav"):
                    found[os.path.join(dp, f)] = dp
    results = []
    for path, dp in sorted(found.items()):
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        parts = {p.lower() for p in dp.split(os.sep)}
        reasons, cls = [], "unknown"
        if (dp, stem) in video_stems:
            cls, _ = "voice", reasons.append("shares its name with a video file (sidecar audio)")
        elif any(w in stem for w in VOICE_WORDS):
            cls, _ = "voice", reasons.append("file name looks like a voice recording")
        elif parts & MUSIC_DIRS:
            cls, _ = "music", reasons.append("sits in a folder named like music/audio/bgm")
        elif any(w in stem for w in MUSIC_WORDS):
            cls, _ = "music", reasons.append("file name looks like music")
        else:
            reasons.append("no strong signal; run a speech check")
        results.append({"path": path, "duration_s": duration(path), "classification": cls, "reasons": reasons})
    music = [r for r in results if r["classification"] == "music"]
    unknown = [r for r in results if r["classification"] == "unknown"]
    verdict = ("use_this_file" if len(music) == 1 and not unknown else
               "ask_user_which" if len(music) + len(unknown) > 1 else
               "check_unknown_with_vad" if unknown else "none_found")
    print(json.dumps({"verdict": verdict, "files": results}, indent=2))


if __name__ == "__main__":
    main()

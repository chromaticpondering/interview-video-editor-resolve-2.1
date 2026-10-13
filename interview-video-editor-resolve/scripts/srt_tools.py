#!/usr/bin/env python3
"""srt_tools.py - stdlib-only SRT helpers for the interview-video-editor skill.

Subcommands
  chunk     words.json -> short display-caption chunks (SRT + JSON with per-word timing)
  diff      old.srt new.srt -> classified changes (deleted/edited/trimmed/split/merged/added)
  align     words.json + edited text -> per-word timestamps for the edited text
  validate  check an SRT is well-formed (UTF-8, ordered, no overlaps, within duration)

words.json is a list of {"word": str, "start": seconds, "end": seconds}.
"""
import argparse, difflib, json, re, sys, unicodedata

TC = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{1,3})")


def parse_tc(s):
    m = TC.match(s.strip())
    if not m:
        raise ValueError(f"bad timecode: {s!r}")
    h, mi, se, ms = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")) / 1000


def fmt_tc(t):
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.split("\n")
        ti = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if ti is None:
            continue
        a, b = lines[ti].split("-->")
        cues.append({
            "index": len(cues) + 1,
            "start": parse_tc(a),
            "end": parse_tc(b.strip().split()[0]),
            "text": "\n".join(lines[ti + 1:]).strip(),
        })
    return cues


def write_srt(cues):
    out = []
    for i, c in enumerate(cues, 1):
        out.append(f"{i}\n{fmt_tc(c['start'])} --> {fmt_tc(c['end'])}\n{c['text']}\n")
    return "\n".join(out)


def norm(tok):
    """Case/punctuation-insensitive key. Keeps combining marks so Indic scripts compare correctly."""
    return "".join(ch for ch in tok if not unicodedata.category(ch).startswith(("P", "S"))).casefold()


def ws(text):
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------- chunk
JOINERS = {"a", "an", "the", "of", "to", "in", "on", "at", "for", "and", "or", "but", "with", "my", "our", "your", "is", "are"}


def chunk_words(words, max_words=5, min_words=2, max_chars=30, gap=0.35, hold=0.12):
    chunks, cur = [], []

    def flush():
        if cur:
            chunks.append(list(cur))
            cur.clear()

    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        text = " ".join(x["word"] for x in cur)
        end_punct = bool(re.search(r"[.!?\u2026\u0964]$", w["word"]))
        soft = bool(re.search(r"[,;:\u2013\u2014]$", w["word"]))
        long_gap = nxt is not None and nxt["start"] - w["end"] > gap
        too_many = len(cur) >= max_words
        too_long = nxt is not None and len(text) + 1 + len(nxt["word"]) > max_chars
        joiner = norm(w["word"]) in JOINERS and nxt is not None and not (long_gap or end_punct) and len(cur) <= max_words
        if nxt is None or end_punct or long_gap or ((too_many or too_long) and not joiner) or (soft and len(cur) >= min_words):
            flush()
    flush()

    # merge one-word orphans into a neighbour when it fits
    merged = []
    for ch in chunks:
        if merged and len(ch) == 1 and len(merged[-1]) < max_words:
            joined = " ".join(x["word"] for x in merged[-1] + ch)
            close = ch[0]["start"] - merged[-1][-1]["end"] <= gap
            if len(joined) <= max_chars and close:
                merged[-1] = merged[-1] + ch
                continue
        merged.append(ch)

    result = []
    for k, ch in enumerate(merged):
        start = ch[0]["start"]
        end = ch[-1]["end"] + hold
        if k + 1 < len(merged):
            end = min(end, merged[k + 1][0]["start"])
        result.append({"start": start, "end": max(end, ch[-1]["end"]), "text": " ".join(x["word"] for x in ch), "words": ch})
    return result


# ---------------------------------------------------------------- diff
def overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def word_ops(old_text, new_text):
    a, b = ws(old_text).split(), ws(new_text).split()
    sm = difflib.SequenceMatcher(a=[norm(x) for x in a], b=[norm(x) for x in b], autojunk=False)
    ops = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            # same word but user changed case/punctuation counts as an edit
            if a[i1:i2] != b[j1:j2]:
                ops.append({"op": "replace", "old": " ".join(a[i1:i2]), "new": " ".join(b[j1:j2])})
        else:
            ops.append({"op": tag, "old": " ".join(a[i1:i2]), "new": " ".join(b[j1:j2])})
    return ops


def diff_cues(old, new, tol=0.15):
    o2n = {i: [] for i in range(len(old))}
    n2o = {j: [] for j in range(len(new))}
    for i, o in enumerate(old):
        for j, n in enumerate(new):
            if overlap(o["start"], o["end"], n["start"], n["end"]) > 0:
                o2n[i].append(j)
                n2o[j].append(i)
    changes, unchanged, seen_merge = [], 0, set()
    for i, o in enumerate(old):
        js = o2n[i]
        base = {"old_index": o["index"], "old_start": o["start"], "old_end": o["end"], "old_text": o["text"]}
        if not js:
            changes.append({**base, "type": "deleted", "cut_ranges": [[o["start"], o["end"]]]})
            continue
        if len(js) > 1:
            kept = [new[j] for j in js]
            gaps = []
            if kept[0]["start"] - o["start"] > tol:
                gaps.append([o["start"], kept[0]["start"]])
            for a, b in zip(kept, kept[1:]):
                if b["start"] - a["end"] > tol:
                    gaps.append([a["end"], b["start"]])
            if o["end"] - kept[-1]["end"] > tol:
                gaps.append([kept[-1]["end"], o["end"]])
            changes.append({**base, "type": "split", "new_cues": [{"start": n["start"], "end": n["end"], "text": n["text"]} for n in kept],
                            "cut_ranges": gaps})
            continue
        j = js[0]
        n = new[j]
        if len(n2o[j]) > 1:
            if j in seen_merge:
                continue
            seen_merge.add(j)
            changes.append({"type": "merged", "old_indexes": [old[k]["index"] for k in n2o[j]],
                            "old_text": " / ".join(old[k]["text"] for k in n2o[j]),
                            "new_cue": {"start": n["start"], "end": n["end"], "text": n["text"]}})
            continue
        kinds, cut = [], []
        if ws(o["text"]) != ws(n["text"]):
            kinds.append("text_edited")
        if n["start"] - o["start"] > tol:
            kinds.append("trimmed"); cut.append([o["start"], n["start"]])
        if o["end"] - n["end"] > tol:
            if "trimmed" not in kinds:
                kinds.append("trimmed")
            cut.append([n["end"], o["end"]])
        if o["start"] - n["start"] > tol or n["end"] - o["end"] > tol:
            kinds.append("extended_beyond_original")
        if not kinds:
            unchanged += 1
            continue
        ch = {**base, "type": "+".join(kinds), "new_start": n["start"], "new_end": n["end"], "new_text": n["text"], "cut_ranges": cut}
        if "text_edited" in kinds:
            ops = word_ops(o["text"], n["text"])
            ch["word_ops"] = ops
            if ops and all(op["op"] == "delete" for op in ops):
                ch["words_deleted_only"] = True
        changes.append(ch)
    for j, n in enumerate(new):
        if not n2o[j]:
            changes.append({"type": "added", "new_start": n["start"], "new_end": n["end"], "new_text": n["text"],
                            "note": "No matching speech in the old SRT; cannot be created from footage. Ask whether it is meant as an on-screen text card."})
    counts = {}
    for c in changes:
        counts[c["type"]] = counts.get(c["type"], 0) + 1
    return {"unchanged": unchanged, "counts": counts, "changes": changes}


def diff_markdown(rep, old_n, new_n):
    L = ["# SRT diff report", "", f"- Old cues: {old_n}", f"- New cues: {new_n}", f"- Unchanged: {rep['unchanged']}"]
    for k, v in sorted(rep["counts"].items()):
        L.append(f"- {k}: {v}")
    L += ["", "| # | Type | Old (timecode / text) | New / action |", "|---|---|---|---|"]
    for n, c in enumerate(rep["changes"], 1):
        t = c["type"]
        if t == "deleted":
            L.append(f"| {n} | deleted | {fmt_tc(c['old_start'])}-{fmt_tc(c['old_end'])} {c['old_text']!r} | cut this range |")
        elif t == "added":
            L.append(f"| {n} | added | - | {fmt_tc(c['new_start'])} {c['new_text']!r} (flag: no matching speech) |")
        elif t == "merged":
            L.append(f"| {n} | merged | {c['old_text']!r} | {c['new_cue']['text']!r} |")
        elif t == "split":
            L.append(f"| {n} | split | {c['old_text']!r} | {len(c['new_cues'])} cues; cut ranges: {len(c['cut_ranges'])} |")
        else:
            act = "; ".join(f"{op['op']}: {op['old']!r} -> {op['new']!r}" for op in c.get("word_ops", [])) or "timing change"
            cuts = ", ".join(f"{fmt_tc(a)}-{fmt_tc(b)}" for a, b in c.get("cut_ranges", []))
            L.append(f"| {n} | {t} | {fmt_tc(c['old_start'])} {c['old_text']!r} | {act}{' | cut ' + cuts if cuts else ''} |")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- align
def align_words(old_words, new_text):
    new_tokens = ws(new_text).split()
    sm = difflib.SequenceMatcher(a=[norm(w["word"]) for w in old_words], b=[norm(t) for t in new_tokens], autojunk=False)
    out = []

    def spread(tokens, s, e, source):
        total = sum(max(1, len(t)) for t in tokens)
        t0 = s
        for t in tokens:
            d = (e - s) * max(1, len(t)) / total
            out.append({"word": t, "start": round(t0, 3), "end": round(t0 + d, 3), "source": source})
            t0 += d

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                ow = old_words[i1 + k]
                out.append({"word": new_tokens[j1 + k], "start": ow["start"], "end": ow["end"], "source": "kept"})
        elif tag == "replace":
            spread(new_tokens[j1:j2], old_words[i1]["start"], old_words[i2 - 1]["end"], "replaced")
        elif tag == "insert":
            n = j2 - j1
            prev_end = old_words[i1 - 1]["end"] if i1 > 0 else (old_words[i1]["start"] if i1 < len(old_words) else 0.0)
            next_start = old_words[i1]["start"] if i1 < len(old_words) else prev_end
            e = next_start if next_start - prev_end >= 0.08 * n else prev_end + 0.08 * n
            spread(new_tokens[j1:j2], prev_end, e, "interpolated")
        # delete: dropped
    return out


# ---------------------------------------------------------------- validate
def validate_srt(path, duration=None, max_line=None):
    errors, warns = [], []
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        errors.append("file is not valid UTF-8")
        text = raw.decode("utf-8", "replace")
    cues = parse_srt(text)
    if not cues:
        errors.append("no cues found")
    prev_end = 0.0
    for i, c in enumerate(cues, 1):
        if c["end"] <= c["start"]:
            errors.append(f"cue {i}: end <= start")
        if c["start"] < prev_end - 0.001:
            errors.append(f"cue {i}: overlaps previous cue")
        if not c["text"].strip():
            errors.append(f"cue {i}: empty text")
        if max_line:
            for ln in c["text"].split("\n"):
                if len(ln) > max_line:
                    warns.append(f"cue {i}: line longer than {max_line} chars")
        prev_end = max(prev_end, c["end"])
    if duration and cues and cues[-1]["end"] > duration + 0.05:
        errors.append(f"last cue ends at {fmt_tc(cues[-1]['end'])}, after video duration {duration}s")
    return {"cues": len(cues), "errors": errors, "warnings": warns, "ok": not errors}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("chunk"); c.add_argument("words"); c.add_argument("--out", required=True); c.add_argument("--out-json")
    c.add_argument("--max-words", type=int, default=5); c.add_argument("--min-words", type=int, default=2)
    c.add_argument("--max-chars", type=int, default=30); c.add_argument("--gap", type=float, default=0.35)
    d = sp.add_parser("diff"); d.add_argument("old"); d.add_argument("new"); d.add_argument("--out-json"); d.add_argument("--out-md"); d.add_argument("--tol", type=float, default=0.15)
    a = sp.add_parser("align"); a.add_argument("--words", required=True); a.add_argument("--text", required=True); a.add_argument("--out")
    v = sp.add_parser("validate"); v.add_argument("srt"); v.add_argument("--duration", type=float); v.add_argument("--max-line", type=int)
    args = ap.parse_args()

    if args.cmd == "chunk":
        words = json.load(open(args.words, encoding="utf-8"))
        ch = chunk_words(words, args.max_words, args.min_words, args.max_chars, args.gap)
        open(args.out, "w", encoding="utf-8").write(write_srt(ch))
        if args.out_json:
            json.dump(ch, open(args.out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"{len(ch)} chunks -> {args.out}")
    elif args.cmd == "diff":
        old = parse_srt(open(args.old, encoding="utf-8-sig").read())
        new = parse_srt(open(args.new, encoding="utf-8-sig").read())
        rep = diff_cues(old, new, args.tol)
        if args.out_json:
            json.dump(rep, open(args.out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        md = diff_markdown(rep, len(old), len(new))
        if args.out_md:
            open(args.out_md, "w", encoding="utf-8").write(md)
        print(md)
    elif args.cmd == "align":
        words = json.load(open(args.words, encoding="utf-8"))
        res = align_words(words, args.text)
        s = json.dumps(res, ensure_ascii=False, indent=2)
        (open(args.out, "w", encoding="utf-8").write(s) if args.out else print(s))
    elif args.cmd == "validate":
        rep = validate_srt(args.srt, args.duration, args.max_line)
        print(json.dumps(rep, indent=2))
        sys.exit(0 if rep["ok"] else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""grades.json の判定を採点用csvの point(M) / comment(N) 列へ反映する。

usage:
    python3 scripts/build_csv.py rounds/01k

前提: <round>/grades.json と、<round>/work/ 以下に answer.csv がある。
      （answer.csv が別置きの場合は --csv で指定）
出力: <round>/採点済_<問題名>.csv （UTF-8 BOM）
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def find_csv(rd: Path) -> Path:
    for pat in ("work/**/answer.csv", "*.csv", "work/**/*.csv"):
        for p in sorted(rd.glob(pat)):
            if "sjis" in p.name.lower() or p.name.startswith("採点済"):
                continue
            if p.name in ("comments.csv",):
                continue
            return p
    sys.exit(f"採点用csvが見つからない: {rd}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("round_dir")
    ap.add_argument("--csv", help="採点用csvのパス（自動検出しない場合）")
    args = ap.parse_args()

    rd = Path(args.round_dir)
    src = Path(args.csv) if args.csv else find_csv(rd)
    grades = json.loads((rd / "grades.json").read_text(encoding="utf-8"))

    with open(src, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    title = next((r[1] for r in rows if r and r[0] == "問題名"), rd.name)
    hdr = next(i for i, r in enumerate(rows) if r and r[0] == "id")
    col = {n: i for i, n in enumerate(rows[hdr])}
    i_uid, i_pt, i_cm = col["USERID"], col["point"], col["comment"]

    hit = 0
    for r in rows[hdr + 1:]:
        if len(r) <= i_cm:
            continue
        g = grades.get(r[i_uid].strip())
        if not g:
            continue
        hit += 1
        qs = g["q"]
        r[i_pt] = str(sum(v[0] for v in qs.values()))
        notes = [f"{k}. {v[1]}" for k, v in sorted(qs.items(), key=lambda x: int(x[0])) if v[1]]
        r[i_cm] = "\n".join(notes) if notes else "全問正解"

    dst = rd / f"採点済_{title}.csv"
    with open(dst, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, quoting=csv.QUOTE_MINIMAL).writerows(rows)

    missing = set(grades) - {r[i_uid].strip() for r in rows[hdr + 1:] if len(r) > i_uid}
    print(f"wrote {dst}  ({hit}/{len(grades)} 名を反映)")
    if missing:
        print(f"警告: csvに見つからない学籍番号 {sorted(missing)}")


if __name__ == "__main__":
    main()

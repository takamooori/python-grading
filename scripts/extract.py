#!/usr/bin/env python3
"""提出物zipを展開し、各ipynbのコードと保存済み出力をテキストで書き出す。

usage:
    python3 scripts/extract.py rounds/01k
    python3 scripts/extract.py rounds/01k --range 1 10   # 学生1〜10人目のみ

前提: <round>/ に提出物zipが1つ置かれている。
出力: <round>/work/ に展開、<round>/extracted.txt に抽出結果。
"""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


def decode_name(s: str) -> str:
    """ファイル名の #Uxxxx 形式のUnicodeエスケープを復元する。"""
    return re.sub(r"#U([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


def cell_outputs(cell: dict) -> tuple[list[str], bool]:
    """セルの出力を文字列化し、(出力リスト, エラー有無) を返す。"""
    outs, has_error = [], False
    for o in cell.get("outputs", []):
        t = o["output_type"]
        if t == "stream":
            outs.append("".join(o["text"]).strip())
        elif t == "error":
            has_error = True
            outs.append(f"!!ERROR {o['ename']}: {str(o.get('evalue'))[:80]}")
        elif t == "execute_result":
            txt = "".join(o.get("data", {}).get("text/plain", "")).strip()
            outs.append(f"[セル戻り値] {txt}")
        elif t == "display_data":
            outs.append("[画像/表示データ]")
    return outs, has_error


def parse_notebook(path: Path) -> list[dict]:
    """ipynbを読み、問題番号ごとのコードと出力を返す。

    問題番号はmarkdownセルの見出し（k01_3 / p01_2 など）から拾う。
    コードセルの順番では数えない（セル欠落でズレるため）。
    """
    nb = json.loads(path.read_text(encoding="utf-8"))
    items, current = [], None
    for c in nb.get("cells", []):
        src = "".join(c.get("source", []))
        if c.get("cell_type") == "markdown":
            m = re.search(r"[kp]0?\d+_(\d+)", src)
            if m:
                current = m.group(1)
        elif c.get("cell_type") == "code":
            if not src.strip() and not c.get("outputs"):
                continue
            outs, err = cell_outputs(c)
            items.append({
                "q": current,
                "code": src.rstrip(),
                "outputs": outs,
                "error": err,
                "executed": c.get("execution_count") is not None,
                "imports": re.findall(r"^\s*(?:import|from)\s+(\w+)", src, re.M),
            })
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("round_dir")
    ap.add_argument("--range", nargs=2, type=int, metavar=("FROM", "TO"))
    args = ap.parse_args()

    rd = Path(args.round_dir)
    zips = sorted(rd.glob("*.zip"))
    if not zips:
        sys.exit(f"zipが見つからない: {rd}/*.zip")

    work = rd / "work"
    work.mkdir(exist_ok=True)
    with zipfile.ZipFile(zips[0]) as z:
        z.extractall(work)

    files = sorted(p for p in work.rglob("*.ipynb") if not p.name.startswith("."))
    others = sorted(p for p in work.rglob("*") if p.suffix.lower() in (".html", ".py", ".pdf", ".txt"))

    if args.range:
        lo, hi = args.range
        files = files[lo - 1:hi]

    lines = [f"# 抽出結果: {rd.name}  提出ipynb {len(files)}件"]
    if others:
        lines.append("")
        lines.append("## ipynb以外の提出（採点不能の可能性 → 要判断リストへ）")
        for p in others:
            lines.append(f"- {decode_name(p.name)}")

    for p in files:
        parts = p.name.split("_")
        uid = parts[1] if len(parts) > 1 else "?"
        name = decode_name("_".join(parts[2:4])) if len(parts) > 3 else ""
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"## {uid} {name}")
        items = parse_notebook(p)
        found = [it["q"] for it in items if it["q"]]
        lines.append(f"検出された問題: {found}")
        for it in items:
            lines.append(f"--- Q{it['q']}"
                         + ("" if it["executed"] else "  [未実行]")
                         + (f"  [import: {','.join(it['imports'])}]" if it["imports"] else ""))
            lines.append(it["code"])
            lines.append("  >> " + (" / ".join(it["outputs"]) if it["outputs"] else "(出力なし)"))

    out = rd / "extracted.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}  ({len(files)} notebooks)")


if __name__ == "__main__":
    main()

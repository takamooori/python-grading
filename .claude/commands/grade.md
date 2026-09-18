---
description: 指定した回の課題を採点し、採点済みcsvと要判断リストを出力する
argument-hint: <回のID 例 01p>
allowed-tools: Bash(python3:*), Bash(ls:*), Read, Write, Edit
---

`rounds/$1` の課題を採点する。CLAUDE.md の判定基準を必ず適用すること。

## 手順

1. `ls rounds/$1` で入力を確認する。zipが無ければ止めて報告する
2. `python3 scripts/extract.py rounds/$1` を実行し、`rounds/$1/extracted.txt` を読む
   - 提出者が20人を超える場合は `--range` で10人ずつに区切り、
     バッチごとに読んで判定する（一度に全員読むと後半の判断がブレる）
3. 模範解答ipynb（`rounds/$1/*_ans.ipynb`）があれば読み、各問の要件を把握する
4. 判定基準に従って全員・全問を採点し、`rounds/$1/grades.json` を書く
   - 提出ipynbは再実行しない。保存済み出力だけで判定する
   - 判断に迷うものは減点せず、`rounds/$1/要判断リスト.txt` に
     学籍番号・問題番号・論点・暫定点を書く
   - `extracted.txt` 冒頭の「ipynb以外の提出」も要判断リストに載せる
5. `python3 scripts/build_csv.py rounds/$1` で採点済csvを生成する
6. 結果を表で報告する（学籍番号・氏名・点数・減点理由）。
   要判断リストがあれば件数と内容を要約する

## 裁定後

裁定が返ってきたら `grades.json` を修正して `build_csv.py` を再実行し、
CLAUDE.md の「裁定履歴」に日付付きで追記する。解消した要判断リストは削除する。

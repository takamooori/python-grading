# セットアップ手順

## 1. Claude Code を入れる

未導入なら公式手順に従う: https://docs.claude.com/en/docs/claude-code/overview

## 2. このフォルダを配置して git 管理下に置く

```bash
cd ~/work            # 好きな場所へ
# ta-grading/ をここに展開
cd ta-grading
git init
git add -A
git commit -m "chore: TA採点プロジェクト初期構成"
```

`.gitignore` で zip・展開先・extracted.txt は除外してある。
リポジトリに残るのは判定基準（CLAUDE.md）・スクリプト・grades.json・採点済csv。

## 3. 回ごとの採点

```bash
mkdir -p rounds/01p
# 大学システムからDLしたzipを rounds/01p/ に置く
# 模範解答があれば rounds/01p/ に置く（任意）

claude            # ta-grading/ 直下で起動
```

起動したら:

```
/grade 01p
```

一覧が出たら要判断リストを見て裁定を返す。
修正版csvと、裁定履歴を追記した CLAUDE.md が出力される。

## 4. 提出

`rounds/01p/採点済_<問題名>.csv` を大学システムの
「レポート/記述式問題の採点」画面からアップロードする。

## 5. 記録

```bash
git add -A && git commit -m "01p 採点完了"
```

判定基準の変化が差分で追える。

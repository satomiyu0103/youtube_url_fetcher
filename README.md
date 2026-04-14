# YouTube URL Fetcher

YouTubeチャンネルを定期監視し、新規動画URLを自動検出して **NotebookLM 登録用テキストを生成する RPA ツール**。

---

## 目的

- 指定した YouTube チャンネルの最新動画を取得
- 取得済み履歴（CSV）と比較して**新規動画のみを抽出**
- NotebookLM へ一括登録するための URL リスト（TXT）を生成
- Windows タスクスケジューラで定期自動実行

---

## 技術スタック

| ライブラリ | バージョン | 用途 |
|---|---|---|
| Python | 3.12+ | 実行環境 |
| yt-dlp | 2025.12.8+ | YouTube 動画メタデータ取得（API 不要） |
| pandas | 2.3.3+ | CSV 操作・差分チェック |
| uv | - | パッケージ管理 |
| ipykernel | 7.1.0+ | Jupyter Notebook 対応 |

---

## ディレクトリ構成

```
youtube_url_fetcher/
├── main/
│   ├── main.py               # メイン処理フロー
│   ├── config.py             # チャンネル設定・パス管理
│   ├── test.py               # 未使用（import のみ）
│   └── modules/
│       ├── get_url.py        # YouTube 動画情報取得
│       ├── data_manager.py   # 履歴 CSV の読込・差分抽出・追記
│       ├── write_new_list.py # NotebookLM 用 TXT 生成
│       └── error_log.py      # エラーログ記録
├── data/
│   ├── history.csv           # 取得済み動画の履歴（自動生成）
│   ├── latest_update.txt     # 最新実行時の出力（自動生成）
│   └── error_log.txt         # エラーログ（自動生成）
├── draft/                    # 試行版・プロトタイプ（参照用）
├── doc/
│   └── Instraction.md
├── pyproject.toml
└── README.md
```

---

## セットアップ

```powershell
# 仮想環境の作成と依存関係のインストール
uv sync

# 仮想環境を有効化
.venv\Scripts\Activate.ps1
```

---

## 使い方

```powershell
# main/ ディレクトリから実行
python main/main.py
```

### 監視チャンネルの変更

`main/config.py` の `TARGET_CHANNELS` を編集する。

```python
TARGET_CHANNELS = [
    "https://www.youtube.com/@チャンネル名/videos",
    # 複数チャンネルを追加可能
]
```

### 取得件数の変更

```python
FETCH_COUNT = 10  # 0 にすると全件取得（非常に遅い）
```

---

## 処理フロー

```
config.py（チャンネルURL・取得件数）
    ↓
get_url：yt-dlp で最新動画を取得 → DataFrame
    ↓
data_manager：history.csv と比較して新規動画を抽出
    ↓
  新規あり → history.csv に追記 + latest_update.txt 生成
  新規なし → 「新規なし」を latest_update.txt に記録
    ↓
例外発生時 → error_log.txt にタイムスタンプ付きで記録
```

---

## 出力ファイル

### `data/latest_update.txt`

NotebookLM へ貼り付けるための URL リスト。

```
【新規動画リスト】NotebookLM登録用
以下のURLをコピーしてNotebookLMのソースに追加してください。

--- [ Copy URLs Below ] ---
https://www.youtube.com/watch?v=xxxxx
https://www.youtube.com/watch?v=yyyyy

--- [ Details ] ---
[20260101] 動画タイトル1
[20260101] 動画タイトル2
```

### `data/history.csv`

動画 ID ベースで重複チェックを行う履歴ファイル。

| video_id | title | url | upload_date | channel_name | fetched_at |
|---|---|---|---|---|---|
| xxxxx | タイトル | https://... | 20260101 | チャンネル名 | 2026-01-01 00:00:00 |

---

## 注意事項

- `FETCH_COUNT = 0` は**全件取得モード**のため実行が非常に遅くなる。通常は `5〜10` を推奨。
- `data/` 配下のファイルは初回実行時に自動生成される。
- `draft/` フォルダはモジュール化前の試行版であり、本番実行には使用しない。

import os
from pathlib import Path

# --- 1. パスの設定（タスクスケジューラ対策 & Notebook対応） ---
try:
    # 通常のPythonファイル(.py)として実行された場合
    # mainフォルダの一つ上(fetch_youtube)をプロジェクトルートとする
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    # Jupyter Notebookなどで実行された場合
    BASE_DIR = Path.cwd()

# データフォルダの場所
DATA_DIR = BASE_DIR / "data"

# 各種ファイルの保存場所（絶対パス）
CSV_PATH = DATA_DIR / "history.csv"
TXT_PATH = DATA_DIR / "latest_update.txt"
LOG_PATH = DATA_DIR / "error_log.txt"

# フォルダが存在しない場合は自動作成する（安全策）
if not DATA_DIR.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# --- 2. YouTube設定 ---

# 対象チャンネルリスト（URLをカンマ区切りで複数記述可能）
TARGET_CHANNELS = [
    "https://www.youtube.com/@RPACommunity/videos"  # RPAコミュニティ
    # "https://www.youtube.com/@pythonvtuber9917/videos"  # サプーチャンネル
    # "https://www.youtube.com/@GoogleJapan/videos",  # 例：Google Japan
    # "https://www.youtube.com/@AnotherChannel/videos", # 追加したい場合
]

# 1回のチェックで取得する最新動画の数（各チャンネルごと）
# 毎週実行なら「5〜10」あれば十分です
FETCH_COUNT = 0

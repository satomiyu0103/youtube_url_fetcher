from pathlib import Path

# --- 1. パスの設定（タスクスケジューラ対策 & Notebook対応） ---
try:
    # 通常のPythonファイル(.py)として実行された場合
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    # Jupyter Notebookなどで実行された場合
    BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = DATA_DIR / "error_log.txt"


# --- 2. YouTube設定 ---

# チャンネル名（ファイル名に使用）: URL の辞書形式で定義
# 追加する場合は "名前": "URL" の形式で記述する
CHANNELS = {
    "RPACommunity": "https://www.youtube.com/@RPACommunity/videos",
    # "GoogleJapan":  "https://www.youtube.com/@GoogleJapan/videos",
    # "Supu":         "https://www.youtube.com/@pythonvtuber9917/videos",
}

# 2回目以降の取得件数（初回は自動的に全件取得になる）
# 毎週実行なら 5〜10 で十分
FETCH_COUNT = 10

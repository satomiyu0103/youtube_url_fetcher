import pandas as pd
from pathlib import Path


def write(new_videos: pd.DataFrame, txt_path: Path) -> None:
    """NotebookLM登録用テキストを書き出す（上書き）。"""
    with open(txt_path, "w", encoding="utf-8") as f:
        if new_videos.empty:
            f.write("新規動画はありません。\n")
            return

        f.write("【新規動画リスト】NotebookLM登録用\n")
        f.write("以下のURLをコピーしてNotebookLMのソースに追加してください。\n\n")

        f.write("--- [ Copy URLs Below ] ---\n")
        for url in new_videos["url"]:
            f.write(f"{url}\n")

        f.write("\n--- [ Details ] ---\n")
        for _, row in new_videos.iterrows():
            f.write(f"[{row['upload_date']}] {row['title']}\n")

def create_output(new_df, txt_path):
    """
    新規動画リストをテキストファイルに書き出す（上書き）
    NotebookLMコピペ用：URLのみのリスト
    人間確認用：[日付] タイトル
    """
    try:
        with open(txt_path, "w", encoding="utf-8") as f:
            if new_df.empty:
                f.write("新規動画はありません。\n")
                return

            f.write("【新規動画リスト】NotebookLM登録用\n")
            f.write("以下のURLをコピーしてNotebookLMのソースに追加してください。\n\n")

            # 1. URLのみ（コピペ用エリア）
            f.write("--- [ Copy URLs Below ] ---\n")
            for _, row in new_df.iterrows():
                f.write(f"{row['url']}\n")

            f.write("\n")
            f.write("-" * 30 + "\n\n")

            # 2. 詳細情報（人間確認用）
            f.write("--- [ Details ] ---\n")
            for _, row in new_df.iterrows():
                date = row.get("upload_date", "不明")
                title = row.get("title", "タイトルなし")
                f.write(f"[{date}] {title}\n")

    except Exception as e:
        print(f"❌ ファイル書き出しエラー: {e}")

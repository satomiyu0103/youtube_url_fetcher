import datetime


def record_error(error_content, log_path):
    """
    エラー内容をログファイルに追記する
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{now}] {str(error_content)}\n"

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(error_msg)
    except Exception:
        pass  # エラーログの書き込み失敗は無視する

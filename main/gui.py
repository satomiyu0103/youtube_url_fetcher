import sys
import tkinter as tk
from tkinter import messagebox
import threading
import subprocess
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

import config
from modules import fetcher, history, output
import logging

# ---- カラーテーマ（ダーク） ----
BG      = "#1e1e1e"
PANEL   = "#252526"
BORDER  = "#3c3c3c"
TEXT    = "#d4d4d4"
MUTED   = "#858585"
ACCENT  = "#0078d4"
SUCCESS = "#3a9d5d"
DANGER  = "#c0392b"
LOG_BG  = "#0d1117"
LOG_FG  = "#98c379"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube URL Fetcher")
        self.geometry("820x580")
        self.minsize(700, 500)
        self.configure(bg=BG)

        self.channels = dict(config.CHANNELS)
        self._cancel_event = threading.Event()
        self._running = False
        self._build_ui()
        self._on_count_change()  # 初期ヒント表示
        self._refresh_channel_list()

    # ------------------------------------------------------------------ UI構築

    def _build_ui(self):
        hdr = tk.Frame(self, bg=PANEL, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="YouTube URL Fetcher",
                 font=("Segoe UI", 15, "bold"), bg=PANEL, fg=TEXT).pack()
        tk.Label(hdr, text=str(config.DATA_DIR),
                 font=("Segoe UI", 8), bg=PANEL, fg=MUTED).pack()

        body = tk.Frame(self, bg=BG, padx=12, pady=10)
        body.pack(fill="both", expand=True)

        self._build_left(body)
        self._build_right(body)

    def _build_left(self, parent):
        """左カラム: チャンネルリスト + 追加/削除"""
        left = tk.Frame(parent, bg=PANEL, padx=10, pady=10)
        left.pack(side="left", fill="both", padx=(0, 8))

        tk.Label(left, text="チャンネル", font=("Segoe UI", 10, "bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w", pady=(0, 6))

        self.ch_listbox = tk.Listbox(
            left, height=9, width=28,
            bg="#1a1a1a", fg=TEXT,
            selectbackground=ACCENT, selectforeground="white",
            font=("Segoe UI", 10), relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            activestyle="none",
        )
        self.ch_listbox.pack(fill="both", expand=True)
        self.ch_listbox.bind("<<ListboxSelect>>", self._on_select)

        form = tk.Frame(left, bg=PANEL, pady=8)
        form.pack(fill="x")
        for row, (label, attr) in enumerate([("名前", "name_var"), ("URL", "url_var")]):
            tk.Label(form, text=label, font=("Segoe UI", 9),
                     bg=PANEL, fg=MUTED, width=4, anchor="w").grid(
                row=row, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Entry(form, textvariable=var, width=24,
                     font=("Segoe UI", 9), bg="#1a1a1a", fg=TEXT,
                     insertbackground=TEXT, relief="flat",
                     highlightthickness=1, highlightbackground=BORDER).grid(
                row=row, column=1, padx=4, pady=2)

        btn_row = tk.Frame(left, bg=PANEL)
        btn_row.pack(fill="x")
        self._btn(btn_row, "+ 追加", self._add_channel, ACCENT).pack(side="left", padx=(0, 4))
        self._btn(btn_row, "- 削除", self._remove_channel, DANGER).pack(side="left")

    def _build_right(self, parent):
        """右カラム: 設定 + 実行ボタン + ログ"""
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        sett = tk.Frame(right, bg=PANEL, padx=10, pady=10)
        sett.pack(fill="x", pady=(0, 8))
        tk.Label(sett, text="設定", font=("Segoe UI", 10, "bold"),
                 bg=PANEL, fg=TEXT).pack(anchor="w", pady=(0, 6))

        cnt_row = tk.Frame(sett, bg=PANEL)
        cnt_row.pack(anchor="w")
        tk.Label(cnt_row, text="取得件数",
                 font=("Segoe UI", 9), bg=PANEL, fg=MUTED).pack(side="left")
        self.fetch_count_var = tk.IntVar(value=config.FETCH_COUNT)
        self.fetch_count_var.trace_add("write", self._on_count_change)
        tk.Spinbox(cnt_row, from_=0, to=200, textvariable=self.fetch_count_var,
                   width=5, font=("Segoe UI", 10),
                   bg="#1a1a1a", fg=TEXT, buttonbackground=BORDER,
                   relief="flat").pack(side="left", padx=8)
        self.count_hint_var = tk.StringVar()
        tk.Label(cnt_row, textvariable=self.count_hint_var,
                 font=("Segoe UI", 9), bg=PANEL, fg=MUTED).pack(side="left")

        run_frame = tk.Frame(right, bg=BG)
        run_frame.pack(fill="x", pady=(0, 4))

        self.run_all_btn = self._btn(
            run_frame, "▶  全チャンネルを実行", self._run_all, SUCCESS, large=True)
        self.run_all_btn.pack(fill="x", pady=(0, 4))

        self.run_sel_btn = self._btn(
            run_frame, "▷  選択チャンネルを実行", self._run_selected, ACCENT, large=True)
        self.run_sel_btn.configure(state="disabled")
        self.run_sel_btn.pack(fill="x", pady=(0, 4))

        self.open_btn = self._btn(
            run_frame, "  結果ファイルを開く（選択中）", self._open_result, BORDER)
        self.open_btn.configure(state="disabled")
        self.open_btn.pack(fill="x", pady=(0, 4))

        self.cancel_btn = self._btn(
            run_frame, "■  キャンセル", self._cancel_task, DANGER)
        self.cancel_btn.configure(state="disabled")
        self.cancel_btn.pack(fill="x")

        log_frame = tk.Frame(right, bg=PANEL, padx=6, pady=6)
        log_frame.pack(fill="both", expand=True, pady=(8, 0))
        tk.Label(log_frame, text="ログ", font=("Segoe UI", 9, "bold"),
                 bg=PANEL, fg=MUTED).pack(anchor="w")

        self.log_text = tk.Text(
            log_frame, height=10, font=("Consolas", 9),
            bg=LOG_BG, fg=LOG_FG, insertbackground=TEXT,
            relief="flat", state="disabled", wrap="word",
        )
        sb = tk.Scrollbar(log_frame, command=self.log_text.yview, bg=PANEL)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True)

    def _btn(self, parent, text, cmd, bg, large=False):
        return tk.Button(
            parent, text=text, command=cmd,
            bg=bg, fg="white",
            font=("Segoe UI", 11 if large else 9),
            relief="flat", pady=7 if large else 4, padx=10,
            cursor="hand2", activebackground=bg, activeforeground="white",
        )

    # ---------------------------------------------------------------- チャンネル操作

    def _refresh_channel_list(self):
        self.ch_listbox.delete(0, tk.END)
        for name in self.channels:
            csv = config.DATA_DIR / f"history_{name}.csv"
            status = "初回" if not csv.exists() else "差分"
            self.ch_listbox.insert(tk.END, f"  [{status}]  {name}")

    def _add_channel(self):
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        if not name or not url:
            messagebox.showwarning("入力エラー", "名前とURLを両方入力してください。", parent=self)
            return
        if name in self.channels:
            messagebox.showwarning("重複", f"「{name}」はすでに登録されています。", parent=self)
            return
        self.channels[name] = url
        self.name_var.set("")
        self.url_var.set("")
        self._refresh_channel_list()

    def _remove_channel(self):
        sel = self.ch_listbox.curselection()
        if not sel:
            return
        name = self._selected_name(sel[0])
        del self.channels[name]
        self._refresh_channel_list()

    def _selected_name(self, index: int) -> str:
        label = self.ch_listbox.get(index)
        return label.strip().split("]  ", 1)[-1]

    def _open_result(self):
        sel = self.ch_listbox.curselection()
        if not sel:
            messagebox.showinfo("未選択", "リストからチャンネルを選択してください。", parent=self)
            return
        name = self._selected_name(sel[0])
        _, txt_path = config.channel_paths(name)
        if txt_path.exists():
            subprocess.Popen(["notepad.exe", str(txt_path)])
        else:
            messagebox.showinfo("ファイルなし",
                                f"まだ実行されていません。\n{txt_path}", parent=self)

    # ---------------------------------------------------------------- 実行処理

    def _run_all(self):
        self._start_task(list(self.channels.items()))

    def _run_selected(self):
        sel = self.ch_listbox.curselection()
        if not sel:
            messagebox.showinfo("未選択", "実行するチャンネルをリストから選択してください。", parent=self)
            return
        name = self._selected_name(sel[0])
        self._start_task([(name, self.channels[name])])

    def _start_task(self, targets: list):
        self._cancel_event.clear()
        self._running = True
        self._update_button_states()
        threading.Thread(target=self._run_task, args=(targets,), daemon=True).start()

    def _run_task(self, targets: list):
        fetch_count = self.fetch_count_var.get()
        self._log(f"\n{'─' * 38}")
        self._log(f"実行開始  対象: {len(targets)} チャンネル")
        self._log(f"{'─' * 38}")

        for name, url in targets:
            if self._cancel_event.is_set():
                self._log("キャンセルされました。")
                break
            try:
                csv_path, txt_path = config.channel_paths(name)

                hist = history.load(csv_path)
                is_first = hist.empty
                count = 0 if is_first else fetch_count

                self._log(f"\n[{name}] {'初回: 全件取得' if is_first else f'差分チェック: 最新{count}件'}")

                latest = fetcher.fetch(url, count)
                if latest.empty:
                    self._log(f"[{name}] 取得できませんでした。スキップします。")
                    continue

                new_videos = history.filter_new(latest, hist)
                self._log(f"[{name}] 新規: {len(new_videos)}件 / 取得: {len(latest)}件")

                history.append(new_videos, csv_path)
                output.write(new_videos, txt_path)

                self.after(0, self._refresh_channel_list)

            except Exception as e:
                self._log(f"[{name}] ERROR: {e}")
                logging.error(f"[{name}] {e}")

        self._log(f"\n{'─' * 38}")
        self._log("キャンセルされました。" if self._cancel_event.is_set() else "完了")
        self._log(f"{'─' * 38}\n")
        self._running = False
        self.after(0, self._update_button_states)

    def _log(self, msg: str):
        def _write():
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
            self.log_text.configure(state="disabled")
        self.after(0, _write)

    def _cancel_task(self):
        self._cancel_event.set()
        self._log("キャンセルリクエストを送信しました（現在のチャンネル処理完了後に停止します）...")
        self.cancel_btn.configure(state="disabled")

    def _on_select(self, event=None):
        self._update_button_states()

    def _on_count_change(self, *args):
        try:
            val = self.fetch_count_var.get()
            self.count_hint_var.set("件（0 = 全件取得）" if val == 0 else "件")
        except (tk.TclError, AttributeError):
            pass

    def _update_button_states(self):
        has_sel = bool(self.ch_listbox.curselection())
        self.run_all_btn.configure(
            state="disabled" if self._running else "normal",
            text="実行中..." if self._running else "▶  全チャンネルを実行",
        )
        self.run_sel_btn.configure(
            state="disabled" if (self._running or not has_sel) else "normal")
        self.open_btn.configure(
            state="disabled" if (self._running or not has_sel) else "normal")
        self.cancel_btn.configure(
            state="normal" if self._running else "disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
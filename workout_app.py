import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Meiryo'  # 表が文字化けするため対策

CSV_FILE = "workout_data.csv"


def get_default_exercise_map():
    return {
        "プッシュ": ["ベンチプレス", "インクラインベンチプレス", "オーバーヘッドプレス"],
        "プル": ["チンニング", "デッドリフト", "ベントオーバーローイング"],
        "スクワット": ["スクワット", "フロントスクワット", "ブルガリアンスクワット"],
    }


EXERCISE_MAP = get_default_exercise_map()


def build_history_rows(records):
    rows = []
    for row in records:
        if not isinstance(row, dict):
            continue
        rows.append({
            "日付": row.get("日付", ""),
            "種目": row.get("種目", ""),
            "重量": float(row.get("重量", 0) or 0),
            "回数": int(row.get("回数", 0) or 0),
            "セット数": int(row.get("セット数", 0) or 0),
        })
    return rows


def save_record():  # 入力データをCSVに保存
    try:
        workout_date = date_entry.get()
        datetime.strptime(workout_date, "%Y-%m-%d")

        exercise = exercise_var.get()
        weight = float(weight_entry.get())
        reps = int(reps_entry.get())
        sets = int(sets_entry.get())

        volume = weight * reps * sets
        new_row = pd.DataFrame([{
            "日付": workout_date,
            "種目": exercise,
            "重量": weight,
            "回数": reps,
            "セット数": sets,
            "総負荷量": volume,
        }])

        try:
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, new_row], ignore_index=True)
        except FileNotFoundError:
            df = new_row

        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
        show_advice(df, exercise)
        messagebox.showinfo("保存完了", "記録を保存しました。")

    except ValueError:
        messagebox.showerror(
            "入力エラー",
            "日付はYYYY-MM-DDの形式で、重量・回数・セット数は数字で入力してください。",
        )


def update_exercise_options():
    category = category_var.get()
    options = EXERCISE_MAP.get(category, [])
    exercise_cb["values"] = options
    if options:
        exercise_var.set(options[0])
        exercise_cb.set(options[0])


def add_custom_exercise():
    category = category_var.get()
    new_exercise = askstring("種目追加", f"{category} に追加する種目名を入力してください")
    if not new_exercise:
        return

    new_exercise = new_exercise.strip()
    if not new_exercise:
        messagebox.showwarning("入力エラー", "種目名を入力してください。")
        return

    if new_exercise in EXERCISE_MAP.get(category, []):
        messagebox.showinfo("追加済み", "その種目はすでに登録されています。")
        return

    EXERCISE_MAP.setdefault(category, []).append(new_exercise)
    update_exercise_options()
    messagebox.showinfo("追加完了", f"{new_exercise} を {category} に追加しました。")


def show_graph():  # CSVファイルからグラフを作成
    exercise = exercise_var.get()

    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        messagebox.showinfo("データなし", "先に記録を保存してください。")
        return

    target = df[df["種目"] == exercise]

    if target.empty:
        messagebox.showinfo("データなし", "その種目の記録はありません。")
        return

    plt.plot(target["日付"], target["総負荷量"], marker="o")
    plt.title(exercise + "の総負荷量")
    plt.xlabel("日付")
    plt.ylabel("総負荷量")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


def show_history():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        messagebox.showinfo("データなし", "先に記録を保存してください。")
        return

    if df.empty:
        messagebox.showinfo("データなし", "記録がまだありません。")
        return

    history_window = tk.Toplevel(root)
    history_window.title("記録履歴")
    history_window.geometry("700x420")

    columns = ("日付", "種目", "重量", "回数", "セット数", "総負荷量")
    tree = ttk.Treeview(history_window, columns=columns, show="headings")

    for column in columns:
        tree.heading(column, text=column)
        tree.column(column, width=110, anchor="center")

    for _, row in df.iterrows():
        tree.insert(
            "",
            "end",
            values=(
                row["日付"],
                row["種目"],
                row["重量"],
                row["回数"],
                row["セット数"],
                row["総負荷量"],
            ),
        )

    scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True, padx=10, pady=10)


def show_advice(df, exercise):  # 最新二回分と比較してアドバイスを表示。
    target = df[df["種目"] == exercise]
    if len(target) < 2:
        advice_label.config(text="アドバイス：記録を続けましょう。")
        return
    previous = target.iloc[-2]["総負荷量"]
    latest = target.iloc[-1]["総負荷量"]

    if latest > previous:
        advice = "前回より成長しています"
    elif latest < previous:
        advice = "総負荷量が減少しています！"
    else:
        advice = "次回は重量か回数を少し増やしてみましょう。"
    advice_label.config(text="アドバイス：" + advice)


root = tk.Tk()
root.title("筋トレ記録アプリ")
root.geometry("420x500")


tk.Label(root, text="筋トレ記録アプリ", font=("", 16, "bold")).pack(pady=10)

category_var = tk.StringVar(value="プッシュ")
exercise_var = tk.StringVar()


tk.Label(root, text="日付(YYYY-MM-DD)").pack()
date_entry = tk.Entry(root)
date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
date_entry.pack()


tk.Label(root, text="分類").pack(pady=(10, 0))
category_cb = ttk.Combobox(root, textvariable=category_var, values=list(EXERCISE_MAP.keys()), state="readonly")
category_cb.pack()
category_cb.bind("<<ComboboxSelected>>", lambda event: update_exercise_options())


tk.Label(root, text="種目").pack(pady=(10, 0))
exercise_cb = ttk.Combobox(root, textvariable=exercise_var, state="readonly")
exercise_cb.pack()

button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text="種目追加", command=add_custom_exercise).pack(side="left", padx=5)
tk.Button(button_frame, text="グラフ表示", command=show_graph).pack(side="left", padx=5)
tk.Button(button_frame, text="履歴表示", command=show_history).pack(side="left", padx=5)


tk.Label(root, text="重量").pack()
weight_entry = tk.Entry(root)
weight_entry.pack()

tk.Label(root, text="回数").pack()
reps_entry = tk.Entry(root)
reps_entry.pack()

tk.Label(root, text="セット数").pack()
sets_entry = tk.Entry(root)
sets_entry.pack()


tk.Button(root, text="記録する", command=save_record).pack(pady=15)

advice_label = tk.Label(root, text="アドバイス：記録すると表示されます。", wraplength=350)
advice_label.pack(pady=10)

update_exercise_options()
root.mainloop()

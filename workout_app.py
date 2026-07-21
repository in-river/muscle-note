import tkinter as tk
from tkinter import messagebox

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Meiryo'  # 表が文字化けするため対策
from datetime import datetime

CSV_FILE = "workout_data.csv"

def save_record(): # 入力データをエクセルに保存
    try:
        workout_date = date_entry.get() #日付の入力
        
        datetime.strptime(workout_date, "%Y-%m-%d")  # 日付形式のチェック
       
        exercise = exercise_entry.get()
        weight = float(weight_entry.get())
        reps = int(reps_entry.get())
        sets = int(sets_entry.get())

        volume = weight * reps * sets
        new_row = pd.DataFrame([{

        #総負荷量＝重量×回数×セット数で計算
            "日付": workout_date,
            "種目": exercise,
            "重量": weight,
            "回数": reps,
            "セット数": sets,
            "総負荷量": volume
        }])

        try:
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, new_row], ignore_index=True)

        except FileNotFoundError:
            df = new_row

        df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")#　←この部分でエクセルに保存
        show_advice(df, exercise)
        messagebox.showinfo("保存完了", "記録を保存しました。")

    except ValueError:
        messagebox.showerror(
             "入力エラー", 
             "日付はYYYY-MM-DDの形式で、重量・回数・セット数は数字で入力してください。"
        )
        

def show_graph():#CSVファイルからグラフを作成
    exercise = exercise_entry.get()

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


def show_advice(df, exercise):#最新二回分と比較してアドバイスを表示。
    target = df[df["種目"] == exercise]
    if len(target) < 2:
        advice_label.config(text="アドバイス：記録を続けましょう。")
        return
    previous = target.iloc[-2]["総負荷量"]
    latest = target.iloc[-1]["総負荷量"]

    if latest > previous:
        advice = "前回より成長しています。"
    elif latest < previous:
        advice = "疲労が残っている可能性があります。"
    else:
        advice = "次回は重量か回数を少し増やしてみましょう。"
    advice_label.config(text="アドバイス：" + advice)


root = tk.Tk()
root.title("筋トレ記録アプリ")
root.geometry("400x420")

tk.Label(root, text="筋トレ記録アプリ", font=("", 16, "bold")).pack(pady=10)
labels = ["日付(YYYY-MM-DD)", "種目", "重量", "回数", "セット数"]
entries = []

for text in labels:
    tk.Label(root, text=text).pack()
    entry = tk.Entry(root)
    entry.pack()
    entries.append(entry)

date_entry, exercise_entry, weight_entry, reps_entry, sets_entry = entries

tk.Button(root, text="記録する", command=save_record).pack(pady=15)#記録するボタン
tk.Button(root, text="グラフ表示", command=show_graph).pack()#グラフ表示ボタン

advice_label = tk.Label(root, text="アドバイス：記録すると表示されます。", wraplength=350)
advice_label.pack(pady=20)

root.mainloop()

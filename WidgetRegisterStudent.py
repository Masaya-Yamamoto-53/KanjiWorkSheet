# WidgetRegisterStudent.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk


class WidgetRegisterStudent:
    # 生徒登録用のウィジェット作成
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

        # 生徒登録ラベルフレーム
        self.RegisterStudentFrame = tk.LabelFrame(root, padx=2, pady=2, text='生徒登録')
        self.RegisterStudentFrame.grid(row=row, column=column)

        # 生徒登録エントリー
        self.RegisterStudentFrame_Entry = tk.Entry(self.RegisterStudentFrame, width=40)
        self.RegisterStudentFrame_Entry.pack(side=tk.LEFT)

        # 生徒登録ボタン
        self.RegisterStudentFrame_Button = tk.Button(
            self.RegisterStudentFrame,
            text='登録',
            command=self.Event_RegisterStudent
        )
        self.RegisterStudentFrame_Button.pack(side=tk.LEFT)

    # イベント発生条件:「登録」ボタンを押したとき
    # 処理概要:「生徒登録」エントリーに記入した名前を設定ファイルに登録する.
    def Event_RegisterStudent(self):
        self.DebugPrint.print_info('Call: Event_RegisterStudent')

        # 「生徒登録」エントリーが空欄であった場合は,
        # メッセージボックスで名前の入力が必要であることを通知する.
        name = self.get_registered_student_entry()
        if len(name) == 0:
            tk.messagebox.showerror('Error', '名前を入力してください.')

        # 「生徒登録」エントリーに名前の記入がある場合
        else:
            # 「生徒登録」エントリーに記入した名称が既に設定ファイルに登録してある場合,
            # メッセージボックスで既に登録済みであることを通知する.
            if self.UserSettings.chk_registered_student(name):
                tk.messagebox.showerror('Error', '既に登録済みです.')
            # 生徒を設定ファイルに登録する.
            else:
                self.DebugPrint.print_info('生徒(' + name + ')の新規登録を行いました.')
                # 生徒を設定ファイルに登録する.
                self.UserSettings.register_student(name)
                # 生徒を設定ファイルに登録した後に, 登録できたことを伝えるために「生徒登録」エントリーを空欄にする.
                # 煩わしいため, メッセージボックスは使用しない.
                self.del_registered_student_entry()

    # 「生徒登録」エントリーのデータを取得する.
    def get_registered_student_entry(self):
        return self.RegisterStudentFrame_Entry.get()

    # 「生徒登録」エントリーのデータを削除する.
    def del_registered_student_entry(self):
        self.RegisterStudentFrame_Entry.delete('0', 'end')

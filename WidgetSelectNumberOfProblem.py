# WidgetSelectNumberOfProblem.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk
from DebugPrint import DebugPrint
from UserSettings import UserSettings


class WidgetSelectNumberOfProblem:
    def __init__(self, root, row, column):
        self.DebugPrint = DebugPrint(debug=True)  # デバッグ表示クラス
        self.UserSettings = UserSettings()  # ユーザ設定クラス

        # 出題数ラベルフレーム
        self.SelectNumberOfProblemFrame = tk.LabelFrame(root, padx=2, pady=2, text='出題数')
        self.SelectNumberOfProblemFrame.grid(row=row, column=column, sticky=tk.W + tk.N)

        # 出題数エントリー
        self.SelectNumberOfProblemFrame_Value = tk.StringVar()
        self.SelectNumberOfProblemFrame_Value.set('')
        self.SelectNumberOfProblemFrame_Value.trace_add('write', self.Event_ChangeNumberOfProblem)
        self.SelectNumberOfProblemFrame_Entry = tk.Entry(
            self.SelectNumberOfProblemFrame,
            width=10,
            textvariable=self.SelectNumberOfProblemFrame_Value,
            state=tk.DISABLED
        )
        self.SelectNumberOfProblemFrame_Entry.pack(side=tk.LEFT)

    def set_class(self, kanji_worksheet, wg_select_student):
        self.KanjiWorkSheet = kanji_worksheet
        self.WidgetSelectStudent = wg_select_student

    # イベント発生条件:「出題数」エントリーを変更したとき
    # 処理概要:出題数を更新する.
    def Event_ChangeNumberOfProblem(self, var, index, mode):
        self.DebugPrint.print_info('Call: Event_ChangeNumberOfProblem')
        num = self.get_number_of_problem()

        # 選択している生徒が設定ファイルに存在しているとき, 設定ファイルに出題数を保存する.
        name = self.WidgetSelectStudent.get_selected_student_name()
        if self.UserSettings.chk_registered_student(name):
            # 問題数を設定する.
            self.UserSettings.set_number_of_problem(name, num)
            # 設定ファイルを保存する.
            self.UserSettings.save_setting_file()

    # 「出題数」エントリーを設定する.
    def set_number_of_problem(self, value):
        self.SelectNumberOfProblemFrame_Entry.delete('0', 'end')
        self.SelectNumberOfProblemFrame_Entry.insert('end', value)

    # 「出題数」エントリーを取得する.
    def get_number_of_problem(self):
        str = self.SelectNumberOfProblemFrame_Value.get()
        if str.isdigit():
            return int(str)
        else:
            return 1

    # 「出題数」のエントリーを有効にする.
    def enable_number_of_problem_entry(self):
        self.SelectNumberOfProblemFrame_Entry['state'] = tk.NORMAL

    # 「出題数」のエントリーを無効にする.
    def disable_number_of_problem_entry(self):
        self.SelectNumberOfProblemFrame_Entry['state'] = tk.DISABLED

    def update(self, subject):
        if subject.notify_status == subject.kNotify_select_student:
            # 「出題数」のエントリーを有効にする。
            self.enable_number_of_problem_entry()
            # 選択した生徒の出題数を設定する。
            name = subject.get_selected_student_name()
            self.set_number_of_problem(self.UserSettings.get_number_of_problem(name))
        elif subject.notify_status == subject.kNotify_delete_student:
            # 問題数の値をクリアし、入力欄を無効にする。
            self.set_number_of_problem('')
            # 出題数のエントリーを無効にする。
            self.disable_number_of_problem_entry()

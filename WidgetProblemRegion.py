# WidgetProblemRegion.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os
import tkinter as tk

class WidgetProblemRegion:
    def __init__(self, debug, user_settings, root, row, column):
        self.Debug = debug  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

        # 出題範囲選択ラベルフレーム
        self.ProblemRegionFrame = tk.LabelFrame(root, text='出題範囲選択')
        self.ProblemRegionFrame.grid(row=row, column=column, sticky=tk.S+tk.W)

        # 出題範囲選択フレーム左側
        self.ProblemRegionFrame_Lft = tk.Frame(self.ProblemRegionFrame, padx=0, pady=0)
        self.ProblemRegionFrame_Lft.grid(row=0, column=0)

        # 出題範囲選択フレーム右側
        self.ProblemRegionFrame_Rgt = tk.Frame(self.ProblemRegionFrame, padx=0, pady=0)
        self.ProblemRegionFrame_Rgt.grid(row=0, column=1)

        # チェックボタンを作成する.
        frame_list = [
              self.ProblemRegionFrame_Lft
            , self.ProblemRegionFrame_Lft
            , self.ProblemRegionFrame_Lft
            , self.ProblemRegionFrame_Rgt
            , self.ProblemRegionFrame_Rgt
            , self.ProblemRegionFrame_Rgt
        ]
        self.ProblemRegionFrame_Checkbutton_Value = {}
        self.ProblemRegionFrame_Checkbutton = {}
        for key, frame in zip(self.UserSettings.kGradeKeyList, frame_list):
            # チェックボックスの値を作成する.
            self.ProblemRegionFrame_Checkbutton_Value[key] = tk.BooleanVar(value=False)

            # チェックボックスの左側を作成する.
            self.ProblemRegionFrame_Checkbutton[key] = tk.Checkbutton(
                  frame
                , text=key
                , command=self.Event_CheckButton
                , variable=self.ProblemRegionFrame_Checkbutton_Value[key]
                , state=tk.DISABLED
            )
            self.ProblemRegionFrame_Checkbutton[key].pack(side=tk.TOP)

    def set_class(self, wg_select_student):
        self.WidgetSelectStudent = wg_select_student

    # イベント発生条件:「出題範囲選択」チェックボックスを選択したとき
    # 処理概要:チェックボックスの値が変化したとき, 設定を反映する.
    def Event_CheckButton(self):
        self.Debug.print_info('Call: Event_CheckButton')
        # 登録者の要素数を取得する.
        name = self.WidgetSelectStudent.get_selected_student_name()

        # 各チェックボタンの値を取得し, 登録者の情報を更新する.
        for key in self.UserSettings.kGradeKeyList:
            self.UserSettings.set_grade_value(name, key, self.get_selected_student_grade(key))

        # 設定ファイルに保存する.
        self.UserSettings.save_setting_file()

    # 「出題範囲選択」のチェックボタンのデータを設定する.
    def set_selected_student_grade(self, key, value):
        self.ProblemRegionFrame_Checkbutton_Value[key].set(value)

    # 「出題範囲選択」のチェックボタンのデータを取得する.
    def get_selected_student_grade(self, key):
        return self.ProblemRegionFrame_Checkbutton_Value[key].get()

    # 「出題範囲選択」のチェックボタンを有効にする.
    def enable_grade_checkbutton(self):
        for key in self.UserSettings.kGradeKeyList:
            self.ProblemRegionFrame_Checkbutton[key]['state'] = tk.NORMAL

    # 「出題範囲選択」のチェックボタンを無効にする.
    def disable_grade_checkbutton(self):
        for key in self.UserSettings.kGradeKeyList:
            self.ProblemRegionFrame_Checkbutton[key]['state'] = tk.DISABLED

    # 学年の設定を削除する.
    # 処理概要:
    # チェックボタンをクリアし, チェックボタンを無効にする.
    # チェックボタンの値をリスト化し, 設定する.
    def del_grade(self):
        for key in self.UserSettings.kGradeKeyList:
            # チェックボタンの値をすべてFalseにする.
            self.set_selected_student_grade(key, False)
            # 「出題範囲選択」のチェックボタンを無効にする.
            self.disable_grade_checkbutton()

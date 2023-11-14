# WidgetSelectMode.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk


class WidgetSelectMode:
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

        self.kMDRW = '復習'
        self.kMDTR = '練習'
        self.kMDWK = '苦手'
        self.kModeKeyList = [
              self.kMDRW
            , self.kMDTR
            , self.kMDWK
        ]
        self.kModeValueList = [
              0
            , 1
            , 2
        ]

        # 出題モードフレーム
        self.SelectModeFrame = tk.LabelFrame(root, padx=2, pady=2, text='出題形式')
        self.SelectModeFrame.grid(row=row, column=column, sticky=tk.W+tk.N)

        # 出題モード選択
        # チェックボタンを作成する.
        self.SelectModeFrameRadiobutton_Value = {}
        self.SelectModeFrame_Radiobutton = {}
        self.radio_value = tk.IntVar(value=-1)
        for key, value in zip(self.kModeKeyList, self.kModeValueList):
            # チェックボックスの左側を作成する.
            self.SelectModeFrame_Radiobutton[key] = tk.Radiobutton(
                self.SelectModeFrame
                , text=key
                , command=self.Event_RadioButton
                , variable=self.radio_value
                , value=value
                , anchor='w'
                , state=tk.DISABLED
            )
            self.SelectModeFrame_Radiobutton[key].pack(side='left')

    def set_class(self, wg_select_student, wg_scoring):
        self.WidgetSelectStudent = wg_select_student
        self.WidgetScoring = wg_scoring

    def Event_RadioButton(self):
        self.DebugPrint.print_info('Call: Event_RadioButton')

        # 登録者を取得する.
        name = self.WidgetSelectStudent.get_selected_student_name()

        # ラジオボタンの値を取得し, 登録者の情報を更新する.
        self.UserSettings.set_mode(name, self.get_selected_student_mode())

        # 設定ファイルに保存する.
        self.UserSettings.save_setting_file()

        # 採点を更新する.
        err_no = self.WidgetScoring.update_scoring()
        if err_no == 0:
            # 「採点完了」ボタンを有効にする.
            self.WidgetScoring.enable_scoring_button()
        else:
            # 「採点完了」ボタンを無効にする.
            self.WidgetScoring.disable_scoring_button()

    # 「出題モード」のラジオボタンのデータを設定する.
    def get_selected_student_mode(self):
        return self.radio_value.get()

    # 「出題モード」のラジオボタンのデータを取得する.
    def set_selected_student_mode(self, value):
        self.radio_value.set(value)

    # 「出題モード」のラジオボタンを有効にする.
    def enable_mode_Radiobutton(self):
        for key in self.kModeKeyList:
            self.SelectModeFrame_Radiobutton[key]['state'] = tk.NORMAL

    # 「出題モード」のラジオボタンを無効にする.
    def disable_mode_Radiobutton(self):
        for key in self.kModeKeyList:
            self.SelectModeFrame_Radiobutton[key]['state'] = tk.DISABLED


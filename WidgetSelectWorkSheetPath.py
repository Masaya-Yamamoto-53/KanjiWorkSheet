# WidgetSelectWorkSheetPath.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os
import tkinter as tk
import tkinter.filedialog as filedialog
from Subject import Subject
from DebugPrint import DebugPrint
from UserSettings import UserSettings


class WidgetSelectWorkSheetPath(Subject):
    def __init__(self, root, row, column):
        Subject.__init__(self)
        self.DebugPrint = DebugPrint(debug=True)  # デバッグ表示クラス
        self.UserSettings = UserSettings()  # ユーザ設定クラス

        # 問題集選択ラベルフレーム
        self.SelectWorksheetPath = tk.LabelFrame(root, padx=2, pady=2, text='問題集選択')
        self.SelectWorksheetPath.grid(row=row, column=column)

        # 問題集選択エントリー
        self.SelectWorksheetPath_Value = tk.StringVar()
        self.SelectWorksheetPath_Entry = tk.Entry(
            self.SelectWorksheetPath,
            textvariable=self.SelectWorksheetPath_Value,
            width=30,
            state='readonly'
        )
        self.SelectWorksheetPath_Entry.pack(side=tk.LEFT)

        # 問題集選択ボタン
        self.SelectWorksheetPath_Button = tk.Button(
            self.SelectWorksheetPath,
            text='選択',
            command=self.Event_SelectKanjiWorkSheet,
            state=tk.DISABLED
        )
        self.SelectWorksheetPath_Button.pack(side=tk.LEFT)

    def set_class(self, kanji_worksheet, wg_select_student):
        self.KanjiWorkSheet = kanji_worksheet
        self.WidgetSelectStudent = wg_select_student

    # イベント発生条件:「選択」ボタンを押したとき
    # 処理概要:選択したCSVファイルを設定する.
    def Event_SelectKanjiWorkSheet(self):
        self.DebugPrint.print_info('Call: Event_SelectKanjiWorkSheet')
        path = filedialog.askopenfilename(
            filetypes=[('', '*.csv')],
            initialdir=os.path.abspath(os.path.dirname(__file__))
        )
        # ファイルパスが有効なとき
        if len(path) > 0:
            self.notify(self.kNotify_valid_file_path)
            # 相対パスに変更する.
            path = './' + os.path.relpath(path)
            # 「問題集選択」エントリーを設定する.
            self.set_selected_worksheet_path(path)

            # 登録者の情報を更新する。
            name = self.WidgetSelectStudent.get_selected_student_name()
            self.UserSettings.set_path_of_problem(name, path)
            # 設定ファイルに保存する。
            self.UserSettings.save_setting_file()

            ################################################################################
            # 登録した問題集のパスを取得し, 問題集を読み込む.
            (_, _, err, err_msg) = self.KanjiWorkSheet.load_worksheet(path)
            ################################################################################
            # 問題集を正しく読み込めたとき
            if err == 0:
                self.notify(self.KNotify_load_successful)
                # 「採点完了」ボタンを有効にする.
                #self.WidgetScoring.enable_scoring_button()
                # 「プリント作成」ボタンを有効にする.
                #self.WidgetCreateWorkSheet.enable_create_button()
                # 「印刷」ボタンを有効にする.
                #self.WidgetCreateWorkSheet.enable_print_button()

            # 問題集を正しく読み込めなかったとき
            else:
                self.notify(self.kNotify_load_failed)
                # 「採点完了」ボタンを無効にする.
                #self.WidgetScoring.disable_scoring_button()
                # 「プリント作成」ボタンを無効にする.
                #self.WidgetCreateWorkSheet.disable_create_button()
                # 「印刷」ボタンを無効にする.
                #self.WidgetCreateWorkSheet.disable_print_button()

                # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
                for msg in err_msg:
                    tk.messagebox.showerror('Error', msg)

            # 登録者を変更, 問題集を新しく読み直したため, レポートを更新する.
            self.WidgetReport.update_report()

    # 「問題集選択」エントリーを設定する。
    def set_selected_worksheet_path(self, path):
        self.SelectWorksheetPath_Value.set(path)

    # 「問題集選択」エントリーを取得する.
    def get_selected_worksheet_path(self):
        return self.SelectWorksheetPath_Value.get()

    # 「選択」ボタンを有効にする.
    def enable_select_button(self):
        self.SelectWorksheetPath_Button['state'] = tk.NORMAL

    # 「選択」ボタンを無効にする.
    def disable_select_button(self):
        self.SelectWorksheetPath_Button['state'] = tk.DISABLED

    def update(self, subject):
        if subject.notify_status == subject.kNotify_select_student:
            # 「選択」ボタンを有効にする。
            self.enable_select_button()

            name = subject.get_selected_student_name()
            path = self.UserSettings.get_path_of_problem(name)

            # 「問題集選択」エントリーを設定する。
            self.set_selected_worksheet_path(path)

        elif subject.notify_status == subject.kNotify_delete_student:
            # 「選択」ボタンを無効にする。
            self.disable_select_button()
            # 「問題集選択」エントリーを空白に設定する。
            self.set_selected_worksheet_path('')

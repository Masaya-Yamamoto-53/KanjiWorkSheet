# WidgetCreateWorkSheet.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os
import subprocess
import tkinter as tk
from tkinter import messagebox


class WidgetCreateWorkSheet:
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

        # 作成フレーム
        self.CreateWorkSheetFrame = tk.Frame(root, padx=5, pady=10)
        self.CreateWorkSheetFrame.grid(row=row, column=column, sticky=tk.W)

        # 作成ボタン
        self.Create_Button = tk.Button(
              self.CreateWorkSheetFrame
            , text='プリント作成'
            , command=self.Event_CreateKanjiWorkSheet
            , state=tk.DISABLED
            , width=10, height=2
        )
        self.Create_Button.pack(side=tk.LEFT)

        # 印刷ボタン
        self.Print_Button = tk.Button(
              self.CreateWorkSheetFrame
            , text='印刷'
            , command=self.Event_PrintOut
            , state=tk.DISABLED
            , width=10, height=2
        )
        self.Print_Button.pack(side=tk.LEFT, padx=5)

    def set_class(self, create_file_path, kanji_worksheet, wg_select_student, wg_select_work_sheet_path, wg_scoring):
        self.CreateFilePath = create_file_path
        self.KanjiWorkSheet = kanji_worksheet
        self.WidgetSelectStudent = wg_select_student
        self.WidgetSelectWorkSheetPath = wg_select_work_sheet_path
        self.WidgetScoring = wg_scoring

    # イベント発生条件:「プリント作成」ボタンを押したとき
    # 処理概要:漢字プリントを作成する.
    def Event_CreateKanjiWorkSheet(self):
        self.DebugPrint.print_info('Call: Event_CreateKanjiWorkSheet')

        # 生徒名を設定する.
        name = self.WidgetSelectStudent.get_selected_student_name()
        self.KanjiWorkSheet.set_student_name(name)

        # 出題数を設定する.
        num = self.UserSettings.get_number_of_problem(name)
        self.KanjiWorkSheet.set_number_of_problem(num)

        # 学年を設定する.
        grade_list = self.UserSettings.get_grade_list(name)
        self.KanjiWorkSheet.set_grade(grade_list)

        # 出題形式を設定する.
        mode = self.UserSettings.get_mode(name)
        self.KanjiWorkSheet.set_mode(mode)

        # 学年を選択していないとき
        if len(grade_list) == 0:
            tk.messagebox.showerror('Error', '学年を選択して, 出題範囲を決定してください.')
        # 学年を選択しているとき
        else:
            # 採点が残っているとき
            log_path = self.CreateFilePath.get_path_of_log()
            yes = True
            if os.path.exists(log_path):
                msg = tk.messagebox.askquestion('Warning', '採点が終わっていません. このまま続けますか.', default='no')
                if msg == 'no':
                    yes = False

            # 漢字プリントを作成する.
            if yes:
                # ログファイルを削除する.
                self.KanjiWorkSheet.delete_kanji_worksheet_logfile(log_path)
                # 漢字プリントを作成する.
                self.KanjiWorkSheet.create_kanji_worksheet()
                # 漢字プリントの概要を表示する.
                self.KanjiWorkSheet.report_kanji_worksheet()
                # 漢字プリントの出題記録を作成する.

                result = self.KanjiWorkSheet.create_kanji_worksheet_logfile(log_path)

                # 漢字プリントをPFDで作成する.
                path = self.CreateFilePath.get_path_of_kanji_worksheet()
                self.KanjiWorkSheet.generate_pdf_kanji_worksheet(path)

                # 採点を更新する.
                self.WidgetScoring.update_scoring()
                if result == True:
                    # 「採点完了」ボタンを有効にする.
                    self.WidgetScoring.enable_scoring_button()
                else:
                    # 「採点完了」ボタンを無効にする.
                    self.WidgetScoring.disable_scoring_button()

                # 終了メッセージを表示する.
                tk.messagebox.showinfo('Info', os.path.basename(path) + ' を作成しました.')
            else:
                # 中止メッセージを表示する.
                tk.messagebox.showinfo('Info', '中止しました.')

    # イベント発生条件:「印刷」ボタンを押したとき
    # 処理概要:PDFを開く.
    def Event_PrintOut(self):
        path = self.CreateFilePath.get_path_of_kanji_worksheet()
        if os.path.exists(path):
            subprocess.Popen(['start', path], shell=True)
        else:
            # 対象ファイルが存在しない/
            tk.messagebox.showinfo('Info', '漢字プリントを作成してください.')

    # 「プリント作成」ボタンを有効にする.
    def enable_create_button(self):
        self.Create_Button['state'] = tk.NORMAL

    # 「プリント作成」ボタンを無効にする.
    def disable_create_button(self):
        self.Create_Button['state'] = tk.DISABLED

    # 「印刷」ボタンを有効にする.
    def enable_print_button(self):
        self.Print_Button['state'] = tk.NORMAL

    # 「印刷」ボタンを無効にする.
    def disable_print_button(self):
        self.Print_Button['state'] = tk.DISABLED

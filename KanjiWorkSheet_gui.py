# KanjiWorkSheet_gui.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import os
import subprocess

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog

from functools import partial

from KanjiWorkSheet_prob import KanjiWorkSheet_prob
from Debug import Debug
from UserSettings import UserSettings

from WidgetRegisterStudent import WidgetRegisterStudent
from WidgetSelectStudent import WidgetSelectStudent
from WidgetSelectWorkSheetPath import WidgetSelectWorkSheetPath
from WidgetCreateWorkSheet import WidgetCreateWorkSheet
from WidgetProblemRegion import WidgetProblemRegion
from WidgetSelectNumberOfProblem import WidgetSelectNumberOfProblem
from WidgetSelectMode import WidgetSelectMode
from WidgetScoring import WidgetScoring
from WidgetReport import WidgetReport

from LogFile import LogFile


class KanjiWorkSheet_gui:
    def __init__(self):
        self.KanjiWorkSheet = KanjiWorkSheet_prob()
        self.Debug = Debug(True)
        self.UserSettings = UserSettings()
        self.Root = tk.Tk()
        self.Root.title(u'漢字プリント作成ツール')
        self.Root.geometry('620x580')
        self.Root.resizable(False, False)

        # 設定ファイルを読み込む
        self.UserSettings.load_setting_file()
        # ウィジェットを作成する.
        self.create_widget()
        # ループ処理
        self.Root.mainloop()

    ################################################################################
    # ウィジェット作成用の関数
    ################################################################################
    # ウィジェットを作成する.
    def create_widget(self):
        self.SettingFrame = tk.Frame(self.Root, padx=10, pady=5)
        self.SettingFrame.grid(row=0, column=0)
        self.ReportFrame = tk.Frame(self.Root)
        self.ReportFrame.grid(row=1, column=0, sticky=tk.E)
        self.SelectFrame = tk.Frame(self.SettingFrame)
        self.SelectFrame.grid(row=0, column=0, sticky=tk.N)
        self.SelectFrame_Range_Num = tk.Frame(self.SelectFrame)
        self.SelectFrame_Range_Num.grid(row=3, column=0, sticky=tk.W)
        self.ScoringFrame = tk.Frame(self.SettingFrame)
        self.ScoringFrame.grid(row=0, column=1)
        self.PrintReportFrame = tk.Frame(self.ReportFrame, padx=5, pady=5)
        self.PrintReportFrame.grid(row=0, column=0)

        # 生徒登録用のウィジェット作成
        self.wg_register_student = WidgetRegisterStudent(
            self.Debug, self.UserSettings, self.SelectFrame, row=0, column=0)
        # 生徒選択用のウィジェット作成
        self.wg_select_student = WidgetSelectStudent(
            self.Debug, self.UserSettings, self.SelectFrame, row=1, column=0)
        # 問題集選択用のウィジェット作成
        self.wg_select_work_sheet_path = WidgetSelectWorkSheetPath(
            self.Debug, self.UserSettings, self.SelectFrame, row=2, column=0)
        # プリント作成用ウィジェット
        self.wg_create_worksheet = WidgetCreateWorkSheet(
            self.Debug, self.UserSettings, self.SelectFrame, row = 4, column = 0)
        # 出題範囲選択用のウィジェット作成
        self.wg_problem_region = WidgetProblemRegion(
            self.Debug, self.UserSettings, self.SelectFrame_Range_Num, row=0, column=0)
        # 出題数用のウィジェット作成
        self.wg_select_number_of_problem = WidgetSelectNumberOfProblem(
            self.Debug, self.UserSettings, self.SelectFrame_Range_Num, row=0, column=1)
        # 出題選択モードのウィジェット作成
        self.wg_select_mode = WidgetSelectMode(
            self.Debug, self.UserSettings, self.SelectFrame_Range_Num, row=1, column=0)
        # 採点用のウィジェット作成
        self.wg_scoring = WidgetScoring(
            self.Debug, self.UserSettings, self.ScoringFrame, row=0, column=0)
        # レポート用ウィジェット作成
        self.wg_report = WidgetReport(
            self.Debug, self.UserSettings, self.PrintReportFrame, row=0, column=0)
        # ログファイル
        self.LogFile = LogFile(
              self.wg_select_student
            , self.wg_select_mode
        )

        # 生徒選択用のウィジェット作成
        self.wg_select_student.set_class(
              self.KanjiWorkSheet
            , self.LogFile
            , self.wg_select_work_sheet_path
            , self.wg_create_worksheet
            , self.wg_problem_region
            , self.wg_select_number_of_problem
            , self.wg_select_mode
            , self.wg_scoring
            , self.wg_report
        )
        # 問題集選択用のウィジェット作成
        self.wg_select_work_sheet_path.set_class(
              self.KanjiWorkSheet
            , self.wg_select_student
            , self.wg_scoring
            , self.wg_report
            , self.wg_create_worksheet
        )
        # プリント作成用ウィジェット
        self.wg_create_worksheet.set_class(
              self.LogFile
            , self.KanjiWorkSheet
            , self.wg_select_student
            , self.wg_select_work_sheet_path
            , self.wg_scoring
        )
        # 出題範囲選択用のウィジェット作成
        self.wg_problem_region.set_class(
              self.wg_select_student
        )
        # 出題数用のウィジェット作成
        self.wg_select_number_of_problem.set_class(
              self.KanjiWorkSheet
            , self.wg_select_student

        )
        # 出題選択モードのウィジェット作成
        self.wg_select_mode.set_class(
              self.wg_select_student
            , self.wg_scoring
        )
        # 採点用のウィジェット作成
        self.wg_scoring.set_class(
              self.KanjiWorkSheet
            , self.wg_select_student
            , self.wg_report
        )
        # レポート用ウィジェット作成
        self.wg_report.set_class(
              self.KanjiWorkSheet
            , self.wg_select_work_sheet_path
        )

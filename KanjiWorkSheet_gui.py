# KanjiWorkSheet_gui.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk

from KanjiWorkSheet_prob import KanjiWorkSheet_prob
from DebugPrint import DebugPrint
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

from CreateFilePath import CreateFilePath


class KanjiWorkSheet_gui:
    def __init__(self):
        self.KanjiWorkSheet = KanjiWorkSheet_prob()
        self.DebugPrint = DebugPrint(True)
        self.UserSettings = UserSettings()
        self.Root = tk.Tk()
        self.Root.title(u'漢字プリント作成ツール')
        self.Root.geometry('1100x1100')
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
        self.ReportFrame = tk.Frame(self.Root, padx=10, pady=5)
        self.ReportFrame.grid(row=1, column=0, sticky=tk.E)

        self.SelectFrame = tk.Frame(self.SettingFrame)
        self.SelectFrame.grid(row=0, column=0, sticky=tk.N)
        self.ScoringFrame = tk.Frame(self.SettingFrame)
        self.ScoringFrame.grid(row=0, column=1)

        # 生徒登録用、生徒選択用、問題集選択用の後のため, row=3
        self.RangeFrame = tk.Frame(self.SelectFrame)
        self.RangeFrame.grid(row=3, column=0, sticky=tk.W)

        self.GradeFrame = tk.Frame(self.RangeFrame)
        self.GradeFrame.grid(row=0, column=0)

        self.ModeFrame = tk.Frame(self.RangeFrame)
        self.ModeFrame.grid(row=0, column=1)

        # 生徒登録用のウィジェット作成
        self.wg_register_student = WidgetRegisterStudent(self.SelectFrame, row=0, column=0)
        # 生徒選択用のウィジェット作成
        self.wg_select_student = WidgetSelectStudent(self.SelectFrame, row=1, column=0)
        # 問題集選択用のウィジェット作成
        self.wg_select_work_sheet_path = WidgetSelectWorkSheetPath(self.SelectFrame, row=2, column=0)
        # プリント作成用ウィジェット
        self.wg_create_worksheet = WidgetCreateWorkSheet(self.SelectFrame, row=4, column=0)
        # 出題範囲選択用のウィジェット作成
        self.wg_problem_region = WidgetProblemRegion(
            self.DebugPrint, self.UserSettings, self.GradeFrame, row=0, column=0)
        # 出題数用のウィジェット作成
        self.wg_select_number_of_problem = WidgetSelectNumberOfProblem(self.ModeFrame, row=1, column=0)
        # 出題選択モードのウィジェット作成
        self.wg_select_mode = WidgetSelectMode(
            self.DebugPrint, self.UserSettings, self.ModeFrame, row=2, column=0)
        # 採点用のウィジェット作成
        self.wg_scoring = WidgetScoring(
            self.DebugPrint, self.UserSettings, self.ScoringFrame, row=0, column=0)
        # レポート用ウィジェット作成
        self.wg_report = WidgetReport(
            self.DebugPrint, self.UserSettings, self.ReportFrame, row=0, column=0)
        # ログファイル
        self.CreateFilePath = CreateFilePath(
            self.wg_select_student,
            self.wg_select_mode
        )

        # 生徒選択用のウィジェット作成
        self.wg_select_student.set_class(
            self.KanjiWorkSheet,
            self.CreateFilePath,
        )
        self.wg_select_student.attach(self.wg_select_work_sheet_path)
        self.wg_select_student.attach(self.wg_create_worksheet)
        self.wg_select_student.attach(self.wg_problem_region)
        self.wg_select_student.attach(self.wg_select_number_of_problem)
        self.wg_select_student.attach(self.wg_select_mode)
        self.wg_select_student.attach(self.wg_scoring)
        self.wg_select_student.attach(self.wg_report)

        # 問題集選択用のウィジェット作成
        self.wg_select_work_sheet_path.set_class(
            self.KanjiWorkSheet,
            self.wg_select_student
        )
        self.wg_select_work_sheet_path.attach(self.wg_create_worksheet)

        # プリント作成用ウィジェット
        self.wg_create_worksheet.set_class(
            self.CreateFilePath,
            self.KanjiWorkSheet,
            self.wg_select_student,
            self.wg_select_work_sheet_path
        )
        self.wg_create_worksheet.attach(self.wg_scoring)

        # 出題範囲選択用のウィジェット作成
        self.wg_problem_region.set_class(
            self.wg_select_student
        )
        # 出題数用のウィジェット作成
        self.wg_select_number_of_problem.set_class(
            self.KanjiWorkSheet,
            self.wg_select_student

        )
        # 出題選択モードのウィジェット作成
        self.wg_select_mode.set_class(
            self.wg_select_student,
            self.wg_scoring
        )
        # 採点用のウィジェット作成
        self.wg_scoring.set_class(
            self.KanjiWorkSheet,
            self.wg_select_student,
            self.wg_select_mode,
            self.wg_report
        )
        # レポート用ウィジェット作成
        self.wg_report.set_class(
            self.KanjiWorkSheet,
            self.wg_select_work_sheet_path
        )

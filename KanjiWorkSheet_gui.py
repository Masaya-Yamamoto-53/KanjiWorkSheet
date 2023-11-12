# KanjiWorkSheet_gui.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import os
import subprocess
import pandas as pd

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog

from functools import partial

from KanjiWorkSheet_prob import KanjiWorkSheet_prob
from UserSettings import UserSettings

class KanjiWorkSheet_gui:
    def __init__(self):
        self.KanjiWorkSheet = KanjiWorkSheet_prob()
        self.UserSettings = UserSettings()
        self.Root = tk.Tk()
        self.Root.title(u'漢字プリント作成ツール')
        self.Root.geometry('620x580')
        self.Root.resizable(False, False)

        self.kStudentName = 'Name'
        self.kProblemPath = 'Path'
        self.kNumber = 'Number'
        self.kJS1 = '小学一年生'
        self.kJS2 = '小学二年生'
        self.kJS3 = '小学三年生'
        self.kJS4 = '小学四年生'
        self.kJS5 = '小学五年生'
        self.kJS6 = '小学六年生'
        self.grade_value_list = [1, 2, 3, 4, 5, 6]

        self.kMDRW = '復習'
        self.kMDTR = '練習'
        self.kMDWK = '苦手'
        self.kMode = '出題形式'
        self.kModeValueList = [
              self.KanjiWorkSheet.kMDRW
            , self.KanjiWorkSheet.kMDTR
            , self.KanjiWorkSheet.kMDWK
        ]
        self.kTotal = '　　　合計'
        self.kGradeReportList = [
              self.UserSettings.kJS1
            , self.UserSettings.kJS2
            , self.UserSettings.kJS3
            , self.UserSettings.kJS4
            , self.UserSettings.kJS5
            , self.UserSettings.kJS6
            , self.kTotal
        ]

        self.path_of_worksheet = ''
        self.PathOfLogFile = ''

        # 設定ファイルを読み込む
        self.UserSettings.load_setting_file()
        # ウィジェットを作成する.
        self.create_widget()
        self.Root.mainloop()

    def CreateAnalysisWindow(self):
        self.ana_window = tk.Toplevel(self.Root)
        self.ana_window.geometry('620x560')
        self.ana_window.title('分析')
        label.pack()

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
        self.create_widget_register_student(self.SelectFrame, row=0, column=0)
        # 生徒選択用のウィジェット作成
        self.create_widget_select_student(self.SelectFrame, row=1, column=0)
        # 問題集選択用のウィジェット作成
        self.create_widget_select_worksheet_path(self.SelectFrame, row=2, column=0)
        # プリント作成用ウィジェット
        self.create_widget_create_worksheet(self.SelectFrame, row=4, column=0)
        # 出題範囲選択用のウィジェット作成
        self.create_widget_problem_region(self.SelectFrame_Range_Num, row=0, column=0)
        # 出題数用のウィジェット作成
        self.create_widget_select_number_of_problem(self.SelectFrame_Range_Num, row=0, column=1)
        # 出題選択モードのウィジェット作成
        self.create_widget_select_mode(self.SelectFrame_Range_Num, row=1, column=0)
        # 採点用のウィジェット作成
        self.create_widget_scoring(self.ScoringFrame, row=0, column=0)
        # レポート用ウィジェット作成
        self.create_widget_report(self.PrintReportFrame, row=0, column=0)

    # 生徒登録用のウィジェット作成
    def create_widget_register_student(self, root, row, column):
        # 生徒登録ラベルフレーム
        self.RegisterStudentFrame = tk.LabelFrame(root, padx=2, pady=2, text='生徒登録')
        self.RegisterStudentFrame.grid(row=row, column=column)

        # 生徒登録エントリー
        self.RegisterStudentFrame_Entry = tk.Entry(self.RegisterStudentFrame, width=40)
        self.RegisterStudentFrame_Entry.pack(side=tk.LEFT)

        # 生徒登録ボタン
        self.RegisterStudentFrame_Button = tk.Button(
                  self.RegisterStudentFrame
                , text='登録'
                , command=self.Event_RegisterStudent
        )
        self.RegisterStudentFrame_Button.pack(side=tk.LEFT)

    # 生徒選択用のウィジェット作成
    def create_widget_select_student(self, root, row, column):
        # 生徒選択ラベルフレーム
        self.SelectStudentFrame = tk.LabelFrame(root, padx=2, pady=2, text='生徒選択')
        self.SelectStudentFrame.grid(row=row, column=column)

        # 生徒選択コンボボックス
        # 生徒が存在しない場合は""にする
        if self.UserSettings.get_setting_num() == 0:
            values = ''
        else:
            # NumPy配列(ndarry)をリストに変換し格納する.
            values = self.UserSettings.get_student_name_list()

        self.SelectStudentFrame_Combobox_Value = tk.StringVar()
        self.SelectStudentFrame_Combobox = tk.ttk.Combobox(
                  self.SelectStudentFrame
                , values=(values)
                , textvariable=self.SelectStudentFrame_Combobox_Value
                , postcommand=self.Event_UpdateStudent
                , width=37
        )
        self.SelectStudentFrame_Combobox.bind('<<ComboboxSelected>>', self.Event_SelectStudent)
        self.SelectStudentFrame_Combobox.pack(side=tk.LEFT)

        # 生徒削除ボタン
        self.SelectStudentFrame_Button = tk.Button(
                  self.SelectStudentFrame
                , text='削除'
                , command=self.Event_DeleteStudent
                , state=tk.DISABLED
        )
        self.SelectStudentFrame_Button.pack(side=tk.LEFT)

    # 問題集選択用のウィジェット作成
    def create_widget_select_worksheet_path(self, root, row, column):
        # 問題集選択ラベルフレーム
        self.SelectWorksheetPath = tk.LabelFrame(root, padx=2, pady=2, text='問題集選択')
        self.SelectWorksheetPath.grid(row=row, column=column)

        # 問題集選択エントリー
        self.SelectWorksheetPath_Value = tk.StringVar()
        self.SelectWorksheetPath_Entry = tk.Entry(
                  self.SelectWorksheetPath
                , textvariable=self.SelectWorksheetPath_Value
                , width=40
                , state='readonly'
        )
        self.SelectWorksheetPath_Entry.pack(side=tk.LEFT)

        # 問題集選択ボタン
        self.SelectWorksheetPath_Button = tk.Button(
                  self.SelectWorksheetPath
                , text='選択'
                , command=self.Event_SelectKanjiWorkSheet
                , state=tk.DISABLED
        )
        self.SelectWorksheetPath_Button.pack(side=tk.LEFT)

    # 出題範囲選択洋のウィジェット作成
    def create_widget_problem_region(self, root, row, column):
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

    # 出題数用のウィジェット作成
    def create_widget_select_number_of_problem(self, root, row, column):
        # 出題数ラベルフレーム
        self.SelectNumberOfProblemFrame = tk.LabelFrame(root, padx=2, pady=2, text='出題数')
        self.SelectNumberOfProblemFrame.grid(row=row, column=column, sticky=tk.W+tk.N)

        # 出題数エントリー
        self.SelectNumberOfProblemFrame_Value = tk.StringVar()
        self.SelectNumberOfProblemFrame_Value.set('')
        self.SelectNumberOfProblemFrame_Value.trace_add('write', self.Event_ChangeNumberOfProblem)
        self.SelectNumberOfProblemFrame_Entry = tk.Entry(
                  self.SelectNumberOfProblemFrame
                , width=10
                , textvariable=self.SelectNumberOfProblemFrame_Value
                , state=tk.DISABLED
        )
        self.SelectNumberOfProblemFrame_Entry.pack(side=tk.LEFT)

    # 出題選択モードのウィジェット作成
    def create_widget_select_mode(self, root, row, column):
        # 出題モードフレーム
        self.SelectModeFrame = tk.LabelFrame(root, padx=2, pady=2, text=self.kMode)
        self.SelectModeFrame.grid(row=row, column=column, sticky=tk.W+tk.N)

        # 出題モード選択
        # チェックボタンを作成する.
        self.SelectModeFrameRadiobutton_Value = {}
        self.SelectModeFrame_Radiobutton = {}
        self.radio_value = tk.IntVar(value=-1)
        for key, value in zip(self.UserSettings.kModeKeyList, self.kModeValueList):
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

    # 採点用のウィジェット作成
    def create_widget_scoring(self, root, row, column):
        # 採点ラベルフレーム
        self.ScoringFrame = tk.LabelFrame(root, padx=2, pady=0, text='採点')
        self.ScoringFrame.grid(row=row, column=column)
        # 答えフレーム
        self.ScoringFrame_AnsFrame = tk.Frame(self.ScoringFrame, padx=2, pady=0)
        self.ScoringFrame_AnsFrame.grid(row=0, column=0)
        # 答案フレーム
        self.Scoring_EndFrame = tk.Frame(self.ScoringFrame, padx=2, pady=0)
        self.Scoring_EndFrame.grid(row=1, column=0)
        # 上のフレーム
        self.ScoringFrame_AnsFrame_Top = tk.Frame(self.ScoringFrame_AnsFrame, padx=2, pady=0)
        self.ScoringFrame_AnsFrame_Top.grid(row=0, column=0)
        # 下のフレーム
        self.ScoringFrame_AnsFrame_Btm = tk.Frame(self.ScoringFrame_AnsFrame, padx=2, pady=0)
        self.ScoringFrame_AnsFrame_Btm.grid(row=1, column=0)

        # 採点ボタン
        self.Scoring_EndFrame_Button = tk.Button(
                  self.Scoring_EndFrame
                , text='採点完了'
                , command=self.Event_PushBtnScoreing
                , state=tk.DISABLED
        )
        self.Scoring_EndFrame_Button.pack(side=tk.BOTTOM)

        i = 0
        num_array = [
                  '⑩', '⑨', '⑧', '⑦', '⑥', '⑤', '④', '③', '②', '①'
                , '⑳', '⑲', '⑱', '⑰', '⑯', '⑮', '⑭', '⑬', '⑫', '⑪'
        ]
        self.kScoringFrame_AnsFrame = [
                  self.ScoringFrame_AnsFrame_Top , self.ScoringFrame_AnsFrame_Top
                , self.ScoringFrame_AnsFrame_Top , self.ScoringFrame_AnsFrame_Top
                , self.ScoringFrame_AnsFrame_Top , self.ScoringFrame_AnsFrame_Top
                , self.ScoringFrame_AnsFrame_Top , self.ScoringFrame_AnsFrame_Top
                , self.ScoringFrame_AnsFrame_Top , self.ScoringFrame_AnsFrame_Top
                , self.ScoringFrame_AnsFrame_Btm , self.ScoringFrame_AnsFrame_Btm
                , self.ScoringFrame_AnsFrame_Btm , self.ScoringFrame_AnsFrame_Btm
                , self.ScoringFrame_AnsFrame_Btm , self.ScoringFrame_AnsFrame_Btm
                , self.ScoringFrame_AnsFrame_Btm , self.ScoringFrame_AnsFrame_Btm
                , self.ScoringFrame_AnsFrame_Btm , self.ScoringFrame_AnsFrame_Btm
        ]
        self.ScoringFrame_AnsFrame_UB = {}
        self.ScoringFrame_AnsFrame_Lable = {}
        self.ScoringFrame_AnsFrame_Text = {}
        self.ScoringFrame_AnsFrame_Button = {}
        self.ScoringFrame_AnsFrame_Value = {}
        for key in num_array:
            self.ScoringFrame_AnsFrame_UB[key] = tk.Frame(self.kScoringFrame_AnsFrame[i], padx=0, pady=0)
            self.ScoringFrame_AnsFrame_UB[key].grid(row=0, column=i)

            # 問題番号
            self.ScoringFrame_AnsFrame_Lable[key] = tk.Label(self.ScoringFrame_AnsFrame_UB[key], text=key)
            self.ScoringFrame_AnsFrame_Lable[key].pack(side=tk.TOP)

            # 答えテキスト
            self.ScoringFrame_AnsFrame_Text[key] = tk.Text(
                      self.ScoringFrame_AnsFrame_UB[key]
                    , width=2
                    , height=4
                    , state=tk.DISABLED
            )
            self.ScoringFrame_AnsFrame_Text[key].configure(font=('msmincho', 18))
            self.ScoringFrame_AnsFrame_Text[key].pack(side=tk.TOP)

            # ○／×ボタン
            self.ScoringFrame_AnsFrame_Button[key] = tk.Button(
                      self.ScoringFrame_AnsFrame_UB[key]
                    , text='―'
                    , state=tk.DISABLED
                    , command=partial(self.Event_ChangeResult, key)
                    , width=2, height=1
            )
            self.ScoringFrame_AnsFrame_Button[key].pack(side=tk.TOP)
            self.ScoringFrame_AnsFrame_Value[key] = None
            i += 1

    # レポート用のウィジェット作成
    def create_widget_report(self, root, row, column):
        # 出題内容ラベルフレーム
        self.OutInfoFrame = tk.LabelFrame(root, text='出題内容')
        self.OutInfoFrame.grid(row=row, column=column, sticky=tk.N)
        # レポートラベルフレーム
        self.ReportFrame = tk.LabelFrame(root, text='レポート')
        self.ReportFrame.grid(row=row, column=column+1)
        # 出題数
        self.Report_ProblemFrame = tk.Frame(self.ReportFrame)
        self.Report_ProblemFrame.grid(row=0, column=0)
        # 正解数
        self.Report_CorrectFrame = tk.Frame(self.ReportFrame)
        self.Report_CorrectFrame.grid(row=0, column=1)
        # 不正解数
        self.Report_InCorrectFrame = tk.Frame(self.ReportFrame)
        self.Report_InCorrectFrame.grid(row=0, column=2)
        # 1日後出題
        self.Report_DayFrame = tk.Frame(self.ReportFrame)
        self.Report_DayFrame.grid(row=0, column=3)
        # 1週間後出題
        self.Report_WeekFrame = tk.Frame(self.ReportFrame)
        self.Report_WeekFrame.grid(row=0, column=4)
        # 1ヶ月後出題
        self.Report_MonthFrame = tk.Frame(self.ReportFrame)
        self.Report_MonthFrame.grid(row=0, column=5)

        # 出題内容
        #self.create_widget_report_OutInfo(self.OutInfoFrame)

        # レポート
        self.create_widget_report_Problem(self.Report_ProblemFrame, self.kGradeReportList, u'出題状況')
        self.create_widget_report_Correct(self.Report_CorrectFrame, self.kGradeReportList, u'　正解')
        self.create_widget_report_InCorrect(self.Report_InCorrectFrame, self.kGradeReportList, u'不正解')
        self.create_widget_report_Day(self.Report_DayFrame, self.kGradeReportList, u'1日後')
        self.create_widget_report_Week(self.Report_WeekFrame, self.kGradeReportList, u'1週間後')
        self.create_widget_report_Month(self.Report_MonthFrame, self.kGradeReportList, u'1ヶ月後')

    # レポート:出題数用のウィジェット作成
    def create_widget_report_OutInfo(self, root):
        self.Report_OutInfoFrame_Title = tk.Frame(root)
        self.Report_OutInfoFrame_Title.grid(row=0, column=0)

        self.Report_OutInfoFrame_Title_text = tk.Label(self.Report_ProblemFrame_Title, text='出題種類')
        self.Report_OutInfoFrame_Title_text.pack()

        self.Report_OutInfo_Correct_text = tk.Label(self.OutInfoFrame_L, text='正解')
        self.Report_OutInfo_Correct_text.pack(anchor=tk.W)
        self.Report_OutInfo_InCorrect_text = tk.Label(self.OutInfoFrame_L, text='不正解')
        self.Report_OutInfo_InCorrect_text.pack(anchor=tk.W)
        self.Report_OutInfo_Day_text = tk.Label(self.OutInfoFrame_L, text='1日後')
        self.Report_OutInfo_Day_text.pack(anchor=tk.W)
        self.Report_OutInfo_Day_text = tk.Label(self.OutInfoFrame_L, text='1週間後')
        self.Report_OutInfo_Day_text.pack(anchor=tk.W)
        self.Report_OutInfo_Day_text = tk.Label(self.OutInfoFrame_L, text='1ヶ月後')
        self.Report_OutInfo_Day_text.pack(anchor=tk.W)

        tmp_entry1 = tk.Entry(self.OutInfoFrame_R, width=5, state=tk.DISABLED)
        tmp_entry1.pack(side=tk.TOP)
        tmp_entry1 = tk.Entry(self.OutInfoFrame_R, width=5, state=tk.DISABLED)
        tmp_entry1.pack(side=tk.TOP)
        tmp_entry1 = tk.Entry(self.OutInfoFrame_R, width=5, state=tk.DISABLED)
        tmp_entry1.pack(side=tk.TOP)
        tmp_entry1 = tk.Entry(self.OutInfoFrame_R, width=5, state=tk.DISABLED)
        tmp_entry1.pack(side=tk.TOP)
        tmp_entry1 = tk.Entry(self.OutInfoFrame_R, width=5, state=tk.DISABLED)
        tmp_entry1.pack(side=tk.TOP)

    # レポート:問題数用のウィジェット作成
    def create_widget_report_Problem(self, root, arr, text):
        self.Report_ProblemFrame_Title = tk.Frame(root)
        self.Report_ProblemFrame_Title.grid(row=0, column=0)

        self.Report_ProblemFrame_Title_text = tk.Label(self.Report_ProblemFrame_Title, text=text)
        self.Report_ProblemFrame_Title_text.pack()

        self.Report_Problem_Frame = {}
        self.Report_Problem_Frame_Label1 = {}
        self.Report_Problem_Frame_Label2 = {}
        self.Report_Problem_Entry_OutNum = {}
        self.Report_Problem_Entry_TolNum = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text=text)
            tmp_label1.pack(side=tk.LEFT)

            # Left Entry
            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            tmp_label2 = tk.Label(tmp_frame, text='/')
            tmp_label2.pack(side=tk.LEFT)

            # Right Entry
            tmp_entry2 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry2.pack(side=tk.LEFT)

            self.Report_Problem_Frame[text] = tmp_frame
            self.Report_Problem_Frame_Label1[text] = tmp_label1
            self.Report_Problem_Frame_Label2[text] = tmp_label2
            self.Report_Problem_Entry_OutNum[text] = tmp_entry1
            self.Report_Problem_Entry_TolNum[text] = tmp_entry2
            i = i + 1

    # レポート:正解用のウィジェット作成
    def create_widget_report_Correct(self, root, arr, text):
        self.Report_CorrectFrame_Title = tk.Frame(root)
        self.Report_CorrectFrame_Title.grid(row=0, column=0)

        self.Report_CorrectFrame_Title_text = tk.Label(self.Report_CorrectFrame_Title, text='　正解')
        self.Report_CorrectFrame_Title_text.pack()

        self.Report_Correct_Frame = {}
        self.Report_Correct_Frame_Label1 = {}
        self.Report_Correct_Entry_Num = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text='　')
            tmp_label1.pack(side=tk.LEFT)

            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            self.Report_Correct_Frame[text] = tmp_frame
            self.Report_Correct_Frame_Label1[text] = tmp_label1
            self.Report_Correct_Entry_Num[text] = tmp_entry1
            i = i + 1

    # レポート:不正解用のウィジェット作成
    def create_widget_report_InCorrect(self, root, arr, text):
        self.Report_InCorrectFrame_Title = tk.Frame(root)
        self.Report_InCorrectFrame_Title.grid(row=0, column=0)

        self.Report_InCorrectFrame_Title_text = tk.Label(self.Report_InCorrectFrame_Title, text=text)
        self.Report_InCorrectFrame_Title_text.pack()

        self.Report_InCorrect_Frame = {}
        self.Report_InCorrect_Frame_Label1 = {}
        self.Report_InCorrect_Entry_Num = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text='')
            tmp_label1.pack(side=tk.LEFT)

            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            self.Report_InCorrect_Frame[text] = tmp_frame
            self.Report_InCorrect_Frame_Label1[text] = tmp_label1
            self.Report_InCorrect_Entry_Num[text] = tmp_entry1
            i = i + 1

    # レポート:1日後用のウィジェット作成
    def create_widget_report_Day(self, root, arr, text):
        self.Report_DayFrame_Title = tk.Frame(root)
        self.Report_DayFrame_Title.grid(row=0, column=0)

        self.Report_DayFrame_Title_text = tk.Label(self.Report_DayFrame_Title, text=text)
        self.Report_DayFrame_Title_text.pack()

        self.Report_Day_Frame = {}
        self.Report_Day_Frame_Label1 = {}
        self.Report_Day_Entry_Num = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text='')
            tmp_label1.pack(side=tk.LEFT)

            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            self.Report_Day_Frame[text] = tmp_frame
            self.Report_Day_Frame_Label1[text] = tmp_label1
            self.Report_Day_Entry_Num[text] = tmp_entry1
            i = i + 1

    # レポート:1週間後用のウィジェット作成
    def create_widget_report_Week(self, root, arr, text):
        self.Report_WeekFrame_Title = tk.Frame(root)
        self.Report_WeekFrame_Title.grid(row=0, column=0)

        self.Report_WeekFrame_Title_text = tk.Label(self.Report_WeekFrame_Title, text=text)
        self.Report_WeekFrame_Title_text.pack()

        self.Report_Week_Frame = {}
        self.Report_Week_Frame_Label1 = {}
        self.Report_Week_Entry_Num = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text='')
            tmp_label1.pack(side=tk.LEFT)

            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            self.Report_Week_Frame[text] = tmp_frame
            self.Report_Week_Frame_Label1[text] = tmp_label1
            self.Report_Week_Entry_Num[text] = tmp_entry1
            i = i + 1

    # レポート:1ヶ月後用のウィジェット作成
    def create_widget_report_Month(self, root, arr, text):
        self.Report_MonthFrame_Title = tk.Frame(root, padx=10, pady=0)
        self.Report_MonthFrame_Title.grid(row=0, column=0)

        self.Report_MonthFrame_Title_text = tk.Label(self.Report_MonthFrame_Title, text=text)
        self.Report_MonthFrame_Title_text.pack()

        self.Report_Month_Frame = {}
        self.Report_Month_Frame_Label1 = {}
        self.Report_Month_Entry_Num = {}
        i = 1
        for text in arr:
            tmp_frame = tk.Frame(root)
            tmp_frame.grid(row=i, column=0)

            tmp_label1 = tk.Label(tmp_frame, text='')
            tmp_label1.pack(side=tk.LEFT)

            tmp_entry1 = tk.Entry(tmp_frame, width=9, state=tk.DISABLED)
            tmp_entry1.pack(side=tk.LEFT)

            self.Report_Month_Frame[text] = tmp_frame
            self.Report_Month_Frame_Label1[text] = tmp_label1
            self.Report_Month_Entry_Num[text] = tmp_entry1
            i = i + 1

    # プリント作成用のウィジェット作成
    def create_widget_create_worksheet(self, root, row, column):
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

        # 分析ボタン
        self.Analysis_Button = tk.Button(
                  self.CreateWorkSheetFrame
                , text='分析'
                , command=self.CreateAnalysisWindow
                , state=tk.DISABLED
                , width=10, height=2
        )
        self.Analysis_Button.pack(side=tk.LEFT, padx=5)

    # ログファイルのパスを取得する.
    def get_path_of_log(self):
        name = self.SelectStudentFrame_Combobox_Value.get()

        logdir = './result/'
        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        return logdir + '.' + name + str(self.KanjiWorkSheet.get_mode()) + '.log'

    # 「生徒登録」エントリーのデータを削除する.
    def del_registered_student_entry(self):
        self.RegisterStudentFrame_Entry.delete('0', 'end')

    # 「生徒登録」エントリーのデータを取得する.
    def get_registered_student_entry(self):
        return self.RegisterStudentFrame_Entry.get()

    # 「生徒選択」エントリーのメニューを設定する.
    def set_selected_student_list(self, list):
        self.SelectStudentFrame_Combobox['values'] = list
        if len(list) == 0:
            self.SelectStudentFrame_Combobox.set('')

    # 「生徒選択」エントリーのデータを取得する.
    def get_selected_student_name(self):
        return self.SelectStudentFrame_Combobox_Value.get()

    # 「問題集選択」エントリーを設定する.
    def set_selected_worksheet_path(self, path):
        self.SelectWorksheetPath_Value.set(path)

    # 「問題集選択」エントリーを取得する.
    def get_selected_worksheet_path(self):
        return self.SelectWorksheetPath_Value.get()

    # 「出題範囲選択」のチェックボタンのデータを設定する.
    def set_selected_student_grade(self, key, value):
        self.ProblemRegionFrame_Checkbutton_Value[key].set(value)

    # 「出題範囲選択」のチェックボタンのデータを取得する.
    def get_selected_student_grade(self, key):
        return self.ProblemRegionFrame_Checkbutton_Value[key].get()

    # 「出題モード」のラジオボタンのデータを設定する.
    def get_selected_student_mode(self):
        return self.radio_value.get()

    # 「出題モード」のラジオボタンのデータを取得する.
    def set_selected_student_mode(self, value):
        self.radio_value.set(value)

    # 「出題数」エントリーを設定する.
    def set_number_of_problem(self, value):
        self.SelectNumberOfProblemFrame_Entry.delete('0', 'end')
        self.SelectNumberOfProblemFrame_Entry.insert('end', value)

    # 「出題数」エントリーを取得する.
    def get_number_of_problem(self):
        str = self.SelectNumberOfProblemFrame_Value.get()
        if str.isdigit() == True:
            return int(str)
        else:
            return 1

    # 「回答」エントリーを消去する.
    def delete_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key].delete('1.0', 'end')

    # 「回答」エントリーを挿入する.
    def insert_scoring_answer_text(self, key, value):
        self.ScoringFrame_AnsFrame_Text[key].insert('end', value)

    # 「採点」ボタンのデータを設定する.
    def set_scoring_answer_button_display_value(self, key, value):
        self.ScoringFrame_AnsFrame_Value[key] = value

    # 「採点」ボタンのデータを取得する.
    def get_scoring_answer_button_value(self, key):
        return self.ScoringFrame_AnsFrame_Value[key]

    # 「採点」ボタンの表示を設定する.
    def set_scoring_answer_button_display(self, key, sign):
        self.ScoringFrame_AnsFrame_Button[key]['text'] = sign

    ################################################################################

    # 「削除」ボタンを有効にする.
    def enable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.NORMAL

    # 「削除」ボタンを無効にする.
    def disable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.DISABLED

    # 「選択」ボタンを有効にする.
    def enable_select_button(self):
        self.SelectWorksheetPath_Button['state'] = tk.NORMAL

    # 「選択」ボタンを無効にする.
    def disable_select_button(self):
        self.SelectWorksheetPath_Button['state'] = tk.DISABLED

    # 「出題範囲選択」のチェックボタンを有効にする.
    def enable_grade_checkbutton(self):
        for key in self.UserSettings.kGradeKeyList:
            self.ProblemRegionFrame_Checkbutton[key]['state'] = tk.NORMAL

    # 「出題範囲選択」のチェックボタンを無効にする.
    def disable_grade_checkbutton(self):
        for key in self.UserSettings.kGradeKeyList:
            self.ProblemRegionFrame_Checkbutton[key]['state'] = tk.DISABLED

    # 「出題数」のエントリーを有効にする.
    def enable_number_of_problem_entry(self):
        self.SelectNumberOfProblemFrame_Entry['state'] = tk.NORMAL

    # 「出題数」のエントリーを無効にする.
    def disable_number_of_problem_entry(self):
        self.SelectNumberOfProblemFrame_Entry['state'] = tk.DISABLED

    # 「出題モード」のラジオボタンを有効にする.
    def enable_mode_Radiobutton(self):
        for key in self.UserSettings.kModeKeyList:
            self.SelectModeFrame_Radiobutton[key]['state'] = tk.NORMAL

    # 「出題モード」のラジオボタンを無効にする.
    def disable_mode_Radiobutton(self):
        for key in self.UserSettings.kModeKeyList:
            self.SelectModeFrame_Radiobutton[key]['state'] = tk.DISABLED

    # 「回答」のエントリーを有効にする.
    def enable_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key]['state'] = tk.NORMAL

    # 「回答」のエントリーを無効にする.
    def disable_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key]['state'] = tk.DISABLED

    #  「正解/不正解」入力ボタンを有効にする.
    def enable_scoring_answer_button(self, key):
        self.ScoringFrame_AnsFrame_Button[key]['state'] = tk.NORMAL

    #  「正解/不正解」入力ボタンを無効にする.
    def disable_scoring_answer_button(self, key):
        self.ScoringFrame_AnsFrame_Button[key]['state'] = tk.DISABLED

    # 「採点完了」ボタンを有効にする.
    def enable_scoring_button(self):
        self.Scoring_EndFrame_Button['state'] = tk.NORMAL

    # 「採点完了」ボタンを無効にする.
    def disable_scoring_button(self):
        self.Scoring_EndFrame_Button['state'] = tk.DISABLED

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

    # 「分析」ボタンを有効にする.
    def enable_analysis_button(self):
        self.Analysis_Button['state'] = tk.NORMAL

    # 「分析」ボタンを有効にする.
    def disable_analysis_button(self):
        self.Analysis_Button['state'] = tk.DISABLED

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

        # 学年の情報を取得し, 設定する.
        self.set_grade()

    # 学年の設定を設定する.
    # 処理概要:
    # チェックボタンの値をリスト化し, 設定する.
    def set_grade(self):
        grade_list = []
        for key, grade in zip(self.UserSettings.kGradeKeyList, self.grade_value_list):
            checked = self.get_selected_student_grade(key)
            # チェックしている時
            if checked == True:
                grade_list.append(grade)

        ################################################################################
        # 学年を設定する.
        self.KanjiWorkSheet.set_grade(grade_list)
        ################################################################################

    def set_mode(self):
        ################################################################################
        # 出題モードを設定する.
        self.KanjiWorkSheet.set_mode(self.get_selected_student_mode())
        ################################################################################

    # 「問題数」エントリーを有効にする.
    def enable_report_tolnum_entry(self, key):
        self.Report_Problem_Entry_TolNum[key].configure(state='normal')

    # 「問題数」エントリーを無効にする.
    def disable_report_tolnum_entry(self, key):
        self.Report_Problem_Entry_TolNum[key].configure(state='readonly')

    # 「問題数」エントリーのデータを削除する.
    def delete_report_tolnum_entry(self, key):
        self.Report_Problem_Entry_TolNum[key].delete('0', 'end')

    # 「問題数」エントリーのデータを挿入する.
    def insert_report_tolnum_entry(self, key, value):
        self.Report_Problem_Entry_TolNum[key].insert('end', value)

    # 「出題数」エントリーを有効にする.
    def enable_report_outnum_entry(self, key):
        self.Report_Problem_Entry_OutNum[key].configure(state='normal')

    # 「出題数」エントリーを無効にする.
    def disable_report_outnum_entry(self, key):
        self.Report_Problem_Entry_OutNum[key].configure(state='readonly')

    # 「出題数」エントリーのデータを削除する.
    def delete_report_outnum_entry(self, key):
        self.Report_Problem_Entry_OutNum[key].delete('0', 'end')

    # 「出題数」エントリーのデータを挿入する.
    def insert_report_outnum_entry(self, key, value):
        self.Report_Problem_Entry_OutNum[key].insert('end', value)

    # 「出題数」エントリーのデータを取得する.
    def get_report_outnum_entry(self, key):
        data = self.Report_Problem_Entry_OutNum[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 「正解数」エントリーを有効にする.
    def enable_report_crctnum_entry(self, key):
        self.Report_Correct_Entry_Num[key].configure(state='normal')

    # 「正解数」エントリーを無効にする.
    def disable_report_crctnum_entry(self, key):
        self.Report_Correct_Entry_Num[key].configure(state='readonly')

    # 「正解数」エントリーのデータを削除する.
    def delete_report_crctnum_entry(self, key):
        self.Report_Correct_Entry_Num[key].delete('0', 'end')

    # 「正解数」エントリーのデータを挿入する.
    def insert_report_crctnum_entry(self, key, value):
        self.Report_Correct_Entry_Num[key].insert('end', value)

    # 「正解数」エントリーのデータを取得する.
    def get_report_crctnum_entry(self, key):
        data = self.Report_Correct_Entry_Num[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 「不正解数」エントリーを有効にする.
    def enable_report_inctnum_entry(self, key):
        self.Report_InCorrect_Entry_Num[key].configure(state='normal')

    # 「不正解数」エントリーを無効にする.
    def disable_report_inctnum_entry(self, key):
        self.Report_InCorrect_Entry_Num[key].configure(state='readonly')

    # 「不正解数」エントリーのデータを削除する.
    def delete_report_inctnum_entry(self, key):
        self.Report_InCorrect_Entry_Num[key].delete('0', 'end')

    # 「不正解数」エントリーのデータを挿入する.
    def insert_report_inctnum_entry(self, key, value):
        self.Report_InCorrect_Entry_Num[key].insert('end', value)

    # 「不正解数」エントリーのデータを取得する.
    def get_report_inctnum_entry(self, key):
        data = self.Report_InCorrect_Entry_Num[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 「１日後」エントリーを有効にする.
    def enable_report_daynum_entry(self, key):
        self.Report_Day_Entry_Num[key].configure(state='normal')

    # 「１日後」エントリーを無効にする.
    def disable_report_daynum_entry(self, key):
        self.Report_Day_Entry_Num[key].configure(state='readonly')

    # 「１日後」エントリーのデータを削除する.
    def delete_report_daynum_entry(self, key):
        self.Report_Day_Entry_Num[key].delete('0', 'end')

    # 「１日後」エントリーのデータを挿入する.
    def insert_report_daynum_entry(self, key, value):
        self.Report_Day_Entry_Num[key].insert('end', value)

    # 「１日後」エントリーのデータを取得する.
    def get_report_daynum_entry(self, key):
        data = self.Report_Day_Entry_Num[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 「１週間後」エントリーを有効にする.
    def enable_report_wknum_entry(self, key):
        self.Report_Week_Entry_Num[key].configure(state='normal')

    # 「１週間後」エントリーを無効にする.
    def disable_report_wknum_entry(self, key):
        self.Report_Week_Entry_Num[key].configure(state='readonly')

    # 「１週間後」エントリーのデータを削除する.
    def delete_report_wknum_entry(self, key):
        self.Report_Week_Entry_Num[key].delete('0', 'end')

    # 「１週間後」エントリーのデータを挿入する.
    def insert_report_wknum_entry(self, key, value):
        self.Report_Week_Entry_Num[key].insert('end', value)

    # 「１週間後」エントリーのデータを取得する.
    def get_report_wknum_entry(self, key):
        data = self.Report_Week_Entry_Num[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 「１ヶ月後」エントリーを有効にする.
    def enable_report_mtnum_entry(self, key):
        self.Report_Month_Entry_Num[key].configure(state='normal')

    # 「１ヶ月後」エントリーを無効にする.
    def disable_report_mtnum_entry(self, key):
        self.Report_Month_Entry_Num[key].configure(state='readonly')

    # 「１ヶ月後」エントリーのデータを削除する.
    def delete_report_mtnum_entry(self, key):
        self.Report_Month_Entry_Num[key].delete('0', 'end')

    # 「１ヶ月後」エントリーのデータを挿入する.
    def insert_report_mtnum_entry(self, key, value):
        self.Report_Month_Entry_Num[key].insert('end', value)

    # 「１ヶ月後」エントリーのデータを取得する.
    def get_report_mtnum_entry(self, key):
        data = self.Report_Month_Entry_Num[key].get().split('(')[0]
        if data.isdigit():
            return int(data)
        else:
            return 0

    # 漢字プリントのパスを取得する.
    def get_kanji_worksheet_path(self):
        name_t = self.KanjiWorkSheet.get_student_name()
        name = ''
        for word in list(name_t):
            if word == u' ' or word == u'　':
                name += '_'
            else:
                name += word

        if self.KanjiWorkSheet.kMDRW == self.KanjiWorkSheet.get_mode():
            mode_str = '復習モード'
        elif self.KanjiWorkSheet.kMDTR == self.KanjiWorkSheet.get_mode():
            mode_str = '練習モード'
        else:
            mode_str = '苦手モード'

        return './' + name + '_漢字テスト_' + mode_str + '.pdf'

    def update_scoring(self):
        """採点を更新する."""
        self.KanjiWorkSheet.print_info('Call: update_scoring')
        keys = [
                 '①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩'
                ,'⑪','⑫','⑬','⑭','⑮','⑯','⑰','⑱','⑲','⑳'
        ]
        # 採点の内容を削除
        for key in keys:
            # 答えを表示するフレームを初期化
            self.enable_scoring_answer_text(key)
            self.delete_scoring_answer_text(key)
            self.disable_scoring_answer_text(key)
            # 採点をするためのボタン
            self.enable_scoring_answer_button(key)
            self.set_scoring_answer_button_display(key, '―')
            self.disable_scoring_answer_button(key)
            # 採点をするためのボタンの表示内容
            self.set_scoring_answer_button_display_value(key, None)

        # ログファイルから情報を取得し, 反映する.
        (err_num, _, ans_list) = self.KanjiWorkSheet.get_column_kanji_worksheet_log(self.get_path_of_log(), self.KanjiWorkSheet.kAnswer)
        if err_num == 0:
            # 答えを印字
            for ans, key in zip(ans_list, keys):
                for ans_i in range(0, len(ans)):
                    self.enable_scoring_answer_text(key)
                    self.insert_scoring_answer_text(key, ans[ans_i])
                    self.insert_scoring_answer_text(key, '\n')
                    self.disable_scoring_answer_text(key)

        (err_num, _, result_list) = self.KanjiWorkSheet.get_column_kanji_worksheet_log(self.get_path_of_log(), self.KanjiWorkSheet.kResult)
        if err_num == 0:
            # 結果を反映
            for result, key in zip(result_list, keys):
                self.enable_scoring_answer_button(key)
                if   result == self.KanjiWorkSheet.kIncrctMk:
                    self.set_scoring_answer_button_display_value(key, False)
                    self.set_scoring_answer_button_display(key, '✕')
                elif result == self.KanjiWorkSheet.kCrctMk:
                    self.set_scoring_answer_button_display_value(key, True)
                    self.set_scoring_answer_button_display(key, '○')
                else:
                    self.set_scoring_answer_button_display_value(key, None)
                    if   result == self.KanjiWorkSheet.kDayMk:
                        self.set_scoring_answer_button_display(key, 'Ｄ')
                    elif result == self.KanjiWorkSheet.kWeekMk:
                        self.set_scoring_answer_button_display(key, 'Ｗ')
                    elif result == self.KanjiWorkSheet.kMonthMk:
                        self.set_scoring_answer_button_display(key, 'Ｍ')
                    else:
                        self.set_scoring_answer_button_display(key, '―')

        return err_num

    def insert_fluc_msg(self, diff, old, new):
        if   diff == 1 and new < old:
            msg = str(new) + '(↓' + str(old - new) + ')'
        elif diff == 1 and new > old:
            msg = str(new) + '(↑' + str(new - old) + ')'
        else:
            msg = str(new)

        return msg

    def update_report(self, diff=0):
        """レポートを更新する."""
        grade_list = [[1], [2], [3], [4], [5], [6], [7], [8], [9], [1, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.KanjiWorkSheet.print_info('レポートを更新する.')

        (err_num, _, _, _) = self.KanjiWorkSheet.load_worksheet(self.SelectWorksheetPath_Value.get())
        if err_num != 0:
            return

        for key, grade in zip(self.kGradeReportList, grade_list):
            self.enable_report_tolnum_entry(key)
            self.enable_report_outnum_entry(key)
            self.enable_report_crctnum_entry(key)
            self.enable_report_inctnum_entry(key)
            self.enable_report_daynum_entry(key)
            self.enable_report_wknum_entry(key)
            self.enable_report_mtnum_entry(key)

            outnum_old = self.get_report_outnum_entry(key)
            crctnum_old = self.get_report_crctnum_entry(key)
            inctnum_old = self.get_report_inctnum_entry(key)
            daynum_old = self.get_report_daynum_entry(key)
            wknum_old = self.get_report_wknum_entry(key)
            mtnum_old = self.get_report_mtnum_entry(key)

            self.delete_report_tolnum_entry(key)
            self.delete_report_outnum_entry(key)
            self.delete_report_crctnum_entry(key)
            self.delete_report_inctnum_entry(key)
            self.delete_report_daynum_entry(key)
            self.delete_report_wknum_entry(key)
            self.delete_report_mtnum_entry(key)

            tolnum = len(self.KanjiWorkSheet.get_problem_with_grade(grade))
            self.insert_report_tolnum_entry(key, str(tolnum))

            outnum = len(self.KanjiWorkSheet.get_problem_with_grade(grade)) \
                   - len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kNotMk))

            msg = self.insert_fluc_msg(diff, outnum_old, outnum)
            self.insert_report_outnum_entry(key, msg)

            crctnum = len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kCrctMk))
            msg = self.insert_fluc_msg(diff, crctnum_old, crctnum)
            self.insert_report_crctnum_entry(key, msg)

            inctnum = len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kIncrctMk))
            msg = self.insert_fluc_msg(diff, inctnum_old, inctnum)
            self.insert_report_inctnum_entry(key, msg)

            daynum = len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kDayMk))
            msg = self.insert_fluc_msg(diff, daynum_old, daynum)
            self.insert_report_daynum_entry(key, msg)

            wknum = len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kWeekMk))
            msg = self.insert_fluc_msg(diff, wknum_old, wknum)
            self.insert_report_wknum_entry(key, msg)

            mtnum = len(self.KanjiWorkSheet.get_problem_with_status(grade, self.KanjiWorkSheet.kMonthMk))
            msg = self.insert_fluc_msg(diff, mtnum_old, mtnum)
            self.insert_report_mtnum_entry(key, msg)

            self.disable_report_tolnum_entry(key)
            self.disable_report_outnum_entry(key)
            self.disable_report_crctnum_entry(key)
            self.disable_report_inctnum_entry(key)
            self.disable_report_daynum_entry(key)
            self.disable_report_wknum_entry(key)
            self.disable_report_mtnum_entry(key)

    ################################################################################
    # イベント関数
    ################################################################################
    # イベント発生条件:「登録」ボタンを押したとき
    # 処理概要:「生徒登録」エントリーに記入した名前を設定ファイルに登録する.
    def Event_RegisterStudent(self):
        self.KanjiWorkSheet.print_info('Call: Event_RegisterStudent')
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
                self.KanjiWorkSheet.print_info('生徒(' + name + ')の新規登録を行いました.')
                # 生徒を設定ファイルに登録する.
                self.UserSettings.register_student(name)

                # 生徒を設定ファイルに登録した後に, 登録できたことを伝えるために「生徒登録」エントリーを空欄にする.
                # 煩わしいため, メッセージボックスは使用しない.
                self.del_registered_student_entry()

    # イベント発生条件:「生徒選択」コンボボックスを押したとき
    # 処理概要:「生徒選択」コンボボックスのメニューを更新する.
    def Event_UpdateStudent(self):
        self.KanjiWorkSheet.print_info('Call: Event_UpdateStudent')
        # 生徒の登録がある場合は, 設定ファイルから生徒の名前を取得して,
        # 「生徒選択」コンボボックスのメニューに設定する.
        if self.UserSettings.get_setting_num() != 0:
            self.set_selected_student_list(self.UserSettings.get_student_name_list())
        # 生徒の登録がない場合は, 「生徒選択」コンボボックスのメニューを空欄にする.
        else:
            self.set_selected_student_list('')

    # イベント発生条件:「生徒選択」コンボボックスを押し, 生徒を選択したとき
    # 処理概要:選択した生徒の設定に更新する.
    def Event_SelectStudent(self, event):
        self.KanjiWorkSheet.print_info('Call: Event_SelectStudent')
        ################################################################################
        # 「生徒選択」コンボボックスで選択した生徒の名前を取得し, 生徒の名前を設定する.
        name = self.get_selected_student_name()
        self.KanjiWorkSheet.set_student_name(name)
        ################################################################################
        # 名前が有効なとき
        if len(name) > 0:
            # 「削除」ボタンを有効にする.
            self.enable_delete_student_button()

            # 「選択」ボタンを有効にする.
            self.enable_select_button()

            # 選択した生徒の問題集のパスを取得し、登録する.
            path = self.UserSettings.get_path_of_problem(name)
            self.set_selected_worksheet_path(path)

            ################################################################################
            # 登録した問題集のパスを取得し, 問題集を読み込む.
            (opn_err_num, _, fmt_err_num, fmt_err_msg) = self.KanjiWorkSheet.load_worksheet(path)
            ################################################################################
            # 問題集を正しく読み込めた場合.
            if opn_err_num == 0 and fmt_err_num == 0:
                # 「プリント作成」ボタンを有効にする.
                self.enable_create_button()
                # 「印刷」ボタンを有効にする.
                self.enable_print_button()
                # 「分析」ボタンを有効にする.
                self.enable_analysis_button()
            else:
                # 「プリント作成」ボタンを無効にする.
                self.disable_create_button()
                # 「印刷」ボタンを無効にする.
                self.disable_print_button()
                # 「分析」ボタンを有効にする.
                self.disable_analysis_button()
                # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
                # ただし, ファイルが存在しないことをこのイベントでは通知しない.(煩わしいため)
                for msg in fmt_err_msg:
                    tk.messagebox.showerror('Error', msg)

            # 学年の設定を反映する.
            for key in self.UserSettings.kGradeKeyList:
                # 「出題範囲選択」のチェックボタンを有効にする.
                self.enable_grade_checkbutton()
                # 設定ファイルからチェックボタンの設定を取得し, 反映する.
                value = str(self.UserSettings.get_grade_value(name, key))
                self.set_selected_student_grade(key, value)

            # 学年の情報を取得し, 設定する.
            self.set_grade()

            # 「出題数」のエントリーを有効にする.
            self.enable_number_of_problem_entry()
            # 選択した生徒の出題数を設定する.
            self.set_number_of_problem(self.UserSettings.get_number_of_problem(name))

            # 「出題モード」のエントリーを有効にする.
            self.enable_mode_Radiobutton()
            # 設定ファイルからラジオボタンの設定を取得し, 反映する.
            value = self.UserSettings.get_mode(name)
            self.set_selected_student_mode(value)

            # 「出題モード」を設定する.
            self.set_mode()

            # 採点を更新する.
            err_num = self.update_scoring()
            if err_num == 0:
                # 「採点完了」ボタンを有効にする.
                self.enable_scoring_button()
            else:
                # 「採点完了」ボタンを無効にする.
                self.disable_scoring_button()

        # レポートを更新する.
        self.update_report()

    # イベント発生条件:「削除」ボタンを押したとき
    # 処理概要:「生徒選択」コンボボックスに記入している生徒を削除する.
    def Event_DeleteStudent(self):
        self.KanjiWorkSheet.print_info('Call: Event_DeleteStudent')
        # 現在選択している登録者を削除する.
        # コンボボックスから登録者名を取得する.
        name = self.get_selected_student_name()
        # 名前が有効なとき
        if len(name) > 0:
            msg = tk.messagebox.askquestion('Warning', '本当に削除しますか.', default='no')
            if msg == 'yes':
                # 漢字プリントのログを削除する.
                self.KanjiWorkSheet.delete_kanji_worksheet_logfile(self.get_path_of_log())

                # 設定ファイルの該当データを削除する.
                i = self.setting[self.setting[self.kStudentName] == name].index[0]
                self.setting = self.setting.drop(i)
                self.setting = self.setting.reset_index(drop=True)

                # 設定ファイルに保存する.
                self.save_setting_file()

                # 削除後、生徒選択用のコンボボックスをクリアする.
                self.set_selected_student_list('')
                ################################################################################
                # 生徒の名前を変更する.
                self.KanjiWorkSheet.set_student_name('')
                ################################################################################

                # 「削除] ボタンを無効にする.
                self.disable_delete_student_button()

                # 問題集の内容をクリアし, 選択ボタンを無効にする.
                # 「選択」ボタンを無効にする.
                self.disable_select_button()
                # 「問題集選択」エントリーを空白に設定する.
                self.set_selected_worksheet_path('')
                ################################################################################
                # 問題集を読み込んで内容クリアする.
                path = self.get_selected_worksheet_path()
                self.KanjiWorkSheet.load_worksheet(path)
                ################################################################################

                # チェックボタンの値をクリアし, チェックボタンを無効にする.
                self.del_grade()

                # 問題数の値をクリアし, 入力欄を無効にする.
                self.set_number_of_problem('')
                # 出題数のエントリーを無効にする.
                self.disable_number_of_problem_entry()

                # 「採点完了」ボタンを無効にする.
                self.disable_scoring_button()
                # 「プリント作成」ボタンを無効にする.
                self.disable_create_button()
                # 「印刷」ボタンを無効にする.
                self.disable_print_button()
                # 「分析」ボタンを有効にする.
                self.disable_analysis_button()

                # 採点を更新する.
                self.update_scoring()
                # レポートを更新する.
                self.update_report()

    # イベント発生条件:「選択」ボタンを押したとき
    # 処理概要:選択したCSVファイルを設定する.
    def Event_SelectKanjiWorkSheet(self):
        self.KanjiWorkSheet.print_info('Call: Event_SelectKanjiWorkSheet')
        path = filedialog.askopenfilename(
                  filetypes=[('', '*.csv')]
                , initialdir=os.path.abspath(os.path.dirname(__file__))
        )
        # ファイルパスが有効なとき
        if len(path) > 0:
            # 相対パスに変更する.
            path = './' + os.path.relpath(path)
            # 「問題集選択」エントリーを設定する.
            self.set_selected_worksheet_path(path)

            # 登録者の情報を更新する
            name = self.get_selected_student_name()
            self.UserSettings.set_path_of_problem(name, path)
            # 設定ファイルに保存する.
            self.UserSettings.save_setting_file()

            ################################################################################
            # 登録した問題集のパスを取得し, 問題集を読み込む.
            (_, _, err, err_msg) = self.KanjiWorkSheet.load_worksheet(path)
            ################################################################################
            # 問題集を正しく読み込めたとき
            if err == 0:
                # 「採点完了」ボタンを有効にする.
                self.enable_scoring_button()
                # 「プリント作成」ボタンを有効にする.
                self.enable_create_button()
                # 「印刷」ボタンを有効にする.
                self.enable_print_button()
                # 「分析」ボタンを有効にする.
                self.enable_analysis_button()

            # 問題集を正しく読み込めなかったとき
            else:
                # 「採点完了」ボタンを無効にする.
                self.disable_scoring_button()
                # 「プリント作成」ボタンを無効にする.
                self.disable_create_button()
                # 「印刷」ボタンを無効にする.
                self.disable_print_button()
                # 「分析」ボタンを有効にする.
                self.disable_analysis_button()

                # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
                for msg in err_msg:
                    tk.messagebox.showerror('Error', msg)

            # 登録者を変更, 問題集を新しく読み直したため, レポートを更新する.
            self.update_report()

    # イベント発生条件:「出題範囲選択」チェックボックスを選択したとき
    # 処理概要:チェックボックスの値が変化したとき, 設定を反映する.
    def Event_CheckButton(self):
        self.KanjiWorkSheet.print_info('Call: Event_CheckButton')
        # 登録者の要素数を取得する.
        name = self.get_selected_student_name()

        # 各チェックボタンの値を取得し, 登録者の情報を更新する.
        for key in self.UserSettings.kGradeKeyList:
            self.UserSettings.set_grade_value(name, key, self.get_selected_student_grade(key))

        # 設定ファイルに保存する.
        self.UserSettings.save_setting_file()

        # 学年の情報を取得し, 設定する.
        self.set_grade()

    def Event_RadioButton(self):
        self.KanjiWorkSheet.print_info('Call: Event_RadioButton')

        # 登録者を取得する.
        name = self.get_selected_student_name()

        # ラジオボタンの値を取得し, 登録者の情報を更新する.
        self.UserSettings.set_mode(name, self.get_selected_student_mode())

        # 設定ファイルに保存する.
        self.UserSettings.save_setting_file()

        # 出題モードを取得し, 設定する.
        self.set_mode()

        # 採点を更新する.
        err_no = self.update_scoring()
        if err_no == 0:
            # 「採点完了」ボタンを有効にする.
            self.enable_scoring_button()
        else:
            # 「採点完了」ボタンを無効にする.
            self.disable_scoring_button()

    # イベント発生条件:「出題数」エントリーを変更したとき
    # 処理概要:出題数を更新する.
    def Event_ChangeNumberOfProblem(self, var, indx, mode):
        self.KanjiWorkSheet.print_info('Call: Event_ChangeNumberOfProblem')
        num = self.get_number_of_problem()
        self.KanjiWorkSheet.set_number_of_problem(num)

        # 選択している生徒が設定ファイルに存在しているとき, 設定ファイルに出題数を保存する.
        name = self.get_selected_student_name()
        if self.UserSettings.chk_registered_student(name):
            self.UserSettings.set_number_of_problem(name, num)

            # 設定ファイルを保存する.
            self.UserSettings.save_setting_file()

    # イベント発生条件:「採点」のボタンを押したとき
    # 処理概要:ボタンが押されたとき, ボタンを○または, ×に切り替える.
    def Event_ChangeResult(self, key):
        self.set_scoring_answer_button_display_value(key, not self.get_scoring_answer_button_value(key))
        if self.get_scoring_answer_button_value(key) == True:
            self.set_scoring_answer_button_display(key, '○')
        else:
            self.set_scoring_answer_button_display(key, '✕')

    # イベント発生条件:「採点完了」ボタンを押したとき
    # 処理概要:採点結果を問題集に反映する.
    def Event_PushBtnScoreing(self):
        self.KanjiWorkSheet.print_info('Call: Event_PushBtnScoreing')
        keys = [
                  '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'
                , '⑪', '⑫', '⑬', '⑭', '⑮', '⑯', '⑰', '⑱', '⑲', '⑳'
        ]
        path = self.get_path_of_log()
        (err, err_msg, ans_list) = self.KanjiWorkSheet.get_column_kanji_worksheet_log(path, self.KanjiWorkSheet.kAnswer)
        # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
        for msg in err_msg:
            tk.messagebox.showerror('Error', msg)

        # 採点フレームのスイッチの値から, 問題に正解したか否かを判断する.
        unans = False
        result = []
        for i in range(0, len(ans_list)):
            status = self.get_scoring_answer_button_value(keys[i])
            if status == None:
                unans = True
            else:
                if status == True:
                    result.append(self.KanjiWorkSheet.kCrctMk)
                else:
                    result.append(self.KanjiWorkSheet.kIncrctMk)

        if unans:
            tk.messagebox.showerror('Error', '未回答の項目があります.')
        else:
            ################################################################################
            # ログファイルに採点結果を反映する.
            self.KanjiWorkSheet.record_kanji_worksheet_logfile(path, result)
            # ログファイルの採点結果を問題集に反映する.
            (opn_err, opn_err_msg, fmt_err, fmt_err_msg) = self.KanjiWorkSheet.update_kanji_worksheet(path)
            if opn_err:
                for msg in opn_err_msg:
                    tk.messagebox.showerror('Error', msg)

            if fmt_err:
                for msg in fmt_err_msg:
                    tk.messagebox.showerror('Error', msg)

            if opn_err == False and fmt_err == False:
                # 問題集を上書きする.
                (wrt_err, wrt_err_msg) = self.KanjiWorkSheet.save_worksheet()
                if wrt_err:
                    for msg in wrt_err_msg:
                        tk.messagebox.showerror('Error', msg)

                if wrt_err != True:
                    ################################################################################
                    # ログファイルを削除する.
                    self.KanjiWorkSheet.delete_kanji_worksheet_logfile(path)
                    ################################################################################

                    # 「採点完了」ボタンを無効にする.
                    self.disable_scoring_button()
                    # 採点を更新する.
                    self.update_scoring()
                    # レポートを更新する.
                    self.update_report(diff=1)
                    # 修了メッセージを表示する.
                    tk.messagebox.showinfo('Info', '問題集に結果を反映しました.')

    # イベント発生条件:「プリント作成」ボタンを押したとき
    # 処理概要:漢字プリントを作成する.
    def Event_CreateKanjiWorkSheet(self):
        self.KanjiWorkSheet.print_info('Call: Event_CreateKanjiWorkSheet')

        # 問題集を改めて読み込む.
        worksheet_path = self.get_selected_worksheet_path()
        (err, err_msg, _, _) = self.KanjiWorkSheet.load_worksheet(worksheet_path)
        if err != 0:
            # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
            for msg in err_msg:
                tk.messagebox.showerror('Error', msg)

        # 出題数を設定する.
        self.set_number_of_problem(self.get_number_of_problem())

        # 学年を取得する.
        grade = self.KanjiWorkSheet.get_grade()
        # 学年を選択していないとき
        if len(grade) == 0:
            tk.messagebox.showerror('Error', '学年を選択して, 出題範囲を決定してください.')
        # 学年を選択しているとき
        else:
            # 採点が残っているとき
            log_path = self.get_path_of_log()
            yes = True
            if os.path.exists(log_path):
                msg = tk.messagebox.askquestion('Warning', '採点が終わっていません. このまま続けますか.', default='no')
                if msg == 'no':
                    yes = False

            # 漢字プリントを作成する.
            if yes:
                ################################################################################
                # ログファイルを削除する.
                self.KanjiWorkSheet.delete_kanji_worksheet_logfile(log_path)
                # 漢字プリントを作成する.
                self.KanjiWorkSheet.create_kanji_worksheet()
                # 漢字プリントの概要を表示する.
                self.KanjiWorkSheet.report_kanji_worksheet()
                # 漢字プリントの出題記録を作成する.
                result = self.KanjiWorkSheet.create_kanji_worksheet_logfile(log_path)
                ################################################################################

                ################################################################################
                # 漢字プリントをPFDで作成する.
                self.path_of_worksheet = self.get_kanji_worksheet_path()
                self.KanjiWorkSheet.generate_pdf_kanji_worksheet(self.path_of_worksheet)
                ################################################################################

                # 採点を更新する.
                self.update_scoring()
                if result == True:
                    # 「採点完了」ボタンを有効にする.
                    self.enable_scoring_button()
                else:
                    # 「採点完了」ボタンを無効にする.
                    self.disable_scoring_button()

                # 終了メッセージを表示する.
                tk.messagebox.showinfo('Info', os.path.basename(self.path_of_worksheet) + ' を作成しました.')
            else:
                # 中止メッセージを表示する.
                tk.messagebox.showinfo('Info', '中止しました.')

    # イベント発生条件:「プリント作成」ボタンを押したとき
    # 処理概要:漢字プリントを作成する.
    def Event_PrintOut(self):
        self.path_of_worksheet = self.get_kanji_worksheet_path()
        if os.path.exists(self.path_of_worksheet):
            subprocess.Popen(['start', self.path_of_worksheet], shell=True)
        else:
            # 対象ファイルが存在しない/
            tk.messagebox.showinfo('Info', '漢字プリントを作成してください.')

# WidgetReport.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk


class WidgetReport:
    # レポート用のウィジェット作成
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

        self.kTotal = '　　　合計'
        self.kGradeReportList = [
            self.UserSettings.kJS1,
            self.UserSettings.kJS2,
            self.UserSettings.kJS3,
            self.UserSettings.kJS4,
            self.UserSettings.kJS5,
            self.UserSettings.kJS6,
            self.kTotal
        ]

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

        # レポート
        self.create_widget_report_Problem(self.Report_ProblemFrame, self.kGradeReportList, u'出題状況')
        self.create_widget_report_Correct(self.Report_CorrectFrame, self.kGradeReportList, u'　正解')
        self.create_widget_report_InCorrect(self.Report_InCorrectFrame, self.kGradeReportList, u'不正解')
        self.create_widget_report_Day(self.Report_DayFrame, self.kGradeReportList, u'1日後')
        self.create_widget_report_Week(self.Report_WeekFrame, self.kGradeReportList, u'1週間後')
        self.create_widget_report_Month(self.Report_MonthFrame, self.kGradeReportList, u'1ヶ月後')

    def set_class(self, kanji_worksheet, wg_select_work_sheet_path):
        self.KanjiWorkSheet = kanji_worksheet
        self.WidgetSelectWorkSheetPath = wg_select_work_sheet_path

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

    def update_report(self, diff=0):
        """レポートを更新する."""
        self.DebugPrint.print_info('レポートを更新する.')

        grade_list = [[1], [2], [3], [4], [5], [6], [1, 2, 3, 4, 5, 6]]

        # 問題集をロードする.
        path = self.WidgetSelectWorkSheetPath.get_selected_worksheet_path()
        (err_num, _, _, _) = self.KanjiWorkSheet.load_worksheet(path)

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

    def insert_fluc_msg(self, diff, old, new):
        if   diff == 1 and new < old:
            msg = str(new) + '(↓' + str(old - new) + ')'
        elif diff == 1 and new > old:
            msg = str(new) + '(↑' + str(new - old) + ')'
        else:
            msg = str(new)

        return msg

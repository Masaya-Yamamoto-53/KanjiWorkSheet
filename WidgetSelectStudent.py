# WidgetSelectStudent.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class WidgetSelectStudent:
    # 生徒登録用のウィジェット作成
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

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
            , values=values
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

    def set_class(
              self
            , kanji_worksheet
            , create_file_path
            , wg_select_work_sheet_path
            , wg_create_worksheet
            , wg_problem_region
            , wg_select_number_of_problem
            , wg_select_mode
            , wg_scoring
            , wg_report
    ):
        self.KanjiWorkSheet = kanji_worksheet
        self.CreateFilePath = create_file_path
        self.WidgetSelectWorkSheetPath = wg_select_work_sheet_path
        self.WidgetCreateWorkSheet = wg_create_worksheet
        self.WidgetProblemRegion = wg_problem_region
        self.WidgetSelectNumberOfProblem = wg_select_number_of_problem
        self.WidgetSelectMode = wg_select_mode
        self.WidgetScoring = wg_scoring
        self.WidgetReport = wg_report

    # イベント発生条件:「生徒選択」コンボボックスを押したとき
    # 処理概要:「生徒選択」コンボボックスのメニューを更新する.
    def Event_UpdateStudent(self):
        self.DebugPrint.print_info('Call: Event_UpdateStudent')
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
        self.DebugPrint.print_info('Call: Event_SelectStudent')
        # 「生徒選択」コンボボックスで選択した生徒の名前を取得する.
        name = self.get_selected_student_name()
        # 名前が有効なとき
        if len(name) > 0:
            # 「削除」ボタンを有効にする.
            self.enable_delete_student_button()
            # 「選択」ボタンを有効にする.
            self.WidgetSelectWorkSheetPath.enable_select_button()
            # 選択した生徒の問題集のパスを取得し、登録する.
            path = self.UserSettings.get_path_of_problem(name)
            self.WidgetSelectWorkSheetPath.set_selected_worksheet_path(path)

            ################################################################################
            # 登録した問題集のパスを取得し, 問題集を読み込む.
            (opn_err_num, _, fmt_err_num, fmt_err_msg) = self.KanjiWorkSheet.load_worksheet(path)
            ################################################################################

            # 問題集を正しく読み込めた場合.
            if opn_err_num == 0 and fmt_err_num == 0:
                # 「プリント作成」ボタンを有効にする.
                self.WidgetCreateWorkSheet.enable_create_button()
                # 「印刷」ボタンを有効にする.
                self.WidgetCreateWorkSheet.enable_print_button()
            else:
                # 「プリント作成」ボタンを無効にする.
                self.WidgetCreateWorkSheet.disable_create_button()
                # 「印刷」ボタンを無効にする.
                self.WidgetCreateWorkSheet.disable_print_button()
                # 何らかのエラーメッセージを取得した場合は, メッセージボックスで通知する.
                # ただし, ファイルが存在しないことをこのイベントでは通知しない.(煩わしいため)
                for msg in fmt_err_msg:
                    tk.messagebox.showerror('Error', msg)

            # 学年の設定を反映する.
            for key in self.UserSettings.kGradeKeyList:
                # 「出題範囲選択」のチェックボタンを有効にする.
                self.WidgetProblemRegion.enable_grade_checkbutton()
                # 設定ファイルからチェックボタンの設定を取得し, 反映する.
                value = str(self.UserSettings.get_grade_value(name, key))
                self.WidgetProblemRegion.set_selected_student_grade(key, value)

            # 「出題数」のエントリーを有効にする.
            self.WidgetSelectNumberOfProblem.enable_number_of_problem_entry()

            # 選択した生徒の出題数を設定する.
            self.WidgetSelectNumberOfProblem.set_number_of_problem(self.UserSettings.get_number_of_problem(name))

            # 「出題モード」のエントリーを有効にする.
            self.WidgetSelectMode.enable_mode_Radiobutton()

            # 設定ファイルからラジオボタンの設定を取得し, 反映する.
            value = self.UserSettings.get_mode(name)
            self.WidgetSelectMode.set_selected_student_mode(value)

            # 採点を更新する.
            err_num = self.WidgetScoring.update_scoring()
            if err_num == 0:
                # 「採点完了」ボタンを有効にする.
                self.WidgetScoring.enable_scoring_button()
            else:
                # 「採点完了」ボタンを無効にする.
                self.WidgetScoring.disable_scoring_button()

        # レポートを更新する.
        self.WidgetReport.update_report()

    # イベント発生条件:「削除」ボタンを押したとき
    # 処理概要:「生徒選択」コンボボックスに記入している生徒を削除する.
    def Event_DeleteStudent(self):
        self.DebugPrint.print_info('Call: Event_DeleteStudent')
        # 現在選択している登録者を削除する.
        # コンボボックスから登録者名を取得する.
        name = self.get_selected_student_name()
        # 名前が有効なとき
        if len(name) > 0:
            msg = tk.messagebox.askquestion('Warning', '本当に削除しますか.', default='no')
            if msg == 'yes':
                # 漢字プリントのログを削除する.
                self.KanjiWorkSheet.delete_kanji_worksheet_logfile(self.CreateFilePath.get_path_of_log())

                # 設定ファイルの該当データを削除する.
                self.UserSettings.delete_student(name)

                # 設定ファイルに保存する.
                self.UserSettings.save_setting_file()

                # 削除後、生徒選択用のコンボボックスをクリアする.
                self.set_selected_student_list('')

                # 「削除] ボタンを無効にする.
                self.disable_delete_student_button()

                # 問題集の内容をクリアし, 選択ボタンを無効にする.
                # 「選択」ボタンを無効にする.
                self.WidgetSelectWorkSheetPath.disable_select_button()
                # 「問題集選択」エントリーを空白に設定する.
                self.WidgetSelectWorkSheetPath.set_selected_worksheet_path('')
                ################################################################################
                # 問題集を読み込んで内容クリアする.
                path = self.WidgetSelectWorkSheetPath.get_selected_worksheet_path()
                self.KanjiWorkSheet.load_worksheet(path)
                ################################################################################

                # チェックボタンの値をクリアし, チェックボタンを無効にする.
                self.WidgetProblemRegion.del_grade()

                # 問題数の値をクリアし, 入力欄を無効にする.
                self.WidgetSelectNumberOfProblem.set_number_of_problem('')
                # 出題数のエントリーを無効にする.
                self.WidgetSelectNumberOfProblem.disable_number_of_problem_entry()

                # 「採点完了」ボタンを無効にする.
                self.WidgetScoring.disable_scoring_button()
                # 「プリント作成」ボタンを無効にする.
                self.WidgetCreateWorkSheet.disable_create_button()
                # 「印刷」ボタンを無効にする.
                self.WidgetCreateWorkSheet.disable_print_button()

                # 採点を更新する.
                self.WidgetScoring.update_scoring()
                # レポートを更新する.
                self.WidgetReport.update_report()

    # 「生徒選択」エントリーのメニューを設定する.
    def set_selected_student_list(self, list):
        self.SelectStudentFrame_Combobox['values'] = list
        if len(list) == 0:
            self.SelectStudentFrame_Combobox.set('')

    # 「生徒選択」エントリーのデータを取得する.
    def get_selected_student_name(self):
        return self.SelectStudentFrame_Combobox_Value.get()

    # 「削除」ボタンを有効にする.
    def enable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.NORMAL

    # 「削除」ボタンを無効にする.
    def disable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.DISABLED

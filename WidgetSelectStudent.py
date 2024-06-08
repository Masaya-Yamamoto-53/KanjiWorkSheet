# WidgetSelectStudent.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from Subject import Subject
from DebugPrint import DebugPrint
from UserSettings import UserSettings


class WidgetSelectStudent(Subject):
    # 生徒登録用のウィジェット作成する。
    # Create a widget for student registration.
    def __init__(self, root, row, column):
        Subject.__init__(self)
        # デバッグ表示クラス / Debug display class
        self.DebugPrint = DebugPrint(debug=True)
        # ユーザ設定クラス / User settings class
        self.UserSettings = UserSettings()

        self.KanjiWorkSheet = None
        self.CreateFilePath = None

        # 生徒選択ラベルフレーム / 'Select Student' label frame
        self.SelectStudentFrame = tk.LabelFrame(root, padx=2, pady=2, text='生徒選択')
        self.SelectStudentFrame.grid(row=row, column=column)

        # 生徒選択コンボボックス
        # 'Select Student' combo box
        # 生徒が存在しない場合は""にする。
        # If no students exist, set to "".
        if self.UserSettings.get_setting_num() == 0:
            values = ''
        else:
            # NumPy配列(ndarry)をリストに変換し格納する。
            # Convert NumPy array (ndarray) to list and store.
            values = self.UserSettings.get_student_name_list()

        self.SelectStudentFrame_Combobox_Value = tk.StringVar()
        self.SelectStudentFrame_Combobox = tk.ttk.Combobox(
            self.SelectStudentFrame,
            values=values,
            textvariable=self.SelectStudentFrame_Combobox_Value,
            postcommand=self.Event_UpdateStudent,
            width=27,
            state='readonly'
        )
        self.SelectStudentFrame_Combobox.bind('<<ComboboxSelected>>', self.Event_SelectStudent)
        self.SelectStudentFrame_Combobox.pack(side=tk.LEFT)

        # 生徒削除ボタン
        # 'Delete Student' button
        self.SelectStudentFrame_Button = tk.Button(
            self.SelectStudentFrame,
            text='削除',
            command=self.Event_DeleteStudent,
            state=tk.DISABLED
        )
        self.SelectStudentFrame_Button.pack(side=tk.LEFT)

    def set_class(
            self,
            kanji_worksheet,
            create_file_path
    ):
        self.KanjiWorkSheet = kanji_worksheet
        self.CreateFilePath = create_file_path

    # イベント発生条件:「生徒選択」コンボボックスを押したとき
    # Event trigger condition: When the 'Select Student' combo box is pressed.
    # 処理概要:「生徒選択」コンボボックスのメニューを更新する。
    # Process overview: Update the menu of the 'Select Student' combo box.
    def Event_UpdateStudent(self):
        self.DebugPrint.print_info('Call: Event_UpdateStudent')
        # 生徒の登録がある場合は、設定ファイルから生徒の名前を取得して、
        # If there are registered students, get the student names from the settings file,
        # 「生徒選択」コンボボックスのメニューに設定する。
        # and set them in the 'Select Student' combo box menu.
        if self.UserSettings.get_setting_num() != 0:
            self.set_selected_student_list(self.UserSettings.get_student_name_list())
        # 生徒の登録がない場合は、「生徒選択」コンボボックスのメニューを空欄にする。
        # If there are no registered students, set the 'Select Student' combo box menu to blank.
        else:
            self.set_selected_student_list('')

    # イベント発生条件:「生徒選択」コンボボックスを押し、生徒を選択したとき
    # Event trigger condition: When the 'Select Student' combo box is pressed and a student is selected.
    # 処理概要:選択した生徒の設定に更新する。
    # Process overview: Update to the settings of the selected student.
    def Event_SelectStudent(self, event):
        self.DebugPrint.print_info('Call: Event_SelectStudent')
        # 「生徒選択」コンボボックスで選択した生徒の名前を取得する。
        # Get the name of the student selected in the 'Select Student' combo box.
        name = self.get_selected_student_name()
        # 名前が有効なとき
        # When the name is valid
        if len(name) > 0:
            # 「削除」ボタンを有効にする。
            # # Enable the 'Delete' button.
            self.enable_delete_student_button()

            # オブザーバーに通知する。
            # Notify the observer.
            self.notify(self.kNotify_select_student)

            ################################################################################
            # 登録した問題集のパスを取得し、問題集を読み込む。
            # Get the path of the registered workbook and load the workbook.
            path = self.UserSettings.get_path_of_problem(name)
            (opn_err_num, _, fmt_err_num, fmt_err_msg) = self.KanjiWorkSheet.load_worksheet(path)
            ################################################################################

            # 問題集を正しく読み込めた場合
            # If the workbook is loaded correctly
            if opn_err_num == 0 and fmt_err_num == 0:
                # オブザーバーに通知する。
                # # Notify the observer.
                self.notify(self.KNotify_load_successful)
            else:
                # オブザーバーに通知する。
                # # Notify the observer.
                self.notify(self.kNotify_load_failed)
                # 何らかのエラーメッセージを取得した場合は、メッセージボックスで通知する。
                # If any error message is obtained, notify with a message box.
                # ただし、ファイルが存在しないことをこのイベントでは通知しない.(煩わしいため)
                # However, do not notify about the non-existence of the file in this event (to avoid annoyance).
                for msg in fmt_err_msg:
                    tk.messagebox.showerror('Error', msg)

    # イベント発生条件:「削除」ボタンを押したとき
    # Event trigger condition: When the 'Delete' button is pressed.
    # 処理概要:「生徒選択」コンボボックスに記入している生徒を削除する。
    # Process overview: Delete the student entered in the 'Select Student' combo box.
    def Event_DeleteStudent(self):
        self.DebugPrint.print_info('Call: Event_DeleteStudent')
        # 現在選択している登録者を削除する。
        # Delete the currently selected registrant.
        # コンボボックスから登録者名を取得する。
        # Get the registrant's name from the combo box.
        name = self.get_selected_student_name()
        # 名前が有効なとき
        # When the name is valid
        if len(name) > 0:
            msg = tk.messagebox.askquestion('Warning', '本当に削除しますか.', default='no')
            if msg == 'yes':
                # 漢字プリントのログを削除する。
                # Delete the kanji worksheet log.
                self.KanjiWorkSheet.delete_kanji_worksheet_logfile(self.CreateFilePath.get_path_of_log())

                # 設定ファイルの該当データを削除する。
                # Delete the corresponding data in the settings file.
                self.UserSettings.delete_student(name)

                # 設定ファイルに保存する。
                # Save the settings file.
                self.UserSettings.save_setting_file()

                # 削除後、生徒選択用のコンボボックスをクリアする。
                # After deletion, clear the combo box for selecting students.
                self.set_selected_student_list('')

                # 「削除] ボタンを無効にする。
                # Disable the 'Delete' button.
                self.disable_delete_student_button()

                # オブザーバーに通知する。
                # Notify the observer.
                self.notify(self.kNotify_delete_student)

                ################################################################################
                # 問題集を読み込んで内容クリアする。
                # Load the workbook and clear the contents.
                self.KanjiWorkSheet.load_worksheet('')
                ################################################################################

    # 「生徒選択」エントリーのメニューを設定する。
    # Set the menu for the 'Select Student' entry.
    def set_selected_student_list(self, name_list):
        self.SelectStudentFrame_Combobox['values'] = name_list
        if len(name_list) == 0:
            self.SelectStudentFrame_Combobox.set('')

    # 「生徒選択」エントリーのデータを取得する。
    # Set the menu for the 'Select Student' entry.
    def get_selected_student_name(self):
        return self.SelectStudentFrame_Combobox_Value.get()

    # 「削除」ボタンを有効にする。
    # Enable the 'Delete' button.
    def enable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.NORMAL

    # 「削除」ボタンを無効にする。
    # Disable the 'Delete' button.
    def disable_delete_student_button(self):
        self.SelectStudentFrame_Button['state'] = tk.DISABLED

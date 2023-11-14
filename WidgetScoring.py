# WidgetScoring.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os

from functools import partial
import tkinter as tk


class WidgetScoring:
    # 生徒登録用のウィジェット作成
    def __init__(self, debug_print, user_settings, root, row, column):
        self.DebugPrint = debug_print  # デバッグ表示クラス
        self.UserSettings = user_settings  # ユーザ設定クラス

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

    def set_class(self, kanji_worksheet, wg_select_student, wg_report):
        self.KanjiWorkSheet = kanji_worksheet
        self.WidgetSelectStudent = wg_select_student
        self.WidgetReport = wg_report

    # イベント発生条件:「採点完了」ボタンを押したとき
    # 処理概要:採点結果を問題集に反映する.
    def Event_PushBtnScoreing(self):
        self.DebugPrint.print_info('Call: Event_PushBtnScoreing')
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
                    self.WidgetReport.update_report(diff=1)
                    # 修了メッセージを表示する.
                    tk.messagebox.showinfo('Info', '問題集に結果を反映しました.')

    # イベント発生条件:「採点」のボタンを押したとき
    # 処理概要:ボタンが押されたとき, ボタンを○または, ×に切り替える.
    def Event_ChangeResult(self, key):
        self.set_scoring_answer_button_display_value(key, not self.get_scoring_answer_button_value(key))
        if self.get_scoring_answer_button_value(key) == True:
            self.set_scoring_answer_button_display(key, '○')
        else:
            self.set_scoring_answer_button_display(key, '✕')

    def update_scoring(self):
        """採点を更新する."""
        self.DebugPrint.print_info('Call: update_scoring')
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

    # 「採点完了」ボタンを有効にする.
    def enable_scoring_button(self):
        self.Scoring_EndFrame_Button['state'] = tk.NORMAL

    # 「採点完了」ボタンを無効にする.
    def disable_scoring_button(self):
        self.Scoring_EndFrame_Button['state'] = tk.DISABLED

    # 「回答」のエントリーを有効にする.
    def enable_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key]['state'] = tk.NORMAL

    # 「回答」のエントリーを無効にする.
    def disable_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key]['state'] = tk.DISABLED

    # 「回答」エントリーを消去する.
    def delete_scoring_answer_text(self, key):
        self.ScoringFrame_AnsFrame_Text[key].delete('1.0', 'end')

    # 「回答」エントリーを挿入する.
    def insert_scoring_answer_text(self, key, value):
        self.ScoringFrame_AnsFrame_Text[key].insert('end', value)

    # 「採点」ボタンのデータを設定する.
    def set_scoring_answer_button_display_value(self, key, value):
        self.ScoringFrame_AnsFrame_Value[key] = value
    #  「正解/不正解」入力ボタンを有効にする.
    def enable_scoring_answer_button(self, key):
        self.ScoringFrame_AnsFrame_Button[key]['state'] = tk.NORMAL

    #  「正解/不正解」入力ボタンを無効にする.
    def disable_scoring_answer_button(self, key):
        self.ScoringFrame_AnsFrame_Button[key]['state'] = tk.DISABLED

    # 「採点」ボタンのデータを取得する.
    def get_scoring_answer_button_value(self, key):
        return self.ScoringFrame_AnsFrame_Value[key]

    # 「採点」ボタンの表示を設定する.
    def set_scoring_answer_button_display(self, key, sign):
        self.ScoringFrame_AnsFrame_Button[key]['text'] = sign

    # ログファイルのパスを取得する.
    def get_path_of_log(self):
        name = self.WidgetSelectStudent.get_selected_student_name()

        logdir = './result/'
        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        return logdir + '.' + name + str(self.KanjiWorkSheet.get_mode()) + '.log'

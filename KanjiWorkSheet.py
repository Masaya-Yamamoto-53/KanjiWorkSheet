# KanjiWorkSheet.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import os
import datetime as datetime
import pandas as pd
import numpy as np

from KanjiWorkSheet_draw import KanjiWorkSheet_draw

class KanjiWorkSheet:
    def __init__(self):
        # デバッグ情報を表示する場合はTrue
        self.kDebug = True

        # 問題集/ログの列
        self.kFileColumns = [
                  '学年', '問題文', '答え', '番号', '管理番号', '最終更新日', '結果', '履歴'
        ]

        self.kGrade = self.kFileColumns[0]
        self.kGradeRange = [1, 7]  # 学年の最小値と最大値(上下限のチェックに使用)
        self.kProblem = self.kFileColumns[1]
        self.kAnswer = self.kFileColumns[2]
        self.kNumber = self.kFileColumns[3]
        self.kAdminNumber = self.kFileColumns[4]
        self.kLastUpdate = self.kFileColumns[5]
        self.kResult = self.kFileColumns[6]
        self.kHistory = self.kFileColumns[7]

        # 漢字テストの結果
        self.kNotMk = '-'  # 未出題の印は、本当はNanだが、キーとして登録するため、ハイフンとする.
                           # そのため、問題集から未出題を検索するときは, Nanで検索する必要があるため, 注意すること.
        self.kCrctMk = 'o'
        self.kIncrctMk = 'x'
        self.kDayMk = 'd'
        self.kWeekMk = 'w'
        self.kMonthMk = 'm'

        # レポートの辞書キー
        self.report_key_list = [
                  self.kNotMk
                , self.kCrctMk
                , self.kIncrctMk
                , self.kDayMk
                , self.kWeekMk
                , self.kMonthMk
        ]

        # 問題集
        self.path_of_worksheet = ''      # 問題集のパス
        self.worksheet = pd.DataFrame()  # 問題集のデータを保持するデータフレーム

        # 漢字プリント
        self.kanji_worksheet = pd.DataFrame()  # 漢字プリントのデータを保持するデータフレーム
        self.kanji_worksheet_idx = []          # 漢字プリントに出題する問題集のインデックスのリスト
        self.list_x_idx = []
        self.list_d_idx = []
        self.list_w_idx = []
        self.list_m_idx = []
        self.list_n_idx = []
        self.list_o_idx = []
        self.create_date = ''  # 作成日

        self.student_name = ''       # 出題対象者(生徒名)
        self.grade = []              # 出題範囲指定(学年)

        self.kMDRW = 0
        self.kMDTR = 1
        self.kMDWK = 2
        self.mode = self.kMDTR       # 出題モード
        self.number_of_problem = 20  # 出題数(デフォルト:20)

    def load_worksheet(self, path):
        """
        :parameter path: 問題集のパス
        :type path: string

        漢字プリントの問題集を読み込む.
        """
        self.path_of_worksheet = path
        opn_err_msg = []
        fmt_err_msg = []

        # ファイルが存在する.
        if os.path.exists(self.path_of_worksheet):
            try:
                # 問題集を読み込む.
                self.worksheet = pd.read_csv(self.path_of_worksheet, sep=',', encoding='shift-jis')
                self.print_info('問題集(' + self.path_of_worksheet + ')の読み込みに成功しました.')

            except pd.errors.EmptyDataError:
                fmt_err_msg.append(self.print_error('問題集が空です.'))
                return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

            # ファイル形式をチェックする.
            # 必要な列が順番通りに存在していることを確認する.
            for name, i in zip(self.kFileColumns, range(len(self.kFileColumns))):
                msg = '問題集の ' + str(i + 1) + '列目は[' + str(name) + ']' + '列である必要があります.'
                # 問題集の列数のほうが大きいとき（列が不足していないとき）.
                if i < len(self.worksheet.columns):
                    # 列の名称が不一致
                    if name != self.worksheet.columns[i]:
                        fmt_err_msg.append(self.print_error(msg))
                # 問題集の列数のほうが小さいとき（列が不足しているとき）.
                else:
                    fmt_err_msg.append(self.print_error(msg))

            # ファイル形式に異常がない.
            if len(fmt_err_msg) == 0:
                # [学年]、[問題文]、[答え] 列の欠損値を確認.
                for name in [self.kGrade, self.kProblem, self.kAnswer]:
                    if self.worksheet[name].isna().any():
                        fmt_err_msg.append(self.print_error('[' + name + ']列に空欄があります.'))

                if len(fmt_err_msg) == 0:
                    # [学年] 列に数値以外が入っていないか確認.
                    data = pd.to_numeric(self.worksheet[self.kGrade], errors='coerce')
                    msg = '[' + str(self.kGrade) + ']列には数値を入れてください.'
                    if pd.isna(data).any():
                        fmt_err_msg.append(self.print_error(msg))

                if len(fmt_err_msg) == 0:
                    # [学年] 列に整数以外が入っていないか確認.
                    data = self.worksheet[self.kGrade]
                    msg = '[' + str(self.kGrade) + ']列には数値を入れてください.'
                    if (data != np.floor(data)).any():
                        fmt_err_msg.append(self.print_error(msg))

                if len(fmt_err_msg) == 0:
                    # [学年] 列の範囲外の数値が入っていないか確認.
                    low = len(self.worksheet[self.worksheet[self.kGrade] < self.kGradeRange[0]])
                    high = len(self.worksheet[self.worksheet[self.kGrade] > self.kGradeRange[-1]])
                    if low != 0 or high != 0:
                        msg = '[' + str(self.kGrade) + ']列には' \
                              + str(self.kGradeRange[0]) + 'から' \
                              + str(self.kGradeRange[-1]) + 'の範囲内にしてください.'
                        fmt_err_msg.append(self.print_error(msg))

                if len(fmt_err_msg) == 0:
                    n = len(self.worksheet[self.kProblem])
                    for sentence, ans, num in zip(self.worksheet[self.kProblem], self.worksheet[self.kAnswer], range(n)):
                        r_inflag = False    #  True: ルビの開始記号<を通過したとき
                        # False: ルビの終了記号>を通過したとき
                        r_nest_err = False  #  True: ルビの指定文字が入れ子になっているとき
                        # False: 入れ子になっていないとき
                        r_cnt_err = False   #  True: ルビの文字数が0のとき
                        # False: ルビの文字数が1以上のとき
                        r_err = False       #  True: ルビの何れかが大文字
                        # False: すべてルビが小文字
                        r_word_cnt = 0      # ルビの文字数

                        p_inflag = False    # True: 問題枠の開始記号[を通過したとき
                        # False: 問題枠の終了記号]を通過したとき
                        p_nest_err = False  # True: 問題枠の指定文字が入れ子になっているとき
                        # False: 入れ子にになっていないとき
                        p_cnt_err = False   # True: 問題の文字数が0のとき
                        # False: 問題の文字数が1以上のとき
                        p_word_cnt = 0      # 問題枠の文字数
                        p_frame_cnt = 0     # 問題枠の数

                        for word in list(sentence):
                            ##########################################################
                            # 問題文のルビ<>が入れ子になっていないか、文字が入っているか確認する.
                            ##########################################################
                            if word == u'＜' or word == u'＞':
                                r_err = True
                            if word == u'<':
                                # 入れ子判定: '<'の後に、'>'ではなく、'<'が来たとき
                                if r_inflag == True:
                                    r_nest_err = True
                                r_inflag = True
                            if word == u'>':
                                # 入れ子判定: '<'の前に、'>'が来たとき
                                if r_inflag == False:
                                    r_nest_err = True
                                else:
                                    # 文字数違反
                                    if r_word_cnt == 0:
                                        r_cnt_err = True
                                r_inflag = False
                                r_word_cnt = 0
                            if r_inflag == True and word != u'<':
                                r_word_cnt += 1
                            ##########################################################
                            # 問題文の問題枠が入れ子になっていないか、文字が入っていないか確認する.
                            ##########################################################
                            if word == u'[':
                                # 入れ子判定: '['の後に、']'ではなく、'['が来たとき
                                if p_inflag == True:
                                    p_nest_err = True
                                p_inflag = True
                            if word == u']':
                                # 入れ子判定: '['の前に、']'が来たとき
                                if p_inflag == False:
                                    p_nest_err = True
                                else:
                                    # 文字数違反
                                    if p_word_cnt == 0:
                                        p_cnt_err = True
                                    else:
                                        p_frame_cnt += 1
                                p_inflag = False
                                p_word_cnt = 0
                            if p_inflag == True and word != u'[':
                                p_word_cnt += 1

                        if r_cnt_err:
                            msg = str(num + 1) + '行目の問題文のルビが空欄です.'
                            fmt_err_msg.append(self.print_error(msg))

                        if r_err:
                            msg = str(num + 1) + '行目の問題文のルビの記号が全角です.'
                            fmt_err_msg.append(self.print_error(msg))

                        if r_nest_err and r_err == False:
                            msg = str(num + 1) + '行目の問題文のルビの指定が入れ子になっています.'
                            fmt_err_msg.append(self.print_error(msg))

                        if p_nest_err:
                            msg = str(num + 1) + '行目の問題文の問題枠の指定が入れ子になっています.'
                            fmt_err_msg.append(self.print_error(msg))

                        if p_cnt_err:
                            msg = str(num + 1) + '行目の問題文の問題枠が空欄です.'
                            fmt_err_msg.append(self.print_error(msg))

                            # 答えの文字数と問題枠の数が合わないとき
                        if len(ans) != p_frame_cnt and p_nest_err == False and p_cnt_err == False:
                            msg = str(num + 1) + '行目の問題文の問題枠と答えの文字数が一致しません.'
                            fmt_err_msg.append(self.print_error(msg))

        # ファイルが存在しない.
        else:
            # データを初期化し, エラーメッセージを出力する.
            self.worksheet = pd.DataFrame()
            opn_err_msg.append(self.print_error('問題集が存在しません.'))

        # エラーコードを出しすぎても仕方がないので、制限を5回までとする.
        return len(opn_err_msg[0:5]) != 0, opn_err_msg[0:5] \
             , len(fmt_err_msg[0:5]) != 0, fmt_err_msg[0:5]

    def save_worksheet(self):
        """漢字プリントの問題集を書き込む."""
        wrt_err_msg = []
        # ファイルが存在する.
        if os.path.exists(self.path_of_worksheet):
            try:
                self.worksheet.to_csv(self.path_of_worksheet, index=False, encoding='shift-jis')
                self.print_info('問題集(' + self.path_of_worksheet + ')を更新しました.')
            # 問題集を開くなどして, 書き込みができない.
            except PermissionError:
                msg = '問題集(' + self.path_of_worksheet + ')を閉じてください. 更新できません.'
                wrt_err_msg.append(self.print_error(msg))
        # ファイルが存在しない.
        else:
            wrt_err_msg.append(self.print_error('問題集が存在しません. 更新できませんでした.'))

        return len(wrt_err_msg) != 0, wrt_err_msg

    def set_student_name(self, name):
        """
        :parameter name: 生徒の名前
        :type name: string

        生徒の名前を設定する."""
        self.student_name = name
        self.print_info('生徒の名前を ' + self.student_name + ' に設定しました.')

    def get_student_name(self):
        """生徒の名前を取得する."""
        return self.student_name

    def get_create_date(self):
        """漢字プリントの作成日を取得する."""
        return self.create_date

    def set_create_date(self, date):
        """
        :param date: 作成日
        :type date: datetime.datetime

        漢字プリントの作成日を設定する.
        """
        self.create_date = date

    def set_grade(self, grade_list):
        """
        :param grade_list: 学年（リストで複数選択可能）
        :type grade_list: list

        漢字プリントの出題範囲を設定する.
        """
        self.grade = grade_list
        self.print_info('学年を ' + str(self.grade) + ' に設定しました.')

    def get_grade(self):
        """漢字プリントの出題範囲を取得する."""
        return self.grade

    def set_mode(self, mode):
        """
        :param mode: 出題モード

        出題モードを設定する.
        """
        self.mode = mode
        self.print_info('出題モードを ' + str(self.mode) + ' に設定しました.')

    def get_mode(self):
        """出題モードを取得する."""
        return self.mode

    def set_number_of_problem(self, num):
        """
        :param num: 漢字プリントの問題の出題数
        :type num: int

        漢字プリントの問題の出題数を設定する.

        問題の出題数は最大20問とし, 20問よりも多く問題数を指定した場合は, 20問にする.

        [理由]

        設定したフォントサイズで問題を出題した場合, A4用紙におさまりが良いのが20問だったため.
        """
        # 出題数が0以下の場合は, 0を設定する.
        self.number_of_problem = max(num,  0)
        # 出題数が20以上の場合は, 20を設定する.
        self.number_of_problem = min(self.number_of_problem, 20)
        self.print_info('出題数を ' + str(self.number_of_problem) + ' に設定しました.')

    def get_number_of_problem(self):
        """漢字プリントの問題の出題数を取得する."""
        return self.number_of_problem

    def create_kanji_worksheet_logfile(self, path):
        """
        :param path: 出題記録のパス

        漢字プリントの出題記録を作成する.
        """
        # 新しく作成した問題のリストをログに出力する.
        if len(self.kanji_worksheet_idx) > 0:
            # インデックスは問題集とマージするときに必要になるため、削除しない.
            self.kanji_worksheet.to_csv(path, encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を作成しました.')
            result = True
        else:
            self.print_error('問題を作成していないため、ログを作成できません.')
            result = False

        return result

    # 漢字プリントの出題記録に採点結果を反映する.
    def record_kanji_worksheet_logfile(self, path, result_list):
        """
        :param path: 出題記録のパス
        :param result_list: 採点結果

        漢字プリントの出題記録に採点結果を反映する.
        """
        opn_err_msg = []
        fmt_err_msg = []

        # ファイルが存在する.
        if os.path.exists(path):
            logs = pd.read_csv(path , sep=',' , index_col=0 , encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を読み込みました.')

            # 出題記録と採点結果の数が一致.
            if len(logs[self.kResult]) == len(result_list):
                # 採点結果を反映する.
                logs[self.kResult] = result_list
                # 更新した漢字プリントの出題記録ファイルを書き込む.
                logs.to_csv(path, encoding='shift-jis')
                self.print_info('ログファイル(' + path + ')を書き込みました.')
            else:
                fmt_err_msg.append(self.print_error('ログファイルと採点結果の数が不一致です.'))

        # ファイルが存在しない.
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')が読み込みませんでした.'))

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    # 漢字プリントの出題記録を削除する.
    def delete_kanji_worksheet_logfile(self, path):
        """
        :param path: 出題記録のパス
        :type path: string

        漢字プリントの出題記録を削除する.
        """
        # ファイルが存在する.
        if os.path.exists(path):
            # 漢字プリントの出題記録を削除する.
            os.remove(path)
            self.print_info('ログファイル(' + path + ')を削除しました.')

        # ファイルが存在しない.
        else:
            self.print_error('存在しないログファイル(' + path + ')を削除しようとしました.')

    def create_kanji_worksheet(self):
        """漢字プリントを作成する."""
        err_msg = []
        self.kanji_worksheet = self.worksheet

        # 漢字プリントの問題集に問題が1問も存在しないとき.
        if len(self.kanji_worksheet) <= 0:
            err_msg.append(self.print_error('問題集を選択していません.'))
            return len(err_msg) != 0, err_msg

        # 出題形式に合わせて問題を抽出する.
        # 指定した学年のみ抽出する.
        if len(self.grade) > 0:
            num = len(self.kanji_worksheet)
            self.kanji_worksheet = self.kanji_worksheet[self.kanji_worksheet[self.kGrade].isin(self.grade)]
            self.print_info('学年は ' + str(self.grade) + ' 年')
            self.print_info('問題集の問題数は ' + str(num) + ' から ' + str(len(self.kanji_worksheet)) + ' に変更.')
        else:
            err_msg.append(self.print_error('学年の指定がありません.'))
            return len(err_msg) != 0, err_msg

        # 設定した出題数よりも、問題集の問題数が少ない時、問題集の問題数を出題数とする.
        num_p = self.get_number_of_problem()
        if num_p > 0:
            num_i = len(self.kanji_worksheet)
            self.print_info('設定出題数は ' + str(num_p) + ' です.')
            if num_i < num_p:
                self.set_number_of_problem(num_i)
                self.print_info('出題数は ' + str(num_i) + ' です.')
            else:
                self.set_number_of_problem(num_p)
                self.print_info('出題数は ' + str(num_p) + ' です.')
        else:
            err_msg.append(self.print_error('出題数の指定がありません.'))
            return len(err_msg) != 0, err_msg

        self.print_info('========================================')
        self.print_info('漢字テストを作成します.')
        self.print_info('========================================')

        if   self.mode == self.kMDRW:
            self.create_review_worksheet()
        elif self.mode == self.kMDWK:
            self.create_weakness_worksheet()
        else:
            self.create_train_worksheet()

        return len(err_msg) != 0, err_msg

    def create_review_worksheet(self):
        self.print_info("Review")
        # テスト問題を選定する
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
        self.create_date = pd.to_datetime(datetime.datetime.today())

        num = self.get_number_of_problem()

        # 既に出題し、正解している問題を候補に挙げる.
        list_o = self.kanji_worksheet[pd.notnull(self.kanji_worksheet[self.kResult])]
        list_o = list_o[list_o[self.kResult] == self.kCrctMk]
        # 最終更新日で昇順に並び替える.
        list_o = list_o.sort_values(self.kLastUpdate, ascending=True)[0: 20]
        self.list_o_idx = list_o.index.values
        np.random.shuffle(self.list_o_idx)

        self.kanji_worksheet_idx = self.list_o_idx[0:num]

        # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
        # レアケースのため、出題数を削ることで対応する。
        self.set_number_of_problem(len(self.kanji_worksheet_idx))

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now
        self.kanji_worksheet = self.kanji_worksheet.loc[self.kanji_worksheet_idx, :]

    def create_train_worksheet(self):
        # テスト問題を選定する
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
        self.create_date = pd.to_datetime(datetime.datetime.today())
        now_time = self.create_date + datetime.timedelta(hours=2)

        # 間違えた問題を最優先で選ぶ。
        self.list_x_idx = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == self.kIncrctMk].index.values

        # 昨日間違えた問題を選ぶ
        list_d = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == self.kDayMk]
        delta = now_time - pd.to_datetime(list_d[self.kLastUpdate]) >= datetime.timedelta(days=1)
        self.list_d_idx = list_d[delta].index.values

        # 一週間前に間違えた問題を選ぶ
        list_w = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == self.kWeekMk]
        delta = now_time - pd.to_datetime(list_w[self.kLastUpdate]) >= datetime.timedelta(days=6)
        self.list_w_idx = list_w[delta].index.values

        # 一ヶ月前に間違えた問題を選ぶ
        list_m = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == self.kMonthMk]
        delta = now_time - pd.to_datetime(list_m[self.kLastUpdate]) >= datetime.timedelta(days=21)
        self.list_m_idx = list_m[delta].index.values

        # 4つの問題を合成
        # 優先順位:
        # 次の日に出題 ＞ 一週間後に出題 ＞ 一ヶ月後に出題 ＞ 不正解 ＞ 未出題 ＞ 正解
        self.kanji_worksheet_idx = np.concatenate([self.list_d_idx , self.list_w_idx , self.list_m_idx , self.list_x_idx])

        if self.number_of_problem <= len(self.kanji_worksheet_idx):
            # 間違えた問題で満足した場合
            self.kanji_worksheet_idx = self.kanji_worksheet_idx[0: self.number_of_problem]
        else:
            # 間違えた問題だけでは不足している場合
            # 必要な分をランダムで選択
            num = self.get_number_of_problem() - len(self.kanji_worksheet_idx)

            # まだ出題していないもの
            self.list_n_idx = self.kanji_worksheet[pd.isnull(self.kanji_worksheet[self.kResult])].index.values
            np.random.shuffle(self.list_n_idx)

            # 未出題だけで確保できた.
            if num <= len(self.list_n_idx):
                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_n_idx[0:num]])
            # 未出題だけでは確保できなかった.
            else:
                # 既に出題し、正解している問題を候補に挙げる.
                list_o = self.kanji_worksheet[pd.notnull(self.kanji_worksheet[self.kResult])]
                list_o = list_o[list_o[self.kResult] == self.kCrctMk]
                # 最終更新日で昇順に並び替える.
                list_o = list_o.sort_values(self.kLastUpdate, ascending=True)[0: 20]
                self.list_o_idx = list_o.index.values
                np.random.shuffle(self.list_o_idx)

                num = num - len(self.list_n_idx)
                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_n_idx])
                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_o_idx[0:num]])

                # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
                # レアケースのため、出題数を削ることで対応する。
                self.set_number_of_problem(len(self.kanji_worksheet_idx))

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now
        self.kanji_worksheet = self.kanji_worksheet.loc[self.kanji_worksheet_idx, :]

    def create_weakness_worksheet(self):
        # テスト問題を選定する
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
        self.create_date = pd.to_datetime(datetime.datetime.today())
        num = self.get_number_of_problem()

        # 既に出題し、正解している問題を候補に挙げる.
        list_o = self.kanji_worksheet[pd.notnull(self.kanji_worksheet[self.kResult])]
        list_o = list_o[list_o[self.kResult] == self.kCrctMk]

        # 間違えた問題を最優先で選ぶ。
        hist = list_o[self.kHistory].str[-10:].str.count(self.kIncrctMk)

        self.kanji_worksheet_idx = hist.sort_values(ascending=False).head(num).index

        # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
        # レアケースのため、出題数を削ることで対応する。
        self.set_number_of_problem(len(self.kanji_worksheet_idx))

        # ランダムに並び替える.
        #np.random.shuffle(self.kanji_worksheet_idx)
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now
        self.kanji_worksheet = self.kanji_worksheet.loc[self.kanji_worksheet_idx, :]

    def report_kanji_worksheet(self):
        """漢字プリントの出題問題の概要を表示する."""
        msg_list = [
                  '　　　　　未出題: '
                , '　　　　　　正解: '
                , '　　　　　不正解: '
                , '明日以降に再実施: '
                , '１週間後に再実施: '
                , '１ヶ月後に再実施: '
        ]
        dict = {}

        test = self.kanji_worksheet
        dict[self.kNotMk]    = len(test[pd.isnull(test[self.kResult])])
        dict[self.kCrctMk]   = len(test[test[self.kResult] == self.kCrctMk])
        dict[self.kIncrctMk] = len(test[test[self.kResult] == self.kIncrctMk])
        dict[self.kDayMk]    = len(test[test[self.kResult] == self.kDayMk])
        dict[self.kWeekMk]   = len(test[test[self.kResult] == self.kWeekMk])
        dict[self.kMonthMk]  = len(test[test[self.kResult] == self.kMonthMk])

        self.print_info('========================================')
        self.print_info('出題内容')
        self.print_info('========================================')
        for key, msg in zip(self.report_key_list, msg_list):
            self.print_info(msg + str(dict[key]) + ' 件')

        return self.report_key_list, dict

    def update_kanji_worksheet(self, path):
        """
        :param path: 出題記録のパス

        漢字プリントの出題記録を問題集に反映する.
        """
        opn_err_msg = []
        fmt_err_msg = []

        # ファイルが存在する.
        if os.path.exists(path):
            # 前回のテスト結果を読み込む.
            logs = pd.read_csv(path , sep=',' , index_col=0 , encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を読み込みました.')

            # 前回のテスト結果を基に、問題集を更新する。

            # レポート用の辞書を初期化
            dict = {}
            for key in self.report_key_list:
                dict[key] = 0

            # ログファイルから問題集に対応するインデックスを取得する.
            for p_i, l_i in zip(logs.index, range(len(logs))):
                # ログファイルの入力がある時.
                if not pd.isnull(logs.iloc[l_i, logs.columns.get_loc(self.kResult)]):
                    # 以前の結果
                    p_result_pos = self.worksheet.columns.get_loc(self.kResult)
                    old = self.worksheet.iloc[p_i, p_result_pos]
                    # 今回の結果
                    l_result_pos = logs.columns.get_loc(self.kResult)
                    new = logs.iloc[l_i, l_result_pos]

                    # [結果]列を更新する.
                    # 【凡例】
                    # NaN: self.kNotMk   : 未実施
                    #   o: self.kCrctMk  : 今回正解
                    #   x: self.kIncrctMk: 今回不正解
                    #   d: self.kDayMk   : 1日後に実施(前回xで今回oの時)
                    #   w: self.kWeekMk  : 1週間後に実施(前回dで今回oの時)
                    #   m: self.kMonthMk : 1ヶ月後に実施(前回wで今回oの時)

                    p_lastup_pos = self.worksheet.columns.get_loc(self.kLastUpdate)
                    l_lastup_pos = logs.columns.get_loc(self.kLastUpdate)

                    if new == self.kCrctMk:
                        if   old == self.kIncrctMk:  # x -> d
                            key = self.kDayMk
                        elif old == self.kDayMk:     # d -> w
                            key = self.kWeekMk
                        elif old == self.kWeekMk:    # w -> m
                            key = self.kMonthMk
                        else:                        # m -> o or nan -> o
                            key = self.kCrctMk
                    else:                            # x
                        key = self.kIncrctMk
                    self.worksheet.iloc[p_i, p_lastup_pos] = logs.iloc[l_i, l_lastup_pos]

                    # 結果を反映する.
                    self.worksheet.iloc[p_i, p_result_pos] = key
                    # 各結果の回数をカウントする.
                    dict[key] += 1

                    # 履歴を更新する.
                    hist_pos = self.worksheet.columns.get_loc(self.kHistory)
                    hist = self.worksheet.iloc[p_i, hist_pos]
                    if pd.isna(hist):
                        hist = new
                    else:
                        hist = str(hist) + new
                    self.worksheet.iloc[p_i, hist_pos] = hist

            # 問題集に反映した数の合計を求める.
            sum = 0
            for key in self.report_key_list:
                sum += dict[key]

            if len(logs) != sum:
                fmt_err_msg.append(self.print_error('ログファイルの問題数と登録件数が不一致です. '))
                fmt_err_msg.append(self.print_error('結果の記入に間違いがあるか、未記入である可能性があります.'))
                self.print_info('＊　明日以降に再実施する問題を ' + str(dict[self.kDayMk]) + ' 件 登録しました.')
                self.print_info('＊　１週間後に再実施する問題を ' + str(dict[self.kWeekMk]) + ' 件 登録しました.')
                self.print_info('＊　１ヶ月後に再実施する問題を ' + str(dict[self.kMonthMk]) + ' 件 登録しました.')
                self.print_info('＊　不正解だった問題を ' + str(dict[self.kIncrctMk]) + ' 件 登録しました.')
                self.print_info('＊　正解だった問題を ' + str(dict[self.kCrctMk]) + ' 件 登録しました.')
                self.print_info('　　計 ' + str(sum) + ' 件 登録しました.')
        # ファイルが存在しない.
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')が読み込みませんでした.'))
            opn_err_msg.append(self.print_info('問題集にテスト結果を反映することができませんでした.'))
            opn_err_msg.append(self.print_info('テストの履歴を反映しない状態で問題を作成します.'))

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    def get_kanji_worksheet_with_status(self, path, status):
        """
        :param path: ログファイル
        :type path: string
        :param status: 採点結果
        :type status: string

        漢字プリントから指定したステータスに該当する問題数を取得する.
        """
        opn_err_msg = []
        ans = []
        if os.path.exists(path):
            logs = pd.read_csv(
                    path
                    , sep=','
                    , index_col=0
                    , encoding='shift-jis'
            )
            self.print_info('ログファイル(' + path+ ')を読み込みました.')

            ans = logs[status].values
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')を読み込めませんでした.'))

        return len(opn_err_msg), opn_err_msg, ans

    def get_number_of_problem_with_status(self, grade, status):
        """
        :param grade: 学年
        :type grade: list
        :param status: 採点結果
        :type status: string

        問題集から指定したステータスに該当する問題数を取得する.
        """
        tmp = self.worksheet[self.worksheet[self.kGrade].isin(grade)]
        return len(tmp[tmp[self.kResult] == status])

    def get_number_of_problem_with_grade(self, grade):
        """
        :param grade: 学年
        :type grade: list

        問題集から指定した学年の問題数を取得する.
        """
        return len(self.worksheet[self.worksheet[self.kGrade].isin(grade)])

    def get_number_of_issued_problem(self, grade):
        """
        :param grade: 学年
        :type grade: list

        問題集から指定した学年の出題数を取得する.
        """
        tmp = self.worksheet[self.worksheet[self.kGrade].isin(grade)]
        return len(tmp) - len(tmp[pd.isna(tmp[self.kResult])])

    def print_kanji_worksheet(self, path):
        """
        :param path: 漢字プリントの保存先
        :type path: string

        漢字プリントを作成する.
        """
        draw = KanjiWorkSheet_draw(
                  path
                , self.student_name
                , self.grade
                , self.create_date
                , self.number_of_problem
                , self.kanji_worksheet[self.kProblem]
                , self.kanji_worksheet_idx
        )

        # 漢字プリント作成
        draw.create_kanji_worksheet()

    def print_info(self, msg):
        """
        :param msg: 出力メッセージ
        :type msg: string

        デバッグ情報を標準出力する.
        """
        if self.kDebug:
            print('Info: ' + msg)
        return msg

    def print_error(self, msg):
        """
        :param msg: 出力メッセージ
        :type msg: string

        エラーメッセージを標準出力する.
        """
        if self.kDebug:
            print('\033[31m' + 'Error: ' + msg + '\033[0m')
        return msg

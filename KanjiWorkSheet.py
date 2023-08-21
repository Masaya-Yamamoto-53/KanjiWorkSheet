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


# 文字が漢字であるか否かを評価する.
def is_kanji(char):
    return '\u4e00' <= char <= '\u9faf'


class KanjiWorkSheet:
    def __init__(self):
        # デバッグ情報を表示する場合はTrue
        self.kDebug = True

        # 問題集/ログの列
        self.kFileColumns = [
              '学年'
            , '問題文'
            , '答え'
            , '番号'
            , '管理番号'
            , '最終更新日'
            , '結果'
            , '履歴'
        ]

        self.kGrade = self.kFileColumns[0]
        self.kGradeRange = [1, 6]  # 学年の最小値と最大値(上下限のチェックに使用)
        self.kProblem = self.kFileColumns[1]
        self.kAnswer = self.kFileColumns[2]
        self.kNumber = self.kFileColumns[3]
        self.kAdminNumber = self.kFileColumns[4]
        self.kLastUpdate = self.kFileColumns[5]
        self.kResult = self.kFileColumns[6]
        self.kHistory = self.kFileColumns[7]

        # 漢字テストの結果
        self.kNotMk = '-'
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

        self.student_name = ''  # 出題対象者(生徒名)
        self.grade = []         # 出題範囲指定(学年)

        self.kMDRW = 0  # 復習モード
        self.kMDTR = 1  # 練習モード
        self.kMDWK = 2  # 苦手モード
        self.mode = self.kMDTR  # 出題モード
        self.number_of_problem = 20  # 出題数(デフォルト:20)

        # 漢字マスタの読み込み.
        self.kanji_by_grade_list = [[] for _ in range(self.kGradeRange[1] + 1)]
        self.answer_kanji_keyword = []

    # 問題集から学年に対応する漢字をリスト化する.
    def create_list_kanji_by_grade(self):
        """問題集から学年に対応する漢字をリスト化する."""
        # このリストは不必要なルビを削除するための判断材料として使用する.
        grade_old = []  # 今までの漢字を格納するリスト
        for grade in range(self.kGradeRange[0], self.kGradeRange[1] + 1):
            # 学年に該当するデータを抽出する.
            worksheet = self.get_problem_with_grade(self.grade)
            # 抽出したデータが存在する場合
            if len(worksheet) > 0:
                # 1語ずつ配列に格納する
                for ans in worksheet[self.kAnswer]:
                    self.kanji_by_grade_list[grade].append([char for char in ans])

                # 多次元を1次元に変換
                self.kanji_by_grade_list[grade] = [item for sublist in self.kanji_by_grade_list[grade] for item in sublist]
                # ソートして、ユニークにする.
                self.kanji_by_grade_list[grade] = sorted(self.kanji_by_grade_list[grade])
                self.kanji_by_grade_list[grade] = list(set(self.kanji_by_grade_list[grade]))
                # 前の学年の漢字のみ取り除く.
                self.kanji_by_grade_list[grade] = list(set(self.kanji_by_grade_list[grade]) - set(grade_old))

                # 現在の学年の漢字だけを残すため、それ以降の漢字を記憶しておく.
                grade_old = grade_old + self.kanji_by_grade_list[grade]

                # 学年毎に習う漢字数を表示する.
                self.print_info('小学' + str(grade) + '年生: 全 ' + str(len(self.kanji_by_grade_list[grade])) + ' 文字')

    # ファイル形式をチェックする.
    def check_file_format(self, fmt_err_msg=None):
        """
        :param fmt_err_msg: エラーメッセージ
        :type fmt_err_msg: string

        ファイル形式をチェックする.
        """
        if fmt_err_msg is None:
            fmt_err_msg = []
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

        return fmt_err_msg

    # 欠損値をチェックする.
    def check_column_nan(self, fmt_err_msg=None):
        """
        :param fmt_err_msg: エラーメッセージ
        :type fmt_err_msg: string

        欠損値をチェックする.
        """
        chk_list = [self.kGrade, self.kProblem, self.kAnswer, self.kNumber, self.kAdminNumber]
        # '学年', '問題文', '答え', '番号', '管理番号' 列の欠損値を確認.
        if fmt_err_msg is None:
            fmt_err_msg = []
        for col in chk_list:
            if self.worksheet[col].isna().any():
                fmt_err_msg.append(self.print_error('[' + col + ']列に空欄があります.'))

        return fmt_err_msg

    # 数値以外をチェックする.
    def check_column_non_numeric(self, fmt_err_msg=None):
        """
        :param fmt_err_msg: エラーメッセージ
        :type fmt_err_msg: string

        数値以外をチェックする.
        """
        # '学年', '番号' 列に数値以外が入っていないか確認.
        chk_list = [self.kGrade, self.kNumber]
        if fmt_err_msg is None:
            fmt_err_msg = []
        for col in chk_list:
            # 数値に変換し、変換に失敗した場合に欠損値にすることで、数値が入っているかを確認する.
            data = pd.to_numeric(self.worksheet[col], errors='coerce')
            msg = '[' + str(col) + ']列には数値を入れてください.'
            if pd.isna(data).any():
                fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 整数以外をチェックする.
    def check_column_non_integer(self, fmt_err_msg=None):
        """整数以外をチェックする."""
        # '学年', '番号' 列に整数以外が入っていないか確認.
        chk_list = [self.kGrade, self.kNumber]
        if fmt_err_msg is None:
            fmt_err_msg = []
        for col in chk_list:
            data = self.worksheet[col]
            msg = '[' + str(col) + ']列には数値を入れてください.'
            if any(np.floor(data) != data):
                fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 範囲外の数値をチェックする.
    def check_column_out_of_range(self, fmt_err_msg):
        """範囲外の数値をチェックする."""
        # [学年] 列の範囲外の数値が入っていないか確認.
        low = len(self.worksheet[self.worksheet[self.kGrade] < self.kGradeRange[0]])
        high = len(self.worksheet[self.worksheet[self.kGrade] > self.kGradeRange[-1]])
        if low != 0 or high != 0:
            msg = '[' + str(self.kGrade) + ']列には' \
                  + str(self.kGradeRange[0]) + 'から' \
                  + str(self.kGradeRange[-1]) + 'の範囲内にしてください.'
            fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 未定義の文字をNotMkに置き換える.
    def replace_undef_char_with_NotMk(self):
        """未定義の文字をNotMkに置き換える."""
        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        worksheet = self.worksheet
        for key in self.report_key_list:
            worksheet = worksheet[worksheet[self.kResult] != key]

        idx = worksheet.index.values
        if len(idx) > 0:
            self.worksheet.loc[idx, self.kResult] = self.kNotMk
            self.save_worksheet()

    # 履歴がNanの場合は、''に置き換える。
    def replace_nan_char_with_space(self):
        # 履歴がNanの場合は、''に置き換える。
        worksheet = self.worksheet[pd.isna(self.worksheet[self.kHistory])]
        pd_idx = worksheet.index.values
        if len(pd_idx) > 0:
            self.worksheet.loc[pd_idx, self.kHistory] = self.worksheet.loc[pd_idx, self.kHistory].fillna('')
            self.save_worksheet()

    def check_kanji_ruby(self, fmt_err_msg):
        flg = False
        i = 0
        for statement in self.worksheet[self.kProblem]:
            for word in statement:
                if is_kanji(word):
                    flg = True
                elif flg:
                    if word != '<':
                        msg = str(i + 1) + '行目の問題文にルビがありません.'
                        fmt_err_msg.append(self.print_error(msg))
                    flg = False
                else:
                    flg = False

            i += 1

        return fmt_err_msg

    # 問題文の構文をチェックする.
    def check_column_syntax(self, fmt_err_msg):
        n = len(self.worksheet[self.kProblem])
        for sentence, ans, num in zip(self.worksheet[self.kProblem], self.worksheet[self.kAnswer], range(n)):
            r_inflag = False  # True: ルビの開始記号<を通過したとき
            # False: ルビの終了記号>を通過したとき
            r_nest_err = False  # True: ルビの指定文字が入れ子になっているとき
            # False: 入れ子になっていないとき
            r_cnt_err = False  # True: ルビの文字数が0のとき
            # False: ルビの文字数が1以上のとき
            r_err = False  # True: ルビの何れかが大文字
            # False: すべてルビが小文字
            r_word_cnt = 0  # ルビの文字数

            p_inflag = False  # True: 問題枠の開始記号[を通過したとき
            # False: 問題枠の終了記号]を通過したとき
            p_nest_err = False  # True: 問題枠の指定文字が入れ子になっているとき
            # False: 入れ子にになっていないとき
            p_cnt_err = False  # True: 問題の文字数が0のとき
            # False: 問題の文字数が1以上のとき
            p_word_cnt = 0  # 問題枠の文字数
            p_frame_cnt = 0  # 問題枠の数

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
                            p_cnt_err = False  # 文字数違反は無効
                            p_frame_cnt += 1   # 文字数違反は無効
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

        return fmt_err_msg

    # 漢字プリントの問題集を読み込む.
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

            except pd.errors.EmptyDataError:  # ファイルが空だった場合
                fmt_err_msg.append(self.print_error('問題集が空です.'))

            if len(fmt_err_msg) == 0:
                # ファイル形式をチェックする.
                fmt_err_msg = self.check_file_format(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # 欠損値をチェックする.
                fmt_err_msg = self.check_column_nan(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # [学年] 列に数値以外が入っていないか確認.
                fmt_err_msg = self.check_column_non_numeric(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # [学年] 列に整数以外が入っていないか確認.
                fmt_err_msg = self.check_column_non_integer(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # [学年] 列の範囲外の数値が入っていないか確認.
                fmt_err_msg = self.check_column_out_of_range(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # [問題文]の構文にエラーがないか確認.
                fmt_err_msg = self.check_column_syntax(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # 漢字にルビが降られていることをチェックする.
                fmt_err_msg = self.check_kanji_ruby(fmt_err_msg)

        # ファイルが存在しない.
        else:
            # データを初期化し, エラーメッセージを出力する.
            self.worksheet = pd.DataFrame()
            opn_err_msg.append(self.print_error('問題集が存在しません.'))

        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        self.replace_undef_char_with_NotMk()

        # 履歴がNanの場合は、''に置き換える。
        self.replace_nan_char_with_space()

        # 学年毎の漢字を確認する.
        self.create_list_kanji_by_grade()

        # エラーコードを出しすぎても仕方がないので、制限を5回までとする.
        return len(opn_err_msg[0:5]) != 0, opn_err_msg[0:5] \
            , len(fmt_err_msg[0:5]) != 0, fmt_err_msg[0:5]

    # 漢字プリントの問題集を書き込む.
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

    # 生徒の名前を設定する.
    def set_student_name(self, name):
        """
        :parameter name: 生徒の名前
        :type name: string

        生徒の名前を設定する."""
        self.student_name = name
        self.print_info('生徒の名前を ' + self.student_name + ' に設定しました.')

    # 生徒の名前を取得する.
    def get_student_name(self):
        """生徒の名前を取得する."""
        return self.student_name

    # 漢字プリントの作成日を設定する.
    def set_create_date(self, date):
        """
        :param date: 作成日
        :type date: datetime.datetime

        漢字プリントの作成日を設定する.
        """
        self.create_date = date

    # 漢字プリントの作成日を取得する.
    def get_create_date(self):
        """漢字プリントの作成日を取得する."""
        return self.create_date

    # 漢字プリントの出題範囲を設定する.
    def set_grade(self, grade_list):
        """
        :param grade_list: 学年（リストで複数選択可能）
        :type grade_list: list

        漢字プリントの出題範囲を設定する.
        """
        self.grade = grade_list
        self.print_info('学年を ' + str(self.grade) + ' に設定しました.')

    # 漢字プリントの出題範囲を取得する.
    def get_grade(self):
        """漢字プリントの出題範囲を取得する."""
        return self.grade

    # 出題モードを設定する.
    def set_mode(self, mode):
        """
        :param mode: 出題モード

        出題モードを設定する.
        """
        self.mode = mode
        self.print_info('出題モードを ' + str(self.mode) + ' に設定しました.')

    # 出題モードを取得する.
    def get_mode(self):
        """出題モードを取得する."""
        return self.mode

    # 漢字プリントの問題の出題数を設定する.
    def set_number_of_problem(self, num):
        """
        :param num: 漢字プリントの問題の出題数
        :type num: int

        漢字プリントの問題の出題数を設定する.

        問題の出題数は最大20問とし, 20問よりも多く問題数を指定した場合は, 20問にする.

        [理由]

        設定したフォントサイズで問題を出題した場合, A4用紙におさまりが良いのが20問だったため.
        """
        num = max(num, 0)  # 出題数が0以下の場合は, 0を設定する.
        num = min(num, 20)  # 出題数が20以上の場合は, 20を設定する.
        self.number_of_problem = num
        self.print_info('出題数を ' + str(self.number_of_problem) + ' に設定しました.')

    # 漢字プリントの問題の出題数を取得する.
    def get_number_of_problem(self):
        """漢字プリントの問題の出題数を取得する."""
        return self.number_of_problem

    # 漢字プリントの出題記録を作成する.
    def create_kanji_worksheet_logfile(self, path):
        """
        :param path: 出題記録のパス

        漢字プリントの出題記録を作成する.
        """
        # 新しく作成した問題のリストをログに出力する.
        if len(self.kanji_worksheet) > 0:
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
            logs = pd.read_csv(path, sep=',', index_col=0, encoding='shift-jis')
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

    def get_answer_kanji_keyword(self):
        target_kanji_problem_list = []
        target_kanji_answer = self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kAnswer].values
        # 1語ずつ配列に格納する
        target_kanji_answer = target_kanji_answer.tolist()
        for ans in target_kanji_answer:
            target_kanji_problem_list.append([char for char in ans])

        # 多次元を1次元に変換
        target_kanji_problem_list = [item for sublist in target_kanji_problem_list for item in sublist]
        target_kanji_problem_list = sorted(target_kanji_problem_list)
        target_kanji_problem_list = list(set(target_kanji_problem_list))

        self.answer_kanji_keyword = target_kanji_problem_list

    def replace_kanji_with_ruby(self):
        kanji_cnt = 0
        flg = False
        self.print_info('問題文中に答えが存在するため、ひらがなに置き換えました.')
        problem_statement_list = ['' for _ in range(self.get_number_of_problem())]
        for statement, idx, i in zip(self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kProblem]
                                   , self.kanji_worksheet_idx
                                   , range(self.get_number_of_problem())):
            for word in statement:
                if is_kanji(word):
                    # 問題文の漢字が答えで使っている場合
                    if word in self.answer_kanji_keyword:
                        flg = True
                    problem_statement_list[i] = problem_statement_list[i] + word
                    kanji_cnt += 1
                elif word == '<':
                    if flg:
                        problem_statement_list[i] = problem_statement_list[i][:-1 * kanji_cnt]
                    else:
                        problem_statement_list[i] = problem_statement_list[i] + word
                    kanji_cnt = 0
                elif word == '>':
                    if flg:
                        flg = False
                    else:
                        problem_statement_list[i] = problem_statement_list[i] + word
                else:
                    problem_statement_list[i] = problem_statement_list[i] + word

            if statement != problem_statement_list[i]:
                self.print_info('Before: ' + statement)
                self.print_info('After : ' + problem_statement_list[i])
                self.kanji_worksheet.loc[idx, self.kProblem] = problem_statement_list[i]

    # 不要なルビを問題文から削除する.
    def delete_ruby(self):
        del_flg = False
        ruby_flg = False
        self.print_info('問題文中に不要なルビがあるため、削除しました.')
        problem_statement_list = ['' for _ in range(self.get_number_of_problem())]
        for statement, idx, i in zip(self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kProblem]
                , self.kanji_worksheet_idx
                , range(self.get_number_of_problem())):
            for word in statement:
                if is_kanji(word):
                    # 選択した学年の最高位は除く。
                    del_flg = False
                    for grade in range(1, max(self.get_grade())):
                        if word in self.kanji_by_grade_list[grade]:
                            del_flg = True
                    problem_statement_list[i] = problem_statement_list[i] + word
                else:
                    if word == '<':
                        ruby_flg = True
                        problem_statement_list[i] = problem_statement_list[i] + word
                    elif word == '>':
                        ruby_flg = False
                        del_flg = False
                        problem_statement_list[i] = problem_statement_list[i] + word
                    elif ruby_flg:
                        if not del_flg:
                            problem_statement_list[i] = problem_statement_list[i] + word
                        else:
                            problem_statement_list[i] = problem_statement_list[i] + ' '
                    else:
                        problem_statement_list[i] = problem_statement_list[i] + word

            if statement != problem_statement_list[i]:
                self.print_info('Before: ' + statement)
                self.print_info('After : ' + problem_statement_list[i])
                self.kanji_worksheet.loc[idx, self.kProblem] = problem_statement_list[i]

    # 条件に該当する問題のインデックスを返す.
    def get_kanji_worksheet_index(self, result, sort=False, days=-1):
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
        now_time = self.create_date + datetime.timedelta(hours=2)

        tmp_list = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == result]

        # 最終更新日の昇順で更新する指定がある場合は、ソートを行う.
        if sort:
            tmp_list = tmp_list.sort_values(self.kLastUpdate, ascending=True)

        # 期間の指定がある場合は、その期間に該当する問題文のみ抽出する.
        if days != -1:
            delta = datetime.timedelta(days=days) < (now_time - pd.to_datetime(tmp_list[self.kLastUpdate]))
            tmp_list = tmp_list[delta]

        return tmp_list.index.values

    # 選出した問題の最終更新日を更新する.
    def set_lastupdate_kanji_worksheet(self):
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        self.kanji_worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now
        self.kanji_worksheet = self.kanji_worksheet.loc[self.kanji_worksheet_idx, :]

        return self.kanji_worksheet

    # 漢字プリントを作成する.
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
            self.kanji_worksheet = self.get_problem_with_grade(self.grade)

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

        # 作成日を更新する.
        self.create_date = pd.to_datetime(datetime.datetime.today())

        # モードの設定にあった問題を選択する.
        if   self.mode == self.kMDRW:  # 復習モード
            self.create_review_mode_kanji_worksheet()
        elif self.mode == self.kMDWK:  # 苦手モード
            self.create_weakness_mode_kanji_worksheet()
        else:  # 練習モード
            self.create_train_mode_kanji_worksheet()

        # 問題の答えに含まれている漢字を取得する.
        self.get_answer_kanji_keyword()
        # 問題文に答えが記載されている場合は、その漢字をルビに置き換える.
        self.replace_kanji_with_ruby()
        # 選択中の学年未満のルビを削除する.
        self.delete_ruby()

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # 出題する問題が決まったため、最終更新日を更新する.
        self.kanji_worksheet = self.set_lastupdate_kanji_worksheet()

        return len(err_msg) != 0, err_msg

    # 復習モードの漢字プリントを作成する.
    def create_review_mode_kanji_worksheet(self):
        """復習モードの漢字プリントを作成する."""
        self.print_info("Review Mode")

        # 最終更新日で昇順にソートしたもの100件を候補にする.
        # num件にすると、答えが同じ問題をピックアップする懸念があるため。
        self.kanji_worksheet_idx = self.get_kanji_worksheet_index(self.kCrctMk, sort=True)[0:100]
        # 最大100件をソートして0~num件を出題する.
        np.random.shuffle(self.kanji_worksheet_idx)
        self.kanji_worksheet_idx = self.kanji_worksheet_idx[0:self.get_number_of_problem()]

        # 指定数だけ問題を得られない場合もあるため、それを考慮して出題数を再設定する.
        self.set_number_of_problem(len(self.kanji_worksheet_idx))

    # 訓練モードの漢字プリントを作成する.
    def create_train_mode_kanji_worksheet(self):
        """訓練モードの漢字プリントを作成する."""
        self.print_info("Train Mode")

        # テスト問題を選定する
        # 間違えた問題のインデックスを取得する.
        self.list_x_idx = self.get_kanji_worksheet_index(self.kIncrctMk, days=0)
        # 昨日間違えた問題のインデックスを取得する.
        self.list_d_idx = self.get_kanji_worksheet_index(self.kDayMk, days=1)
        # 一週間前に間違えた問題のインデックスを取得する.
        self.list_w_idx = self.get_kanji_worksheet_index(self.kWeekMk, days=7 - 1)
        # 一ヶ月前に間違えた問題のインデックスを取得する.
        self.list_m_idx = self.get_kanji_worksheet_index(self.kMonthMk, days=7 * 4 - 7)

        # まだ出題していない問題を抽出する.
        self.list_n_idx = self.get_kanji_worksheet_index(self.kNotMk)
        np.random.shuffle(self.list_n_idx)
        # 既に出題し、正解している問題を候補に挙げる.
        self.list_o_idx = self.get_kanji_worksheet_index(self.kCrctMk, sort=True)

        # 4つの問題を連結する.
        # 優先順位: 不正解 ＞ 次の日に出題 ＞ 一週間後に出題 ＞ 一ヶ月後に出題 ＞ 未出題 ＞ 正解
        self.kanji_worksheet_idx = np.concatenate([self.list_x_idx, self.list_d_idx, self.list_w_idx, self.list_m_idx])

        num = self.get_number_of_problem() - len(self.kanji_worksheet_idx)
        if num <= 0:
            # 間違えた問題で満足した場合
            # 1~20番目の問題のインデックスを作成する.
            self.kanji_worksheet_idx = self.kanji_worksheet_idx[0: self.get_number_of_problem()]
        else:
            # 間違えた問題だけでは不足している場合
            # 残り必要な問題数を計算する.
            self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_n_idx[0:num]])

            # 未出題だけでは確保できなかった.
            num = num - len(self.list_n_idx)
            if num > 0:
                list_o = self.list_o_idx[0:100]
                np.random.shuffle(list_o)
                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, list_o[0:num]])

                # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
                # レアケースのため、出題数を削ることで対応する。
                self.set_number_of_problem(len(self.kanji_worksheet_idx))

    # 苦手モードの漢字プリントを作成する.
    def create_weakness_mode_kanji_worksheet(self):
        """苦手モードの漢字プリントを作成する."""
        self.print_info("Weakness Mode")

        # テスト問題を選定する
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
        num = self.get_number_of_problem()

        # 既に出題し、正解している問題を候補に挙げる.
        list_o = self.get_kanji_worksheet_index(self.kCrctMk, sort=True)

        # 間違えた問題を最優先で選ぶ。
        hist = list_o[self.kHistory].str[-10:].str.count(self.kIncrctMk)

        self.kanji_worksheet_idx = hist.sort_values(ascending=False).head(num).index

        # 指定数だけ問題を得られない場合もあるため、それを考慮して出題数を再設定する.
        self.set_number_of_problem(len(self.kanji_worksheet_idx))

    # 漢字プリントの出題問題の概要を表示する.
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

        self.print_info('========================================')
        self.print_info('出題内容')
        self.print_info('========================================')
        for key, msg in zip(self.report_key_list, msg_list):
            self.print_info(msg + str(len(self.kanji_worksheet[self.kanji_worksheet[self.kResult] == key])) + ' 件')

        return self.report_key_list

    # 漢字プリントの出題記録を問題集に反映する.
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
            logs = pd.read_csv(path, sep=',', index_col=0, encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を読み込みました.')
        # ファイルが存在しない.
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')が読み込みませんでした.'))
            opn_err_msg.append(self.print_info('問題集にテスト結果を反映することができませんでした.'))
            opn_err_msg.append(self.print_info('テストの履歴を反映しない状態で問題を作成します.'))
            return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

        # 前回のテスト結果を基に、問題集を更新する。
        # レポート用の辞書を初期化
        result_dict = {key: 0 for key in self.report_key_list}

        # ログファイルから問題集に対応するインデックスを取得する.
        for idx in logs.index:
            # ログファイルの入力がある時.
            if not pd.isnull(logs.loc[idx, self.kResult]):
                old = self.worksheet.loc[idx, self.kResult]  # 以前の結果
                new = logs.loc[idx, self.kResult]  # 今回の結果

                # 整合を確認
                # '答え', '番号', '管理番号'を比較
                if  (self.worksheet.loc[idx, self.kAnswer] == logs.loc[idx, self.kAnswer]) \
                and (self.worksheet.loc[idx, self.kNumber] == logs.loc[idx, self.kNumber]) \
                and (self.worksheet.loc[idx, self.kAdminNumber] == logs.loc[idx, self.kAdminNumber]):

                    # [結果]列を更新する.
                    # 【凡例】
                    # NaN: self.kNotMk   : 未実施
                    #   o: self.kCrctMk  : 今回正解
                    #   x: self.kIncrctMk: 今回不正解
                    #   d: self.kDayMk   : 1日後に実施(前回xで今回oの時)
                    #   w: self.kWeekMk  : 1週間後に実施(前回dで今回oの時)
                    #   m: self.kMonthMk : 1ヶ月後に実施(前回wで今回oの時)

                    # 今回, 正解した場合.
                    if new == self.kCrctMk:
                        if   old == self.kIncrctMk:  # x -> d
                            key = self.kDayMk
                        elif old == self.kDayMk:   # d -> w
                            key = self.kWeekMk
                        elif old == self.kWeekMk:  # w -> m
                            key = self.kMonthMk
                        else:                      # m -> o or - -> o
                            key = self.kCrctMk
                    # 今回, 不正解の場合
                    else:                          # x
                        key = self.kIncrctMk

                    # 最終更新日を更新
                    self.worksheet.loc[idx, self.kLastUpdate] = logs.loc[idx, self.kLastUpdate]
                    # 結果を反映する.
                    self.worksheet.loc[idx, self.kResult] = key
                    # 履歴を更新する.
                    self.worksheet.loc[idx, self.kHistory] = self.worksheet.loc[idx, self.kHistory] + new
                    # 各結果の回数をカウントする.
                    result_dict[key] += 1
                else:
                    fmt_err_msg.append(self.print_error('ログファイルと問題集のインデックスが不一致です.'))

        total = sum(result_dict[key] for key in self.report_key_list)

        if len(logs) != total:
            fmt_err_msg.append(self.print_error('ログファイルの問題数と登録件数が不一致です. '))
            fmt_err_msg.append(self.print_error('結果の記入に間違いがあるか、未記入である可能性があります.'))

        self.print_info('＊　明日以降に再実施する問題を ' + str(result_dict[self.kDayMk]) + ' 件 登録しました.')
        self.print_info('＊　１週間後に再実施する問題を ' + str(result_dict[self.kWeekMk]) + ' 件 登録しました.')
        self.print_info('＊　１ヶ月後に再実施する問題を ' + str(result_dict[self.kMonthMk]) + ' 件 登録しました.')
        self.print_info('＊　不正解だった問題を ' + str(result_dict[self.kIncrctMk]) + ' 件 登録しました.')
        self.print_info('＊　正解だった問題を ' + str(result_dict[self.kCrctMk]) + ' 件 登録しました.')
        self.print_info('　　計 ' + str(sum) + ' 件 登録しました.')

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    # 漢字プリントを作成する.
    def generate_pdf_kanji_worksheet(self, path):
        """
        :param path: 漢字プリントの保存先
        :type path: string

        漢字プリントを作成する.
        """
        # 漢字プリントを作成する.
        draw = KanjiWorkSheet_draw(
              path
            , self.get_student_name()
            , self.get_grade()
            , self.get_create_date()
            , self.get_number_of_problem()
            , self.kanji_worksheet[self.kProblem]
            , self.kanji_worksheet_idx)

        # PDFを作成する.
        draw.generate_pdf_kanji_worksheet()

    # ログファイルから指定したステータスに該当するリストを取得する.
    def get_kanji_worksheet_with_status(self, path, status):
        """
        :param path: ログファイル
        :type path: string
        :param status: 採点結果
        :type status: string

        ログファイルから指定したステータスに該当するリストを取得する.
        """
        opn_err_msg = []
        status_list = []
        if os.path.exists(path):
            logs = pd.read_csv(
                path
                , sep=','
                , index_col=0
                , encoding='shift-jis'
            )
            self.print_info('ログファイル(' + path + ')を読み込みました.')

            status_list = logs[status].values
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')を読み込めませんでした.'))

        return len(opn_err_msg), opn_err_msg, status_list

    # 問題集から指定したステータスに該当する問題を取得する.
    def get_problem_with_status(self, grade, status):
        """
        :param grade: 学年
        :type grade: list
        :param status: 採点結果
        :type status: string

        問題集から指定したステータスに該当する問題を取得する.
        """
        tmp = self.get_problem_with_grade(grade)
        return tmp[tmp[self.kResult] == status]

    # 問題集から指定した学年の問題を取得する.
    def get_problem_with_grade(self, grade):
        """
        :param grade: 学年
        :type grade: list

        問題集から指定した学年の問題を取得する.
        """
        return self.worksheet[self.worksheet[self.kGrade].isin(grade)]

    # デバッグ情報を標準出力する.
    def print_info(self, msg):
        """
        :param msg: 出力メッセージ
        :type msg: string

        デバッグ情報を標準出力する.
        """
        if self.kDebug:
            print('Info: ' + msg)
        return msg

    # エラーメッセージを標準出力する.
    def print_error(self, msg):
        """
        :param msg: 出力メッセージ
        :type msg: string

        エラーメッセージを標準出力する.
        """
        if self.kDebug:
            print('\033[31m' + 'Error: ' + msg + '\033[0m')
        return msg

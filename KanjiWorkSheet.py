# KanjiWorkSheet.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import os
import pandas as pd
from DebugPrint import DebugPrint


class KanjiWorkSheet:
    def __init__(self, debug=False):
        # デバッグ情報を表示する場合はTrue
        # Set to True if you want to display debug information
        self.DebugPrint = DebugPrint(debug=debug)

        # 学年の最小値と最大値(上下限のチェックに使用)
        # Minimum and maximum grade levels (used for bounds checking)
        self.kGradeRange = [1, 6]

        # 問題集/ログの列
        # Columns in the problem set/log
        self.kGrade = '学年'
        self.kProblem = '問題文'
        self.kAnswer = '答え'
        self.kNumber = '番号'
        self.kAdminNumber = '管理番号'
        self.kLastUpdate = '最終更新日'
        self.kResult = '結果'
        self.kHistory = '履歴'

        # 問題集/ログの辞書のキー
        # Dictionary keys for the problem set/log
        self.kFileColumns = [
            self.kGrade,
            self.kProblem,
            self.kAnswer,
            self.kNumber,
            self.kAdminNumber,
            self.kLastUpdate,
            self.kResult,
            self.kHistory
        ]

        # 漢字テストの結果
        # Results of kanji tests
        self.kNotMk = '-'
        self.kCrctMk = 'o'
        self.kIncrctMk = 'x'
        self.kDayMk = 'd'
        self.kWeekMk = 'w'
        self.kMonthMk = 'm'

        # 漢字テストの辞書のキー
        # Dictionary keys for kanji tests
        self.report_key_list = [
            self.kNotMk,     # 未出題
            self.kCrctMk,    # 正解
            self.kIncrctMk,  # 不正解
            self.kDayMk,     # 一日後
            self.kWeekMk,    # 一週間後
            self.kMonthMk,   # 一ヶ月後
        ]

        # 問題集のパス
        # Path to the problem set
        self.path_of_worksheet = ''
        # 問題集のデータを保持するデータフレーム
        # Data frame to hold the problem set data
        self.worksheet = pd.DataFrame()
        # 学年毎の漢字リスト
        # Kanji lists by grade level
        self.kanji_by_grade_list = [[] for _ in range(self.kGradeRange[1] + 1)]

    # 漢字の問題集を読み込む。
    # Load the kanji worksheet.
    def load_worksheet(self, path):
        """
        :parameter path: 問題集のパス / Path to the problem set
        :type path: string

        漢字の問題集を読み込む。
        Load the kanji worksheet.
        """
        self.path_of_worksheet = path
        opn_err_msg = []
        fmt_err_msg = []

        # ファイルが存在する。
        # If the file exists.
        if os.path.exists(self.path_of_worksheet):
            try:
                # 問題集を読み込む。
                # Read the problem set.
                self.worksheet = pd.read_csv(self.path_of_worksheet, sep=',', encoding='shift-jis')
                self.print_info('問題集(' + self.path_of_worksheet + ')の読み込みに成功しました。')
            # ファイルが空だった場合
            # If the file is empty.
            except pd.errors.EmptyDataError:
                fmt_err_msg.append(self.print_error('問題集が空です。'))

            # 問題集の内容をチェックする。
            # Check the content of the problem set.
            fmt_err_msg = self.__check_worksheet()

        # ファイルが存在しない。
        # If the file does not exist.
        else:
            # データを初期化し、エラーメッセージを出力する。
            # Initialize data and output an error message.
            self.worksheet = pd.DataFrame()
            opn_err_msg.append(self.print_error('問題集が存在しません。'))

            # エラーコードを出しすぎても仕方がないので、制限を5回までとする。
            # Limit the error messages to 5.
            return len(opn_err_msg[0:5]) != 0, opn_err_msg[0:5], len(fmt_err_msg[0:5]) != 0, fmt_err_msg[0:5]

        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        # Replace results other than self.report_key_list with self.kNotMk.
        self.__replace_undef_char_with_NotMk()

        # 履歴がNanの場合は、''に置き換える。
        # Replace NaN values in history with an empty string.
        self.__replace_nan_char_with_space()

        # 学年毎の漢字を確認する。
        # Check kanji by grade level.
        self.__create_list_kanji_by_grade()

        # 学年毎の合計出題数を表示する。
        # Display the total number of questions per grade level.
        for grade in range(self.kGradeRange[0], self.kGradeRange[-1] + 1):
            # 指定した学年の問題を取得する。
            # Get problems for the specified grade.
            problem = self.get_problem_with_grade([grade])
            p_value = 0
            # 履歴から合計出題数を算出する。
            # Calculate the total number of questions from the history.
            for hist in problem[self.kHistory].values:
                p_value += len(hist)

            # 学年毎に合計出題数を出力する。
            #  Output the total number of questions per grade.
            self.print_info(str(grade) + '年生: ' + str(p_value) + '問')

        # エラーコードを出しすぎても仕方がないので、制限を5回までとする。
        # Limit the error messages to 5.
        return len(opn_err_msg[0:5]) != 0, opn_err_msg[0:5], len(fmt_err_msg[0:5]) != 0, fmt_err_msg[0:5]

    # 漢字の問題集を書き込む。
    # Save the kanji worksheet.
    def save_worksheet(self):
        """
        漢字の問題集を書き込む。
        Save the kanji worksheet.
        """
        wrt_err_msg = []

        # ファイルが存在する。
        # If the file exists.
        if os.path.exists(self.path_of_worksheet):
            try:
                self.worksheet.to_csv(self.path_of_worksheet, index=False, encoding='shift-jis')
                self.print_info('問題集(' + self.path_of_worksheet + ')を更新しました。')
            # 問題集を開くなどして、書き込みができない。
            # If unable to write due to the problem set being open, etc.
            except PermissionError:
                msg = '問題集(' + self.path_of_worksheet + ')を閉じてください。更新できません。'
                wrt_err_msg.append(self.print_error(msg))
        # ファイルが存在しない。
        # If the file does not exist.
        else:
            wrt_err_msg.append(self.print_error('問題集が存在しません。更新できませんでした。'))

        return len(wrt_err_msg) != 0, wrt_err_msg

    # 漢字の問題集をチェックする。
    # Check the kanji worksheet.
    def __check_worksheet(self):
        fmt_err_msg = []

        # ファイル形式をチェックする。
        # Check the file format.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_file_format()
        # 欠損値をチェックする。
        # Check for missing values.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_column_nan(fmt_err_msg)
        # 数値以外をチェックする。
        # Check for non-numeric values.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_column_non_numeric(fmt_err_msg)
        # 整数以外をチェックする。
        # Check for non-integer values.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_column_non_integer(fmt_err_msg)
        # 範囲外の数値をチェックする。
        # Check for out-of-range values.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_column_out_of_range(fmt_err_msg)
        # ルビの有無をチェックする。
        # Check for presence of ruby annotations.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_kanji_ruby(fmt_err_msg)
        # 問題文の構文をチェックする。
        # Check the syntax of problem statements.
        if len(fmt_err_msg) == 0:
            fmt_err_msg = self.__check_kanji_syntax(fmt_err_msg)

        return fmt_err_msg

    # 問題集から指定したステータスに該当する問題を取得する。
    # Retrieve problems from the worksheet that match the specified status.
    def get_problem_with_status(self, grade, status):
        """
        :param grade: 学年 / Grade level
        :type grade: list
        :param status: 採点結果 / Scoring result
        :type status: string

        問題集から指定したステータスに該当する問題を取得する。
        Retrieve problems from the worksheet that match the specified status.
        """
        tmp = self.get_problem_with_grade(grade)
        return tmp[tmp[self.kResult] == status]

    # 問題集から指定した学年の問題を取得する。
    # Retrieve problems from the worksheet for the specified grade level.
    def get_problem_with_grade(self, grade):
        """
        :param grade: 学年 / Grade level
        :type grade: list

        問題集から指定した学年の問題を取得する。
        Retrieve problems from the worksheet for the specified grade level.
        """
        return self.worksheet[self.worksheet[self.kGrade].isin(grade)]

    # 問題集から指定した答えの問題を取得する。
    # Retrieve problems from the worksheet with the specified answer.
    def get_problem_with_answer(self, kanji, grade):
        if not isinstance(grade, list):
            grade = [grade]

        # 答えに指定した漢字が含まれている問題を抽出する。
        # Extract problems where the answer contains the specified kanji characters.
        temp = self.worksheet[self.worksheet[self.kAnswer].apply(lambda x: any(char in x for char in kanji))]
        grade_list = list(range(1, max(grade) + 1))
        return temp[temp[self.kGrade].isin(grade_list)]

    # 指定した学年の漢字のリストを取得する。
    # Retrieve the list of kanji characters for the specified grade level.
    def get_kanji_by_grade_list(self, grade):
        return self.kanji_by_grade_list[grade]

    # 指定した学年の漢字が正解しているか否かを辞書形式で取得する。
    # Get a dictionary indicating whether each specified grade level kanji is correct or not.
    # 辞書のキーは漢字で、データはTrueが正解、Falseが正解以外。
    # The dictionary keys are kanji characters, and the values are True (correct) or False (not correct).
    def get_analysis_correct_kanji_by_grade_dict(self, grade):
        # 指定した学年の漢字のリストを取得する。
        # Get the list of kanji characters for the specified grade level.
        kanji_list = self.get_kanji_by_grade_list(grade)
        result_dict = {}

        # 指定した学年の漢字だけ処理をする。
        # Process only the kanji characters for the specified grade level.
        for kanji in kanji_list:
            # 問題集から指定した答えの問題を取得する。
            # Retrieve problems from the worksheet with the specified answer.
            problem_list = self.get_problem_with_answer(kanji, grade)

            # 漢字毎に辞書化し、その漢字が正解しているか否かを確認する。
            # Create a dictionary for each kanji character and check if it is correct.
            # 1つでも正解していれば正解と判断する。
            # If at least one problem is correct, consider the kanji as correct.#
            # その漢字ではなく、熟語が分からず間違っている可能性があるため。
            # It might be a compound word that the user doesn't recognize.
            result_dict[kanji] = False
            for result in problem_list[self.kResult]:
                if result == self.kCrctMk:
                    result_dict[kanji] = True

        return result_dict

    # デバッグ情報を標準出力する.
    def print_info(self, msg):
        return self.DebugPrint.print_info(msg)

    # エラーメッセージを標準出力する.
    def print_error(self, msg):
        return self.DebugPrint.print_error(msg)

    # ファイル形式をチェックする.
    def __check_file_format(self, fmt_err_msg=None):
        """
        :param fmt_err_msg: エラーメッセージ
        :type fmt_err_msg: string

        ファイル形式をチェックする.
        """
        if fmt_err_msg is None:
            fmt_err_msg = []
        # 必要な列が順番通りに存在していることを確認する.
        for i, column_name in enumerate(self.kFileColumns):
            msg = '問題集の ' + str(i + 1) + '列目は[' + str(column_name) + ']' + '列である必要があります.'
            # 問題集の列数のほうが大きいとき（列が不足していないとき）.
            if i < len(self.worksheet.columns):
                # 列の名称が不一致
                if column_name != self.worksheet.columns[i]:
                    fmt_err_msg.append(self.print_error(msg))
            # 問題集の列数のほうが小さいとき（列が不足しているとき）.
            else:
                fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 欠損値をチェックする.
    def __check_column_nan(self, fmt_err_msg=None):
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
    def __check_column_non_numeric(self, fmt_err_msg=None):
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
    def __check_column_non_integer(self, fmt_err_msg=None):
        """整数以外をチェックする."""
        # '学年', '番号' 列に整数以外が入っていないか確認.
        chk_list = [self.kGrade, self.kNumber]
        if fmt_err_msg is None:
            fmt_err_msg = []
        for col in chk_list:
            data = self.worksheet[col]
            msg = '[' + str(col) + ']列には数値を入れてください.'
            if any(list(data.astype(int).values) != data):
                fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 範囲外の数値をチェックする.
    def __check_column_out_of_range(self, fmt_err_msg):
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

    # ルビの有無をチェック
    def __check_kanji_ruby(self, fmt_err_msg):
        kanji_flg = False
        i = 0
        for statement in self.worksheet[self.kProblem]:
            for word in statement:
                if self.is_kanji(word):
                    kanji_flg = True
                elif kanji_flg:
                    if word != '<':
                        msg = str(i + 1) + '行目の問題文にルビがありません.'
                        fmt_err_msg.append(self.print_error(msg))
                    kanji_flg = False
                else:
                    kanji_flg = False

            i += 1

        return fmt_err_msg

    # 問題文の構文をチェックする.
    def __check_kanji_syntax(self, fmt_err_msg):
        n = len(self.worksheet[self.kProblem])
        for sentence, ans, num in zip(self.worksheet[self.kProblem], self.worksheet[self.kAnswer], range(n)):
            r_inflag = False  # ルビの True:開始記号<を通過したとき, False:ルビの終了記号>を通過したとき
            r_nest_err = False  # ルビの指定文字が True:入れ子になっているとき, False:入れ子になっていないとき
            r_cnt_err = False  # ルビの文字数が True:0のとき, False:1以上のとき
            r_err = False  # ルビの True:何れかが大文字, False:すべてルビが小文字

            r_word_cnt = 0  # ルビの文字数

            p_inflag = False  # 問題の True:開始記号[を通過したとき, False:問題枠の終了記号]を通過したとき
            p_nest_err = False  # 問題枠の True:指定文字が入れ子になっているとき, False:問題枠の指定文字が入れ子になっていないとき
            p_cnt_err = False  # 問題の True:文字数が0のとき, False:問題の文字数が1以上のとき

            p_word_cnt = 0  # 問題枠の文字数
            p_frame_cnt = 0  # 問題枠の数

            for word in list(sentence):
                ##########################################################
                # 問題文のルビ<>が入れ子になっていないか、文字が入っているか確認する.
                ##########################################################
                # 問題文のルビ<>が全角であることを確認する.
                if self.is_ruby_full_width_prefix(word) or self.is_ruby_full_width_suffix(word):
                    r_err = True
                if self.is_ruby_prefix(word):
                    # 入れ子判定: '<'の後に、'>'ではなく、'<'が来たとき
                    if r_inflag:
                        r_nest_err = True
                    r_inflag = True
                if self.is_ruby_suffix(word):
                    # 入れ子判定: '<'の前に、'>'が来たとき
                    if not r_inflag:
                        r_nest_err = True
                    else:
                        # 文字数違反
                        if r_word_cnt == 0:
                            r_cnt_err = True
                    r_inflag = False
                    r_word_cnt = 0
                if r_inflag and (not self.is_ruby_prefix(word)):
                    r_word_cnt += 1
                ##########################################################
                # 問題文の問題枠が入れ子になっていないか、文字が入っていないか確認する.
                ##########################################################
                if self.is_problem_prefix(word):
                    # 入れ子判定: '['の後に、']'ではなく、'['が来たとき
                    if p_inflag:
                        p_nest_err = True
                    p_inflag = True
                if self.is_problem_suffix(word):
                    # 入れ子判定: '['の前に、']'が来たとき
                    if not p_inflag:
                        p_nest_err = True
                    else:
                        # 文字数違反
                        if p_word_cnt == 0:
                            p_cnt_err = True
                        else:
                            p_cnt_err = False
                        p_frame_cnt += 1
                    p_inflag = False
                    p_word_cnt = 0
                if p_inflag and (not self.is_problem_prefix(word)):
                    p_word_cnt += 1

            if r_cnt_err:
                msg = str(num + 1) + '行目の問題文のルビが空欄です.'
                fmt_err_msg.append(self.print_error(msg))

            if r_err:
                msg = str(num + 1) + '行目の問題文のルビの記号が全角です.'
                fmt_err_msg.append(self.print_error(msg))

            if r_nest_err and not r_err:
                msg = str(num + 1) + '行目の問題文のルビの指定が入れ子になっています.'
                fmt_err_msg.append(self.print_error(msg))

            if p_nest_err:
                msg = str(num + 1) + '行目の問題文の問題枠の指定が入れ子になっています.'
                fmt_err_msg.append(self.print_error(msg))

            if p_cnt_err:
                msg = str(num + 1) + '行目の問題文の問題枠が空欄です.'
                fmt_err_msg.append(self.print_error(msg))

            if len(ans) != p_frame_cnt and not p_nest_err and not p_cnt_err:
                msg = str(num + 1) + '行目の問題文の問題枠と答えの文字数が一致しません.'
                fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 未定義の文字をNotMkに置き換える.
    def __replace_undef_char_with_NotMk(self):
        """未定義の文字をNotMkに置き換える."""
        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        worksheet = self.worksheet
        for key in self.report_key_list:
            worksheet = worksheet[worksheet[self.kResult] != key]

        pd_idx = worksheet.index.values
        if len(pd_idx) > 0:
            self.worksheet.loc[pd_idx, self.kResult] = self.kNotMk
            self.save_worksheet()

    # 履歴がNanの場合は、''に置き換える。
    def __replace_nan_char_with_space(self):
        # 履歴がNanの場合は、''に置き換える。
        worksheet = self.worksheet[pd.isna(self.worksheet[self.kHistory])]
        pd_idx = worksheet.index.values
        if len(pd_idx) > 0:
            self.worksheet.loc[pd_idx, self.kHistory] = self.worksheet.loc[pd_idx, self.kHistory].fillna('')
            self.save_worksheet()

    # 問題集から学年に対応する漢字をリスト化する.
    def __create_list_kanji_by_grade(self):
        """問題集から学年に対応する漢字をリスト化する."""
        # このリストは不必要なルビを削除するための判断材料として使用する.
        grade_old = []  # 今までの漢字を格納するリスト
        for grade in range(self.kGradeRange[0], self.kGradeRange[1] + 1):
            # 学年に該当するデータを抽出する.
            worksheet = self.get_problem_with_grade([grade])
            # 抽出したデータが存在する場合
            if len(worksheet) > 0:
                # 1語ずつ配列に格納する
                for ans in worksheet[self.kAnswer]:
                    self.kanji_by_grade_list[grade].append([char for char in ans])

                # 多次元を1次元に変換
                self.kanji_by_grade_list[grade] = [item for sublist in self.kanji_by_grade_list[grade] for item in
                                                   sublist]
                # ソートして、ユニークにする.
                self.kanji_by_grade_list[grade] = sorted(self.kanji_by_grade_list[grade])
                self.kanji_by_grade_list[grade] = list(set(self.kanji_by_grade_list[grade]))
                # 前の学年の漢字のみ取り除く.
                self.kanji_by_grade_list[grade] = list(set(self.kanji_by_grade_list[grade]) - set(grade_old))

                # 現在の学年の漢字だけを残すため、それ以降の漢字を記憶しておく.
                grade_old = grade_old + self.kanji_by_grade_list[grade]

                # 学年毎に習う漢字数を表示する.
                self.print_info('小学' + str(grade) + '年生: 全 ' + str(len(self.kanji_by_grade_list[grade])) + ' 文字')

    def is_ruby_prefix(self, word):
        return word == u'<'

    def is_ruby_full_width_prefix(self, word):
        return word == u'＜'

    def is_ruby_full_width_suffix(self, word):
        return word == u'＞'

    def is_ruby_suffix(self, word):
        return word == u'>'

    def is_problem_prefix(self, word):
        return word == u'['

    def is_problem_suffix(self, word):
        return word == u']'

    # 受け取った文字が漢字か否かを確認し、その結果を返す。
    # Check if the received character is a kanji or not, and return the result.
    def is_kanji(self, char):
        """
        :param char: 文字 / Character
        :return: True:漢字 / Kanji, False:漢字以外 / Other than a Kanji

        受け取った文字が漢字か否かを確認し、その結果を返す。
        Check if the received character is a kanji or not, and return the result.
        """
        return '\u4e00' <= char <= '\u9faf'


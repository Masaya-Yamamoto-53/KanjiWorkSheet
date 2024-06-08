# KanjiWorkSheet_prob.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import os
import datetime as datetime
import pandas as pd
import numpy as np
from KanjiWorkSheet import KanjiWorkSheet
from KanjiWorkSheet_draw import KanjiWorkSheet_draw


# 答えが重複している漢字のインデックスを除去する。
# Remove the index of Kanji with duplicate answers.
def remove_duplicates_index(list_value, exclusion_list):
    return [value for value in list_value if value not in exclusion_list]


# 答えの漢字が重複しているインデックスを作成する。
# Create an index where the answer Kanji is duplicated.
def create_duplicate_kanji_index_dict(ans_list):
    index_map = {}
    result_dict = {}

    # この要素数はself.kanji_worksheetのインデックスとは違う。
    # The number of elements is different from the index of self.kanji_worksheet.
    # 答えのリストと、その要素数を格納する。
    # Store the list of answers and its number of elements.
    for i, phrase in enumerate(ans_list):
        # 答えの熟語を分解する。 / Decompose the compound word of the answer.
        for char in phrase:
            if char in index_map:
                # キーが存在するとき。 / When the key exists.
                index_map[char].append(i)
            else:
                # キーが存在しないとき。 / When the key does not exist.
                index_map[char] = [i]

    for char, index in index_map.items():
        # インデックスが複数あるもののみ対象とする。
        # Only those with multiple indices are targeted.
        # 複数ない場合は重複していないため。
        # If there are no multiple, it is not duplicated.
        if len(index) > 1:
            result_dict[char] = index

    return result_dict


# 答えが重複している漢字の問題を除去する。
# Remove Kanji problems that have duplicate answers.
def remove_duplicates_kanji_problem_index(kanji_worksheet_idx, duplicate_dict):
    # 例 / Example)
    # 雨 [0, 2, 5, 8]
    # 右 [1, 3]
    # 一 [4, 6]
    # 円 [6, 7]

    # [0]: 0を選んだため、2, 5, 8 は除外 / Selected 0, so exclude 2, 5, 8
    # [1]: 1を選んだため、3は除外 / Selected 1, so exclude 3
    # [4]: 4を選んだため、6は除外 / Selected 4, so exclude 6
    # [7]: 6を除外したため、7を選択 / Excluded 6, so select 7

    # 答えに同じ漢字が内容に重複しているものを取り除く。
    # Remove those that have the same Kanji in the answer.
    first_idx = []  # 重複を取り除いた結果 / Result of removeing duplicates
    exclusion_list = []  # 除外リスト / Exclusion list
    for list_value in duplicate_dict.values():
        list_value = set(list_value)
        list_value = remove_duplicates_index(list_value, exclusion_list)

        # 問題の答えが重複している場合は先頭のインデックスだけ取り除く。
        if len(list_value) > 0:
            first_idx.append(list_value[0])

        # 除外リストを更新
        exclusion_list = exclusion_list + [value for value in list_value]

    # 重複しているリストを一次元にする。
    duplicate = []
    for list_value in duplicate_dict.values():
        for value in list_value:
            duplicate.append(value)

    # 除外したいものだけ残す。
    duplicate = remove_duplicates_index(duplicate, first_idx)
    duplicate = sorted(set(duplicate))
    duplicate = kanji_worksheet_idx[duplicate]  # 除外したい問題のインデックスを得る。

    # 漢字の問題が被っていない問題のインデックスを取得する。
    not_duplicate = remove_duplicates_index(kanji_worksheet_idx, duplicate)

    return not_duplicate, duplicate


class KanjiWorkSheet_prob(KanjiWorkSheet):
    def __init__(self):
        super(KanjiWorkSheet_prob, self).__init__(debug=True)

        # 漢字プリントの問題を代入するためのデータフレーム
        # DataFrame to assign the problems for the Kanji worksheet
        self.kanji_worksheet = pd.DataFrame()
        # 漢字プリントに出題する問題のインデックスを代入するためのリスト
        # List for assigning the indices of the problems to be asked in the Kanji worksheet
        self.kanji_worksheet_idx = []

        # 間違えた問題のインデックス
        # Index of the question that was answered incorrectly
        self.list_x_idx = []
        # 出題してからしばらく再出題していない問題のインデックス
        # Index of the question that has not been asked for a while
        self.list_a_idx = []
        # 三日間前違えた問題のインデックス
        # Index of the question that was answered incorrectly three days ago
        self.list_d_idx = []
        # 一週間前に間違えた問題のインデックス
        # Index of the question that was answered incorrectly a week ago
        self.list_w_idx = []
        # 一ヶ月前に間違えた問題のインデックス
        # Index of the question that was answered incorrectly a month ago
        self.list_m_idx = []
        # 未出題のインデックス
        # Index of the unasked question
        self.list_n_idx = []
        # 正解している問題のインデックス
        # Index of the question that is being answered correctly
        self.list_o_idx = []

        # 作成日 / Creation date
        self.create_date = pd.to_datetime(datetime.datetime.today())

        # 出題対象者(生徒名)
        # The name of the student who will be asked the questions
        self.student_name = ''
        # 出題範囲指定(学年)
        # The grade range for the questions
        self.grade = []

        self.kMDRW = 0  # 復習モード / Review mode
        self.kMDTR = 1  # 練習モード / Training mode
        self.mode = self.kMDTR  # 出題モード / Question mode
        # 出題数(デフォルト:20)
        # Number of questions (default: 20)
        self.number_of_problem = 20

    # 生徒の名前を設定する。
    # Set the student's name.
    def set_student_name(self, name):
        """
        :parameter name: 生徒の名前 / The student's name
        :type name: string

        生徒の名前を設定する。
        Set the student's name.
        """
        self.student_name = name
        self.print_info('生徒の名前を ' + self.student_name + ' に設定しました。')

    # 生徒の名前を取得する。
    # Get the student's name.
    def get_student_name(self):
        """
        生徒の名前を取得する。
        Get the student's name.
        """
        return self.student_name

    # 漢字プリントの作成日を設定する。
    # Set the creation date of the Kanji worksheet.
    def set_create_date(self, date):
        """
        :param date: 作成日
        :type date: datetime.datetime

        漢字プリントの作成日を設定する。
        Set the creation date of the Kanji worksheet.
        """
        self.create_date = date

    # 漢字プリントの作成日を取得する。
    # Get the creation date of the Kanji worksheet.
    def get_create_date(self):
        """
        漢字プリントの作成日を取得する。
        Get the creation date of the Kanji worksheet.
        """
        return self.create_date

    # 漢字プリントの出題範囲を設定する。
    # Set the question range of the Kanji worksheet.
    def set_grade(self, grade_list):
        """
        :param grade_list: 学年(リストで複数選択可能) / Grades (multiple selections possible in a list)
        :type grade_list: list

        漢字プリントの出題範囲を設定する。
        Set the question range of the Kanji worksheet.
        """
        self.grade = grade_list
        self.print_info('学年を ' + str(self.grade) + ' に設定しました。')

    # 漢字プリントの出題範囲を取得する。
    # Get the question rage of the Kanji worksheet.
    def get_grade(self):
        """
        漢字プリントの出題範囲を取得する。
        Get the question rage of the Kanji worksheet.
        """
        return self.grade

    # 出題モードを設定する。
    # Set the question mode.
    def set_mode(self, mode):
        """
        :param mode: 出題モード

        出題モードを設定する。
        Set the question mode.
        """
        self.mode = mode
        self.print_info('出題モードを ' + str(self.mode) + ' に設定しました。')

    # 出題モードを取得する。
    # Get the question mode.
    def get_mode(self):
        """
        出題モードを取得する。
        Get the question mode.
        """
        return self.mode

    # 漢字プリントの問題の出題数を設定する。
    # Set the number of questions for the Kanji worksheet.
    def set_number_of_problem(self, num):
        """
        :param num: 漢字プリントの問題の出題数 / The number of questions for the Kanji worksheet
        :type num: int

        漢字プリントの問題の出題数を設定する.
        Set the number of questions for the Kanji worksheet.

        問題の出題数は最大20問とし, 20問よりも多く問題数を指定した場合は, 20問にする。
        The number of questions is up to 20, and if more than 20 questions are specified, it will be 20.

        [理由] / [Reason]

        設定したフォントサイズで問題を出題した場合, A4用紙におさまりが良いのが20問だったため。
        When setting the font size and creating questions, it was found that 20 questions fit well on A4 paper.
        """
        # 出題数が0以下の場合は, 0を設定する。
        # If the number of questions is less than or equal to 0, set it to 0.
        num = max(num, 0)
        # 出題数が20以上の場合は, 20を設定する。
        # If the number of questions is more than 20, set it to 20.
        num = min(num, 20)
        self.number_of_problem = num
        self.print_info('出題数を ' + str(self.number_of_problem) + ' に設定しました。')

    # 漢字プリントの問題の出題数を取得する。
    # Get the number of questions for the Kanji worksheet.
    def get_number_of_problem(self):
        """
        漢字プリントの問題の出題数を取得する。
        Get the number of questions for the Kanji worksheet.
        """
        return self.number_of_problem

    # 漢字プリントの出題記録を作成する。
    # Create a log file for the Kanji worksheet questions.
    def create_kanji_worksheet_logfile(self, path):
        """
        :param path: 出題記録のパス / Path of the question log

        漢字プリントの出題記録を作成する。
        Create a log file for the Kanji worksheet questions.
        """
        # 新しく作成した問題のリストをログに出力する。
        # Output the list of newly created questions to the log.
        if len(self.kanji_worksheet) > 0:
            # インデックスは問題集とマージするときに必要になるため、削除しない。
            # Do not delete the index as it is needed when merging with the question set.
            self.kanji_worksheet.to_csv(path, encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を作成しました。')
            return True
        else:
            self.print_error('問題を作成していないため、ログを作成できません。')
            return False

    # 漢字プリントの出題記録に採点結果を反映する。
    # Reflect the grading results in the Kanji worksheet question record.
    def record_kanji_worksheet_logfile(self, path, result_list):
        """
        :param path: 出題記録のパス / Path of the question record
        :param result_list: 採点結果 / Grading result

        漢字プリントの出題記録に採点結果を反映する。
        Reflect the grading results in the Kanji worksheet question record.
        """
        opn_err_msg = []
        fmt_err_msg = []

        # ファイルが存在する。
        # The file exists.
        if os.path.exists(path):
            logs = pd.read_csv(path, sep=',', index_col=0, encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を読み込みました.')

            # 出題記録と採点結果の数が一致。
            # The number of question records and grading results match.
            if len(logs[self.kResult]) == len(result_list):
                # 採点結果を反映する。
                # Reflect the grading results.
                logs[self.kResult] = result_list
                # 更新した漢字プリントの出題記録ファイルを書き込む。
                # Write the updated Kanji worksheet question record file.
                logs.to_csv(path, encoding='shift-jis')
                self.print_info('ログファイル(' + path + ')を書き込みました。')
            else:
                fmt_err_msg.append(self.print_error('ログファイルと採点結果の数が不一致です。'))

        # ファイルが存在しない。
        # The file does not exist.
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')が読み込みませんでした。'))

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    # 漢字プリントの出題記録を削除する。
    # Delete the Kanji worksheet question record.
    def delete_kanji_worksheet_logfile(self, path):
        """
        :param path: 出題記録のパス / Path of the question record
        :type path: string

        漢字プリントの出題記録を削除する.
        Delete the Kanji worksheet question record.
        """
        # ファイルが存在する.
        # The file exists.
        if os.path.exists(path):
            # 漢字プリントの出題記録を削除する.
            # Delete the Kanji worksheet question record.
            os.remove(path)
            self.print_info('ログファイル(' + path + ')を削除しました.')

        # ファイルが存在しない.
        # The file does not exist.
        else:
            self.print_error('存在しないログファイル(' + path + ')を削除しようとしました.')

    # self.kanji_worksheetの「答え]を分割し、辞書のキーを作成する。
    # Split the "answers" in self.kanji_worksheet and create dictionary keys.
    def get_answer_kanji_keyword(self):
        target_kanji_problem_list = []
        # 選択した問題の答えを取り出す。
        # Retrieve answers for the selected problem.
        target_kanji_answer = self.worksheet.loc[self.kanji_worksheet_idx, self.kAnswer].values
        # 1語ずつ配列に格納する。
        # Store each word in an array.
        target_kanji_answer = target_kanji_answer.tolist()
        for ans in target_kanji_answer:
            target_kanji_problem_list.append([char for char in ans])

        # 多次元を1次元に変換し、ソートする。
        # Convert multidimensional list to a flat list and sort it.
        target_kanji_problem_list = [item for sublist in target_kanji_problem_list for item in sublist]
        target_kanji_problem_list = sorted(set(target_kanji_problem_list))

        # 答えの漢字をキーワードにする。
        # Use the kanji characters from the answers as keywords.
        return target_kanji_problem_list

    # 漢字を読み仮名に置き換える。
    def replace_kanji_with_ruby(self):
        self.print_info('問題文中に答えが存在するため、ひらがなに置き換えました。')
        kanji_cnt = 0  # 読み仮名に置き換えた直近の漢字の数
        flg = False    # 読み仮名に置き換える必要がある漢字を見つけた時に立てるフラグ。置き換え後にフラグを落とす。

        # 答えを格納
        answer_kanji_keyword = self.get_answer_kanji_keyword()

        # リストを問題数分だけ初期化する。
        problem_statement_list = ['' for _ in range(self.get_number_of_problem())]
        for i, statement in enumerate(self.worksheet.loc[self.kanji_worksheet_idx, self.kProblem]):
            for word in statement:
                # 語が漢字である場合
                if self.is_kanji(word):
                    # 問題文の漢字が答えで使っている場合
                    if word in answer_kanji_keyword:
                        flg = True
                    problem_statement_list[i] = problem_statement_list[i] + word
                    kanji_cnt += 1
                # ルビの始まり
                elif self.is_ruby_prefix(word):
                    if flg:
                        problem_statement_list[i] = problem_statement_list[i][:-1 * kanji_cnt]
                    else:
                        problem_statement_list[i] = problem_statement_list[i] + word
                    kanji_cnt = 0
                # ルビの終わり
                elif self.is_ruby_suffix(word):
                    if flg:
                        # 漢字をルビに置き換えた場合はルビのサフィックスは削除する。
                        flg = False
                    else:
                        problem_statement_list[i] = problem_statement_list[i] + word
                else:
                    problem_statement_list[i] = problem_statement_list[i] + word

            # 漢字を平仮名で置き換えた場合は問題文を更新する。
            if statement != problem_statement_list[i]:
                self.print_info('Before: ' + statement)
                self.print_info('After : ' + problem_statement_list[i])
                idx = self.kanji_worksheet_idx[i]
                self.worksheet.loc[idx, self.kProblem] = problem_statement_list[i]

    # 不要なルビを問題文から削除する.
    def remove_unnecessary_ruby(self):
        del_flg = False
        ruby_flg = False
        self.print_info('問題文中に不要なルビがあるため、削除しました.')
        problem_statement_list = ['' for _ in range(self.get_number_of_problem())]
        for statement, idx, i in zip(self.worksheet.loc[self.kanji_worksheet_idx, self.kProblem],
                                     self.kanji_worksheet_idx,
                                     range(self.get_number_of_problem())):
            for word in statement:
                if self.is_kanji(word):
                    # 選択した学年の最高位は除く。
                    del_flg = False
                    for grade in range(1, max(self.get_grade())):
                        if word in self.get_kanji_by_grade_list(grade):
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
                self.worksheet.loc[idx, self.kProblem] = problem_statement_list[i]

    # 条件に該当する問題のインデックスを返す.
    def get_kanji_worksheet_index(self, result, sort=False, days=-1):
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力できないため、
        # 2時間オフセットを入れる。
        now_time = self.create_date + datetime.timedelta(hours=2)

        if result == self.kCrctMk or result == self.kNotMk:
            tmp_list = self.kanji_worksheet[self.kanji_worksheet[self.kResult] == result]
        else:
            tmp_list = self.worksheet[self.worksheet[self.kResult] == result]

        # 最終更新日の昇順で更新する指定がある場合は、ソートを行う.
        if sort:
            tmp_list = tmp_list.sort_values(self.kLastUpdate, ascending=True)

        # 期間の指定がある場合は、その期間に該当する問題文のみ抽出する.
        if days != -1:
            date_str = tmp_list[self.kLastUpdate]
            date_str = date_str.replace("'", "")  # ここでreplaceの結果を再代入
            print(type(date_str))
            delta = datetime.timedelta(days=days) < (now_time - pd.to_datetime(date_str))
            tmp_list = tmp_list[delta]

        return tmp_list.index.values

    # 答えの漢字が重複している最終更新日を作成する。
    def create_long_time_no_question_dict(self, ans_list, date_list, days=30):
        # この要素数はself.kanji_worksheetのインデックスとは違う。
        # 答えのリストと、その最終更新日を格納する。
        date_map = {}
        for i, phrase in enumerate(ans_list):
            # 答えの熟語を分解する。
            for char in phrase:
                # Nanでない場合
                if isinstance(date_list[i], str) or ~np.isnan(date_list[i]):
                    idx_date_list = [i, date_list[i]]
                    if char in date_map:
                        # キーが存在するとき。
                        date_map[char].append(idx_date_list)
                    else:
                        # キーが存在しないとき。
                        date_map[char] = [idx_date_list]

        # 各問題の最終更新日の中で、直近のものを選んで辞書に登録する。
        newest_dates_dict = {}
        old_kanji_dict = {}
        for key, idx_date_list in date_map.items():
            for idx_date_str in idx_date_list:
                date_str = idx_date_str[1]
                date_str = date_str.replace('"', '')
                date_str = date_str.replace("'", '')
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
                if key not in newest_dates_dict or date_obj > newest_dates_dict[key][1]:
                    newest_dates_dict[key] = [idx_date_str[0], date_obj]

            # 前回出題してから経過した日数から候補を選択
            for grade in self.grade:
                if key in self.get_kanji_by_grade_list(grade):
                    if self.create_date - newest_dates_dict[key][1] > datetime.timedelta(days=days):
                        old_kanji_dict[key] = newest_dates_dict[key][0]
                        self.print_info('(' + str(key) + ') ' + '経過時間: '
                                        + str(self.create_date - newest_dates_dict[key][1]))

        self.print_info(('合計：' + str(len(old_kanji_dict))))

        return old_kanji_dict

    # 重複した漢字の問題を削除する。
    # Remove duplicate Kanji problems.
    def remove_duplicates_kanji_problem(self, num, result, sort=False):
        # 最終更新日の古い順にソートしたもの候補にする。
        # Make the ones sorted in order of the oldest last update date a candidate.
        # 答えが重複している問題を除去することから、指定した問題数を確保するため、全て候補にする。
        # Since we remove problems that have duplicate answers,
        # we make all of them candidates to secure the specified number of problems.
        kanji_worksheet_idx = self.get_kanji_worksheet_index(result, sort=sort)

        # 答えに重複がある問題についてはなるべく選択しないようにする。
        # For problems with duplicate answers, try not to select them as much as possible.
        # 問題集から答えの列を抽出する。
        # Extract the column of answers from the problem set.
        ans_list = self.kanji_worksheet.loc[kanji_worksheet_idx, self.kAnswer]
        # 答えの漢字が重複しているインデックスを作成する。
        # Create an index where the answer Kanji is duplicated.
        # (漢字をキーにして、値をインデックスにした辞書を作成する。)
        # (Create a dictionary with Kanji as the key and the index as the value.)
        duplicate_dict = create_duplicate_kanji_index_dict(ans_list)
        # 重複した問題のインデックスを削除する。
        # Remove the index of duplicate problems.
        (list_not_duplicate, list_duplicate) = remove_duplicates_kanji_problem_index(
            kanji_worksheet_idx, duplicate_dict)

        # 重複を削除した問題のインデックスを問題集だけ選出し、シャッフルする。
        # Select only the problem set from the index of the problem with duplicates removed, and shuffle it.
        kanji_worksheet_idx = list_not_duplicate[0:num]
        np.random.shuffle(kanji_worksheet_idx)

        # 重複箇所を削ることによって、問題数が減ってしまうので、不足してしまった場合は、重複しても良いので選出する。
        # If the number of problems decreases due to pruning duplicates,
        # select even if it is duplicated if it is insufficient.
        for value in list_duplicate:
            kanji_worksheet_idx.append(value)
        # 指定数だけ問題を得られない場合もあるため、それを考慮して出題数を再設定する。
        # Since there may be cases where the specified number of problems cannot be obtained.
        # reconsider the number of questions considering that.
        kanji_worksheet_idx = kanji_worksheet_idx[0:num]

        return kanji_worksheet_idx, len(kanji_worksheet_idx)

    # 選出した問題の最終更新日を更新する。
    # Update the last update date of the selected problem.
    def set_last_update_kanji_worksheet(self):
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        # Enclose with single quotes to prevent strange interpretation and breaking of the format when reading in Excel.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        # 選出した問題の最終日を更新する。
        # Update the last day of the selected problem.
        self.worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now

        return self.kanji_worksheet

    # 漢字プリントを作成する。
    # Create a Kanji worksheet
    def create_kanji_worksheet(self):
        """
        漢字プリントを作成する。
        Create a Kanji worksheet
        """
        err_msg = []
        self.kanji_worksheet = self.worksheet

        # 漢字プリントの問題集に問題が1問も存在しないとき。
        # When there are no problems in the Kanji worksheet problem set.
        if len(self.kanji_worksheet) <= 0:
            # '問題集を選択していません.'
            msg = 'No problem set selected.'
            err_msg.append(self.print_error(msg))
            return len(err_msg) != 0, err_msg

        # 出題形式に合わせて問題を抽出する。
        # Extract problems according to the question format.
        # 指定した学年のみ抽出する。
        # Only extract the specified grade.
        if len(self.grade) > 0:
            num = len(self.kanji_worksheet)
            self.kanji_worksheet = self.get_problem_with_grade(self.grade)

            # '学年は ' + str(self.grade) + ' 年'
            msg = 'The grade is ' + str(self.grade)
            self.print_info(msg)
            # '問題集の問題数は ' + str(num) + ' から ' + str(len(self.kanji_worksheet)) + ' に変更.'
            msg = 'The number of problems in the problem set has changed from '
            msg = msg + str(num) + ' to ' + str(len(self.kanji_worksheet)) + '.'
            self.print_info(msg)
        else:
            err_msg.append(self.print_error('学年の指定がありません.'))
            return len(err_msg) != 0, err_msg

        # 設定した出題数よりも、問題集の問題数が少ない時、問題集の問題数を出題数とする.
        num_p = self.get_number_of_problem()
        if num_p > 0:
            num_i = len(self.kanji_worksheet)
            # '設定出題数は ' + str(num_p) + ' です.'
            msg = 'The set number of questions is ' + str(num_p) + '.'
            self.print_info(msg)
            if num_i < num_p:
                # '出題数は ' + str(num_i) + ' です.'
                self.set_number_of_problem(num_i)
                # '出題数は ' + str(num_i) + ' です.'
                msg = 'The number of questions is ' + str(num_i) + '.'
            else:
                # '出題数は ' + str(num_p) + ' です.'
                self.set_number_of_problem(num_p)
                # '出題数は ' + str(num_p) + ' です.'
                msg = 'The number of questions is ' + str(num_i) + '.'
            self.print_info(msg)
        else:
            # '出題数の指定がありません.'
            msg = 'There is no specification of the number of questions.'
            err_msg.append(msg)
            return len(err_msg) != 0, err_msg

        # '漢字テストを作成します。'
        self.print_info('========================================')
        self.print_info('Creating a Kanji worksheet')
        self.print_info('========================================')

        # 作成日を更新する。 / Update the creation date.
        self.create_date = pd.to_datetime(datetime.datetime.today())

        # モードの設定にあった問題を選択する。
        # Select the problem according to the mode setting.
        # 復習モード / Review mode
        if self.mode == self.kMDRW:
            self.create_review_mode_kanji_worksheet()
        # 練習モード / Training mode
        else:
            self.create_train_mode_kanji_worksheet()

        # 問題の答えに含まれている漢字を取得する.
        # Get the Kanji included in the answer to the problem.
        self.get_answer_kanji_keyword()
        # 問題文に答えが記載されている場合は、その漢字をルビに置き換える.
        # If the answer is written in the problem statement,
        # replace that Kanji with ruby.
        self.replace_kanji_with_ruby()
        # 選択中の学年未満のルビを削除する.
        # Remove the ruby less than the selected grade.
        self.remove_unnecessary_ruby()

        # ランダムに並び替える.
        # Shuffle randomly.
        np.random.shuffle(self.kanji_worksheet_idx)
        # 出題する問題が決まったため、最終更新日を更新する.
        # Since the problem to be asked has been decided, update the last update date.
        self.kanji_worksheet = self.set_last_update_kanji_worksheet()
        # 問題集を抽出した物だけにする.
        # Only the extracted problem set.
        self.kanji_worksheet = self.worksheet.loc[self.kanji_worksheet_idx, :]

        return len(err_msg) != 0, err_msg

    # 復習モードの漢字プリントを作成する。
    # Get the index of the Kanji question that
    # has not been re-questioned for a while after questioning.
    def create_review_mode_kanji_worksheet(self):
        """
        復習モードの漢字プリントを作成する。
        Create a dictionary of Kanji that has passed more than 30 days since the last question.
        """
        self.print_info("Review Mode")

        # 間違えた問題のインデックスを取得する。
        # Extract the problem with the specified answer,
        # shuffle it, and get the index at the top.
        self.list_x_idx = self.get_kanji_worksheet_index(self.kIncrctMk, days=0)
        np.random.shuffle(self.list_x_idx)

        # インデックスをマージする。
        # Merge the indices.
        self.kanji_worksheet_idx = self.list_x_idx[0:self.get_number_of_problem()]
        self.set_number_of_problem(len(self.list_x_idx))

    # 出題してからしばらく再出題していない漢字の問題のインデックスを取得する。
    # Get the index of the Kanji question
    # that has not been re-questioned for a while after questioning.
    def get_kanji_worksheet_a_index(self):
        # 最後の出題から30日以上経過した漢字の辞書を作成。
        # Create a dictionary of Kanji that has passed more than 30 days since the last question.
        kanji_dict = self.create_long_time_no_question_dict(
            self.kanji_worksheet[self.kAnswer].tolist(),
            self.kanji_worksheet[self.kLastUpdate].tolist(),
            days=30
        )

        # 指定した答えの問題を抽出し、シャッフルしてその先頭のインデックスを得る。
        # Extract the problem with the specified answer, shuffle it, and get the index at the top.
        idx_list = []
        for key in kanji_dict.keys():
            tmp_df_idx = self.get_problem_with_answer(key, self.grade).index.values
            np.random.shuffle(tmp_df_idx)
            idx_list.append(tmp_df_idx[0])

        return idx_list

    # 訓練モードの漢字プリントを作成する。
    # Create a Kanji worksheet in training mode.
    def create_train_mode_kanji_worksheet(self):
        """
        訓練モードの漢字プリントを作成する。
        Create a Kanji worksheet in training mode.
        """
        self.print_info("Selected training mode.")

        # テスト問題を選定する。/ Select the test questions.
        # 出題してからしばらく再出題していない漢字の問題のインデックスを取得する。
        # Get the index of the Kanji question that has not been re-questioned for a while after questioning.
        self.list_a_idx = self.get_kanji_worksheet_a_index()
        # 三日前に間違えた問題のインデックスを取得する。
        # Get the index of the question that was wrong three days ago.
        self.list_d_idx = self.get_kanji_worksheet_index(self.kDayMk, days=3)
        # 一週間前に間違えた問題のインデックスを取得する。
        # Get the index of the question that was wrong a week ago.
        self.list_w_idx = self.get_kanji_worksheet_index(self.kWeekMk, days=7 - 1)
        # 一ヶ月前に間違えた問題のインデックスを取得する。
        # Get the index of the question that was wrong a month ago.
        self.list_m_idx = self.get_kanji_worksheet_index(self.kMonthMk, days=7 * 4 - 7)

        # 4つの問題を連結する。/ Concatenate the four questions.
        # 優先順位: 30日以上出題していない問題 ＞ 3日後に出題 ＞ 1週間後に出題 ＞ 1ヶ月後に出題 ＞ 未出題 ＞ 正解
        # Priority: more than 30 days > after three days > after a week > after a month > unasked > Correct
        self.kanji_worksheet_idx = np.concatenate([self.list_a_idx, self.list_d_idx, self.list_w_idx, self.list_m_idx])

        num = self.get_number_of_problem() - len(self.kanji_worksheet_idx)
        if num <= 0:
            # 間違えた問題で満足した場合 / If satisfied with the wrong questions
            # 1~20番目の問題のインデックスを作成する。 / Create an index of the 1st to 20th questions.
            self.kanji_worksheet_idx = self.kanji_worksheet_idx[0: self.get_number_of_problem()]
        else:
            # 間違えた問題だけでは不足している場合 / If there are not enough wrong questions
            # まだ出題していない問題を抽出する。 / Extract the questions that have not yet been asked.
            (self.list_n_idx, n_num) = self.remove_duplicates_kanji_problem(num, self.kNotMk, sort=False)
            self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_n_idx[0:n_num]])

            # 未出題だけでは確保できなかった。 / It could not be secured only by unasked.
            num = num - len(self.list_n_idx[0:n_num])
            if num > 0:
                # 既に出題し、正解している問題を候補に挙げる。
                # Already asked and correct questions are candidates.
                (self.list_o_idx, _) = self.remove_duplicates_kanji_problem(num, self.kCrctMk, sort=True)
                self.list_o_idx = list(set(self.list_o_idx) - set(self.list_a_idx))
                o_num = len(self.list_o_idx)

                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_o_idx[0:o_num]])

                # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
                # If it is still not enough,
                # you can select the unasked questions that are scheduled to be asked one day later,
                # But for rare case, cope by reducing the number of questions.
                # レアケースのため、出題数を削ることで対応する。
                self.set_number_of_problem(len(self.kanji_worksheet_idx))

    # 漢字プリントの出題問題の概要を表示する。
    # Display the overview of the Kanji worksheet problem.
    def report_kanji_worksheet(self):
        """
        漢字プリントの出題問題の概要を表示する。
        Display the overview of the Kanji worksheet problem.
        """
        msg_list = [
            '            Not yet asked: ',  # 未出題:
            '                  Correct: ',  # 正解:
            '                Incorrect: ',  # 不正解:
            'Reimplement after 3 days : ',  # 3日以降に再実施:
            'Reimplement after 1 week : ',  # １週間後に再実施:
            'Reimplement after 1 month: '  # １ヶ月後に再実施:
        ]

        self.print_info('========================================')
        self.print_info('出題内容')
        self.print_info('========================================')
        for key, msg in zip(self.report_key_list, msg_list):
            self.print_info(msg + str(len(self.kanji_worksheet[self.kanji_worksheet[self.kResult] == key])) + ' 件')

        return self.report_key_list

    # 漢字プリントの出題記録を問題集に反映する。
    # Reflect the question record of Kanji work sheet on the problem set.
    def update_kanji_worksheet(self, path):
        """
        :param path: 出題記録のパス / Path of the question record

        漢字プリントの出題記録を問題集に反映する。
        Reflect the question record of Kanji work sheet on the problem set.
        """
        opn_err_msg = []
        fmt_err_msg = []

        # ログファイルが存在することを確認する。/ Confirm that the log file exists.
        if os.path.exists(path):
            # 前回のテスト結果を読み込む。/ Load the results of the previous test.
            logs = pd.read_csv(path, sep=',', index_col=0, encoding='shift-jis')
            msg = 'The log file (' + path + ') was loaded.'
            self.print_info(msg)
        # ファイルが存在しない。 / The file does not exist.
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

                # 整合を確認 / Check for consistency
                # 問題集の問題を挿入したりするとインデックスがずれてしまい、上手く記録できないため、そのポカヨケとしてチェックする.
                # When inserting problems from the problem set,
                # the index may shift, making it impossible to record properly.
                # Therefore, check as a mistake prevention.
                # '答え', '番号', '管理番号'を比較
                # Compare 'Answer', 'Number', 'Admin Number'
                if (self.worksheet.loc[idx, self.kAnswer] == logs.loc[idx, self.kAnswer]) \
                        and (self.worksheet.loc[idx, self.kNumber] == logs.loc[idx, self.kNumber]) \
                        and (self.worksheet.loc[idx, self.kAdminNumber] == logs.loc[idx, self.kAdminNumber]):

                    # [結果]列を更新する. / Update the [Result] colum.
                    # 【凡例】/ [Legend]
                    # NaN: self.kNotMk   : 未実施 / Not implemented
                    #   o: self.kCrctMk  : 今回正解 / Correct this time
                    #   x: self.kIncrctMk: 今回不正解 / Incorrect this time
                    #   d: self.kDayMk   : 3日後に実施(前回xで今回oの時)
                    #                      Implement after 3 days (when last time was x and this time is o)
                    #   w: self.kWeekMk  : 1週間後に実施(前回dで今回oの時)
                    #                      Implement after 1 week (when last time was d and this time is o)
                    #   m: self.kMonthMk : 1ヶ月後に実施(前回wで今回oの時)
                    #                      Implement after 1 month (when last time was w and this time is o)

                    # 今回、正解した場合 / If the answer is correct this time.
                    if new == self.kCrctMk:
                        if old == self.kIncrctMk:  # x -> d
                            key = self.kDayMk
                        elif old == self.kDayMk:  # d -> w
                            key = self.kWeekMk
                        elif old == self.kWeekMk:  # w -> m
                            key = self.kMonthMk
                        else:  # m -> o or - -> o
                            key = self.kCrctMk
                    # 今回、不正解の場合 / If the answer is incorrect this time.
                    else:  # x
                        key = self.kIncrctMk

                    # 最終更新日を更新 / Update the last update date
                    self.worksheet.loc[idx, self.kLastUpdate] = logs.loc[idx, self.kLastUpdate]
                    # 結果を反映 / Reflect the result
                    self.worksheet.loc[idx, self.kResult] = key
                    # 履歴を更新 / Update the history
                    self.worksheet.loc[idx, self.kHistory] = self.worksheet.loc[idx, self.kHistory] + new
                    # 各結果の回数をカウント / Count the occurrences of each result
                    result_dict[key] += 1
                else:
                    fmt_err_msg.append(self.print_error('ログファイルと問題集のインデックスが不一致です.'))

        # ログに反映した数を算出する。
        # Calculate the number reflected in the log.
        total = sum(result_dict[key] for key in self.report_key_list)

        if len(logs) != total:
            fmt_err_msg.append(self.print_error('ログファイルの問題数と登録件数が不一致です。'))
            fmt_err_msg.append(self.print_error('結果の記入に間違いがあるか、未記入である可能性があります。'))

        dy_num = str(result_dict[self.kDayMk])
        wk_num = str(result_dict[self.kWeekMk])
        mt_num = str(result_dict[self.kMonthMk])
        in_num = str(result_dict[self.kIncrctMk])
        ct_num = str(result_dict[self.kCrctMk])
        msgs = ['--------------------------------------------------------------------------------',
                '＊　明日以降に再実施する問題を ' + str(result_dict[self.kDayMk]) + ' 件 登録しました。',
                '＊　１週間後に再実施する問題を ' + str(result_dict[self.kWeekMk]) + ' 件 登録しました。',
                '＊　１ヶ月後に再実施する問題を ' + str(result_dict[self.kMonthMk]) + ' 件 登録しました。',
                '＊　不正解だった問題を ' + str(result_dict[self.kIncrctMk]) + ' 件 登録しました。',
                '＊　正解だった問題を ' + str(result_dict[self.kCrctMk]) + ' 件 登録しました。',
                '　　計 ' + str(sum) + ' 件 登録しました。'
                                     '--------------------------------------------------------------------------------']
        for msg in msgs:
            self.print_info(msg)

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    # 漢字プリントを作成する。 / Creates a kanji worksheet.
    def create_pdf_kanji_worksheet(self, path):
        """
        :param path: 漢字プリントの保存先 / Destination for the kanji worksheet
        :type path: string

        漢字プリントを作成する。 / Creates a kanji worksheet.
        """
        # 漢字プリントを作成する。 / Create a kanji worksheet.
        draw = KanjiWorkSheet_draw(
            path,
            self.get_student_name(),
            self.get_grade(),
            self.get_create_date(),
            self.get_number_of_problem(),
            self.worksheet[self.kProblem],
            self.kanji_worksheet_idx)

        # PDFを作成する。 / Create the PDF.
        draw.create_pdf_kanji_worksheet()

    # ログファイルから指定した列を取得する。
    # Get a list corresponding to the specified column from the log file.
    def get_column_kanji_worksheet_log(self, path, column_name):
        """
        :param path: Log file
        :type path: string
        :param column_name: 採点結果 / Grading results
        :type column_name: string

        ログファイルから指定した列に該当するリストを取得する。
        Retrieves a list corresponding to the specified column from the log file.
        """
        opn_err_msg = []
        status_list = []

        # ログファイルが存在することを確認する。
        # Verify that the log file exists.
        if os.path.exists(path):
            # ログファイルが存在する場合は、読み込みを行う。
            # If the log file exists, perform the read operation.
            logs = pd.read_csv(
                path,
                sep=',',
                index_col=0,
                encoding='shift-jis'
            )
            self.print_info('ログファイル(' + path + ')ファイルを読み込みました。')

            # 採点結果 / Grading results
            status_list = logs[column_name].values
        else:
            opn_err_msg.append('ログファイル(' + path + ')ファイルを読み込めませんでした。')

        return len(opn_err_msg), opn_err_msg, status_list

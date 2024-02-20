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


class KanjiWorkSheet_prob(KanjiWorkSheet):
    def __init__(self):
        super(KanjiWorkSheet_prob, self).__init__(debug=True)

        # 漢字プリント
        self.kanji_worksheet = pd.DataFrame()  # 漢字プリントのデータを保持するデータフレーム
        self.kanji_worksheet_idx = []          # 漢字プリントに出題する問題集のインデックスのリスト

        self.list_x_idx = []  # 間違えた問題のインデックス
        self.list_a_idx = []  # 出題してからしばらく再出題していない問題のインデックス
        self.list_d_idx = []  # 昨日間違えた問題のインデックス
        self.list_w_idx = []  # 一週間前に間違えた問題のインデックス
        self.list_m_idx = []  # 一ヶ月前に間違えた問題のインデックス
        self.list_n_idx = []  # 未出題のインデックス
        self.list_o_idx = []  # 正解している問題のインデックス

        self.create_date = ''  # 作成日

        self.student_name = ''  # 出題対象者(生徒名)
        self.grade = []         # 出題範囲指定(学年)

        self.kMDRW = 0  # 復習モード
        self.kMDTR = 1  # 練習モード
        self.mode = self.kMDTR  # 出題モード
        self.number_of_problem = 20  # 出題数(デフォルト:20)

        # 漢字マスタの読み込み.
        self.answer_kanji_keyword = []
        # 最後の出題から30日以上経過した漢字の辞書
        self.old_kanji_dict = {}

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
        result = []
        # 学年毎に処理する.
        for grade in self.grade:
            result_dict = self.get_analysis_correct_kanji_by_grade_dict(grade)
            for key, value in result_dict.items():
                if not value:
                    result.append(key)

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
        num = max(num, 0)   # 出題数が0以下の場合は, 0を設定する.
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

    # self.kanji_worksheetの「答え]を分割し、辞書のキーを作成する。
    def get_answer_kanji_keyword(self):
        target_kanji_problem_list = []
        target_kanji_answer = self.worksheet.loc[self.kanji_worksheet_idx, self.kAnswer].values
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
        for statement, idx, i in zip(self.worksheet.loc[self.kanji_worksheet_idx, self.kProblem],
                                     self.kanji_worksheet_idx,
                                     range(self.get_number_of_problem())):
            for word in statement:
                if self.is_kanji(word):
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
        # 毎日同じ時間帯に学習する場合は、昨日間違えた問題を出力することができないため、
        # 2時間オフセットをいれる。
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
            delta = datetime.timedelta(days=days) < (now_time - pd.to_datetime(tmp_list[self.kLastUpdate]))
            tmp_list = tmp_list[delta]

        return tmp_list.index.values

    # 答えが重複している漢字のインデックスを除去する.
    def remove_duplicates_index(self, list_value, exclusion_list):
        return [value for value in list_value if value not in exclusion_list]

    # 答えが重複している漢字の問題を除去する.
    def remove_duplicates_kanji_problem_index(self, kanji_worksheet_idx, duplicate_dict):
        # 例)
        # 雨 [0, 2, 5, 8]
        # 右 [1, 3]
        # 一 [4, 6]
        # 円 [6, 7]

        # [0]: 0を選んだため、2, 5, 8 は除外
        # [1]: 1を選んだため、3は除外
        # [4]: 4を選んだため、6は除外
        # [7]: 6を除外したため、7を選択

        # 答えに同じ漢字が内容に重複しているものを取り除く
        first_idx = []       # 重複を取り除いた結果
        exclusion_list = []  # 除外リスト
        for list_value in duplicate_dict.values():
            list_value = set(list_value)
            list_value = self.remove_duplicates_index(list_value, exclusion_list)

            # 問題の答えが重複している場合は先頭のインデックスだけ取り除く
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
        duplicate = self.remove_duplicates_index(duplicate, first_idx)
        duplicate = sorted(set(duplicate))
        duplicate = kanji_worksheet_idx[duplicate]  # 除外したい問題のインデックスを得る。

        # 漢字の問題が被っていない問題のインデックスを取得する。
        not_duplicate = self.remove_duplicates_index(kanji_worksheet_idx, duplicate)

        return not_duplicate, duplicate

    # 答えの漢字が重複している最終更新日を作成する.
    def create_long_time_no_question_dict(self, ans_list, date_list, days=30):
        date_map = {}

        # この要素数はself.kanji_worksheetのインデックスとは違う.
        # 答えのリストと、その最終更新日を格納する。
        for i, phrase in enumerate(ans_list):
            # 答えの熟語を分解する.
            for char in phrase:
                # Nanでない場合
                if isinstance(date_list[i], str) or ~np.isnan(date_list[i]):
                    idx_date_list = [i, date_list[i]]
                    if char in date_map:
                        # キーが存在するとき.
                        date_map[char].append(idx_date_list)
                    else:
                        # キーが存在しないとき.
                        date_map[char] = [idx_date_list]

        # 各問題の最終更新日の中で、直近のものを選んで辞書に登録する.
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
                        self.print_info('(' + str(key) + ') ' + '経過時間: '+ str(self.create_date - newest_dates_dict[key][1]))

        self.print_info(('合計：' + str(len(old_kanji_dict))))

        return old_kanji_dict

    # 答えの漢字が重複しているインデックスを作成する.
    def create_duplicate_kanji_index_dict(self, ans_list):
        index_map = {}
        result_dict = {}

        # この要素数はself.kanji_worksheetのインデックスとは違う.
        # 答えのリストと、その要素数を格納する。
        for i, phrase in enumerate(ans_list):
            # 答えの熟語を分解する.
            for char in phrase:
                if char in index_map:
                    # キーが存在するとき.
                    index_map[char].append(i)
                else:
                    # キーが存在しないとき.
                    index_map[char] = [i]

        for char, index in index_map.items():
            # インデックスが複数あるもののみ対象とする.
            # 複数ない場合は重複していないため.
            if len(index) > 1:
                result_dict[char] = index

        # 例)
        # 右 [0, 4, 8, 15, 19]
        # 円 [1, 5, 7, 14, 18]
        # 一 [2, 3, 6, 11, 13, 17]
        # 雨 [9, 12]
        # 王 [10, 16, 20]
        # 音 [21, 26]
        # 花 [22, 25]

        # 本当は学年毎に問題を分けてユニークにしたい。
        # この実装で対して問題にならないのであれば、このままとする.
        # 一番上の学年用の漢字以外は重複しても良いことにする。
        # keys_to_keep = self.get_list_kanji_by_grade(max(self.get_grade()))
        # keys_to_remove = [key for key in result_dict.keys() if key not in keys_to_keep]
        # for key in keys_to_remove:
        #     result_dict.pop(key)

        return result_dict

    def remove_duplicates_kanji_problem(self, num, result, sort=False):
        # 最終更新日の古い順にソートしたもの候補にする.
        # 答えが重複している問題を除去することから、指定した問題数を確保するため、全て候補にする.
        kanji_worksheet_idx = self.get_kanji_worksheet_index(result, sort=sort)

        # 答えに重複がある問題についてはなるべく選択しないようにする.
        # 問題集から答えの列を抽出する.
        ans_list = self.kanji_worksheet.loc[kanji_worksheet_idx, self.kAnswer]
        # 答えの漢字が重複しているインデックスを作成する.
        # (漢字をキーにして、値をインデックスにした辞書を作成する.)
        duplicate_dict = self.create_duplicate_kanji_index_dict(ans_list)
        # 重複した問題のインデックスを削除する.
        (list_not_duplicate, list_duplicate) = self.remove_duplicates_kanji_problem_index(kanji_worksheet_idx, duplicate_dict)

        # 重複を削除した問題のインデックスを問題集だけ選出し、シャッフルする.
        kanji_worksheet_idx = list_not_duplicate[0:num]
        np.random.shuffle(kanji_worksheet_idx)

        # 重複箇所を削ることによって、問題数が減ってしまうので、不足してしまった場合は、重複しても良いので選出する。
        for value in list_duplicate:
            kanji_worksheet_idx.append(value)
        # 指定数だけ問題を得られない場合もあるため、それを考慮して出題数を再設定する.
        kanji_worksheet_idx = kanji_worksheet_idx[0:num]

        return kanji_worksheet_idx, len(kanji_worksheet_idx)

    # 選出した問題の最終更新日を更新する.
    def set_lastupdate_kanji_worksheet(self):
        # Excelで読み込んだ時に妙な解釈をされ、形式が壊れてしまうため、シングルクォートで囲っておく.
        now = "'" + str(pd.to_datetime(datetime.datetime.today())) + "'"
        # 選出した問題の最終日を更新する.
        self.worksheet.loc[self.kanji_worksheet_idx, self.kLastUpdate] = now

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
        else:                          # 練習モード
            self.create_train_mode_kanji_worksheet()

        # 問題の答えに含まれている漢字を取得する.
        self.get_answer_kanji_keyword()
        # 問題文に答えが記載されている場合は、その漢字をルビに置き換える.
        self.replace_kanji_with_ruby()
        # 選択中の学年未満のルビを削除する.
        self.remove_unnecessary_ruby()

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # 出題する問題が決まったため、最終更新日を更新する.
        self.kanji_worksheet = self.set_lastupdate_kanji_worksheet()
        # 問題集を抽出した物だけにする.
        self.kanji_worksheet = self.worksheet.loc[self.kanji_worksheet_idx, :]

        return len(err_msg) != 0, err_msg

    # 復習モードの漢字プリントを作成する.
    def create_review_mode_kanji_worksheet(self):
        """復習モードの漢字プリントを作成する."""
        self.print_info("Review Mode")

        # ○になっている問題を出題する.
        # 最終更新日の古い順に並び替えて、その先頭から順に問題を選択する。
        # ただし、答えに重複がある問題については選択しないようにする。
        (list_o, num) = self.remove_duplicates_kanji_problem(self.get_number_of_problem(), self.kCrctMk, sort=True)

        # 一ヶ月経過しても出題していない漢字の問題のインデックスを取得する.
        #self.get_kanji_worksheet_old_index()

        if len(list_o) > 0:
            self.kanji_worksheet_idx = list_o  # 漢字プリントに出題する問題集のインデックスのリストを更新する.
            self.set_number_of_problem(num)    # 出題数を更新する.
        else:
            # 問題を選出できなかったとき、練習モードと同じにする.
            self.create_train_mode_kanji_worksheet()

    # 出題してからしばらく再出題していない漢字の問題のインデックスを取得する.
    def get_kanji_worksheet_old_index(self):
        # 最後の出題から30日以上経過した漢字の辞書を作成.
        #tmp2_df = pd.DataFrame()
        self.old_kanji_dict = self.create_long_time_no_question_dict(
                self.worksheet[self.kAnswer].tolist(),
                self.worksheet[self.kLastUpdate].tolist()
        )
        #print("==================================================================")
        #print(self.old_kanji_dict)

        # 指定した答えの問題を抽出し、シャッフルしてその先頭のインデックスを得る.
        idx_list = []
        for key in self.old_kanji_dict.keys():
            tmp_df_idx = self.get_problem_with_answer(key, self.grade).index.values
            np.random.shuffle(tmp_df_idx)
            idx_list.append(tmp_df_idx[0])

        #print("==================================================================")
        #print(idx_list)
        #print(len(idx_list))
        #print(len(set(sorted(idx_list))))

        #for idx in idx_list:
        #    tmp1_df = pd.DataFrame(self.worksheet.loc[idx, :]).T

        #    if not tmp1_df[self.kGrade].isin([self.grade]).any():
        #        if len(tmp2_df) > 0:
        #            tmp2_df = pd.concat([tmp2_df, tmp1_df], axis=0, ignore_index=False)
        #        else:
        #            tmp2_df = tmp1_df

        # gradeで除いてしまった問題は再び追加する。
        #self.kanji_worksheet = pd.concat([self.kanji_worksheet, tmp2_df])
        #print(tmp2_df.index.values)

        return idx_list  #, tmp2_df #tmp2_df.index.values, tmp2_df

    # 訓練モードの漢字プリントを作成する.
    def create_train_mode_kanji_worksheet(self):
        """訓練モードの漢字プリントを作成する."""
        self.print_info("Train Mode")

        # テスト問題を選定する.
        # 間違えた問題のインデックスを取得する.
        self.list_x_idx = self.get_kanji_worksheet_index(self.kIncrctMk, days=0)
        # 出題してからしばらく再出題していない漢字の問題のインデックスを取得する.
        self.list_a_idx = self.get_kanji_worksheet_old_index()
        # 昨日間違えた問題のインデックスを取得する.
        self.list_d_idx = self.get_kanji_worksheet_index(self.kDayMk, days=1)
        # 一週間前に間違えた問題のインデックスを取得する.
        self.list_w_idx = self.get_kanji_worksheet_index(self.kWeekMk, days=7 - 1)
        # 一ヶ月前に間違えた問題のインデックスを取得する.
        self.list_m_idx = self.get_kanji_worksheet_index(self.kMonthMk, days=7 * 4 - 7)

        # 4つの問題を連結する.
        # 優先順位: 30日以上出題していない問題 ＞ 不正解 ＞ 次の日に出題 ＞ 一週間後に出題 ＞ 一ヶ月後に出題 ＞ 未出題 ＞ 正解
        self.kanji_worksheet_idx = np.concatenate([
                self.list_x_idx,
                self.list_a_idx,
                self.list_d_idx,
                self.list_w_idx,
                self.list_m_idx])

        num = self.get_number_of_problem() - len(self.kanji_worksheet_idx)
        if num <= 0:
            # 間違えた問題で満足した場合
            # 1~20番目の問題のインデックスを作成する.
            self.kanji_worksheet_idx = self.kanji_worksheet_idx[0: self.get_number_of_problem()]
        else:
            # 間違えた問題だけでは不足している場合
            # まだ出題していない問題を抽出する.
            (self.list_n_idx, n_num) = self.remove_duplicates_kanji_problem(num, self.kNotMk, sort=False)
            self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_n_idx[0:n_num]])

            # 未出題だけでは確保できなかった.
            num = num - len(self.list_n_idx[0:n_num])
            if num > 0:
                # 既に出題し、正解している問題を候補に挙げる.
                (self.list_o_idx, _) = self.remove_duplicates_kanji_problem(num, self.kCrctMk, sort=True)
                self.list_o_idx = list(set(self.list_o_idx) - set(self.list_a_idx))
                o_num = len(self.list_o_idx)

                self.kanji_worksheet_idx = np.concatenate([self.kanji_worksheet_idx, self.list_o_idx[0:o_num]])

                # それでも足りない場合は、一日後や一週間後、一ヶ月後に出題する予定の未出題の問題を選択することもできるが、
                # レアケースのため、出題数を削ることで対応する。
                self.set_number_of_problem(len(self.kanji_worksheet_idx))

    # 漢字プリントの出題問題の概要を表示する.
    def report_kanji_worksheet(self):
        """漢字プリントの出題問題の概要を表示する."""
        msg_list = [
            '　　　　　未出題: ',
            '　　　　　　正解: ',
            '　　　　　不正解: ',
            '明日以降に再実施: ',
            '１週間後に再実施: ',
            '１ヶ月後に再実施: '
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

        # ログファイルが存在することを確認する.
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
                new = logs.loc[idx, self.kResult]            # 今回の結果

                # 整合を確認
                # 問題集の問題を挿入したりするとインデックスがずれてしまい、上手く記録できないため、そのポカヨケとしてチェックする.
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
                        if old == self.kIncrctMk:  # x -> d
                            key = self.kDayMk
                        elif old == self.kDayMk:     # d -> w
                            key = self.kWeekMk
                        elif old == self.kWeekMk:    # w -> m
                            key = self.kMonthMk
                        else:                        # m -> o or - -> o
                            key = self.kCrctMk
                    # 今回, 不正解の場合
                    else:                            # x
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

        # ログに反映した数を算出する.
        total = sum(result_dict[key] for key in self.report_key_list)

        if len(logs) != total:
            fmt_err_msg.append(self.print_error('ログファイルの問題数と登録件数が不一致です. '))
            fmt_err_msg.append(self.print_error('結果の記入に間違いがあるか、未記入である可能性があります.'))

        self.print_info('--------------------------------------------------------------------------------')
        self.print_info('＊　明日以降に再実施する問題を ' + str(result_dict[self.kDayMk]) + ' 件 登録しました.')
        self.print_info('＊　１週間後に再実施する問題を ' + str(result_dict[self.kWeekMk]) + ' 件 登録しました.')
        self.print_info('＊　１ヶ月後に再実施する問題を ' + str(result_dict[self.kMonthMk]) + ' 件 登録しました.')
        self.print_info('＊　不正解だった問題を ' + str(result_dict[self.kIncrctMk]) + ' 件 登録しました.')
        self.print_info('＊　正解だった問題を ' + str(result_dict[self.kCrctMk]) + ' 件 登録しました.')
        self.print_info('　　計 ' + str(sum) + ' 件 登録しました.')
        self.print_info('--------------------------------------------------------------------------------')

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
            path,
            self.get_student_name(),
            self.get_grade(),
            self.get_create_date(),
            self.get_number_of_problem(),
            self.worksheet[self.kProblem],
            self.kanji_worksheet_idx)

        # PDFを作成する.
        draw.generate_pdf_kanji_worksheet()

    # ログファイルから指定した列に該当するリストを取得する.
    def get_column_kanji_worksheet_log(self, path, column_name):
        """
        :param path: ログファイル
        :type path: string
        :param column_name: 採点結果
        :type column_name: string

        ログファイルから指定した列に該当するリストを取得する.
        """
        opn_err_msg = []
        status_list = []

        # ログファイルが存在することを確認する.
        if os.path.exists(path):
            # ログファイルが存在する場合は、読み込みを行う.
            logs = pd.read_csv(
                path,
                sep=',',
                index_col=0,
                encoding='shift-jis'
            )
            self.print_info('ログファイル(' + path + ')を読み込みました.')

            # 採点結果
            status_list = logs[column_name].values
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')を読み込めませんでした.'))

        return len(opn_err_msg), opn_err_msg, status_list


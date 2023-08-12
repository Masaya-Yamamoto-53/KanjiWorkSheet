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
                  '学年'
                , '問題文'
                , '答え'
                , '番号'
                , '管理番号'
                , '最終更新日'
                , '結果'
                , '履歴'
                , '結果の履歴'
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
        self.kHistRlt = self.kFileColumns[8]

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

        self.student_name = ''       # 出題対象者(生徒名)
        self.grade = []              # 出題範囲指定(学年)

        self.kMDRW = 0  # 復習モード
        self.kMDTR = 1  # 練習モード
        self.kMDWK = 2  # 苦手モード
        self.mode = self.kMDTR       # 出題モード
        self.number_of_problem = 20  # 出題数(デフォルト:20)

    # ファイル形式をチェックする.
    def check_file_format(self, fmt_err_msg):
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

        return fmt_err_msg

    # 欠損値をチェックする.
    def check_column_nan(self, fmt_err_msg):
        # [学年]、[問題文]、[答え] 列の欠損値を確認.
        for name in [self.kGrade, self.kProblem, self.kAnswer]:
            if self.worksheet[name].isna().any():
                fmt_err_msg.append(self.print_error('[' + name + ']列に空欄があります.'))

        return fmt_err_msg

    # 数値以外をチェックする.
    def check_column_non_numeric(self, fmt_err_msg):
        # [学年] 列に数値以外が入っていないか確認.
        data = pd.to_numeric(self.worksheet[self.kGrade], errors='coerce')
        msg = '[' + str(self.kGrade) + ']列には数値を入れてください.'
        if pd.isna(data).any():
            fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 整数以外をチェックする.
    def check_column_non_integer(self, fmt_err_msg):
        # [学年] 列に整数以外が入っていないか確認.
        data = self.worksheet[self.kGrade]
        msg = '[' + str(self.kGrade) + ']列には数値を入れてください.'
        if (data != np.floor(data)).any():
            fmt_err_msg.append(self.print_error(msg))

        return fmt_err_msg

    # 範囲外の数値をチェックする.
    def check_column_out_of_range(self, fmt_err_msg):
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
        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        worksheet = self.worksheet
        for key in self.report_key_list:
            worksheet = worksheet[worksheet[self.kResult] != key]

        idx = worksheet.index.values
        if len(idx) > 0:
            p_result_pos = self.worksheet.columns.get_loc(self.kResult)
            self.worksheet.iloc[idx, p_result_pos] = self.kNotMk
            self.save_worksheet()

    # 問題文が漢字プリントに収まるか否かを確認する.
    def check_print_fit(self):
        draw = KanjiWorkSheet_draw()
        for problem in self.worksheet[self.kProblem]:
            y_pos = draw.draw_problem_statement(0, problem, 0, chk=True)
            if y_pos > draw.kMaxSize:
                self.print_info(str(y_pos))

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

            except pd.errors.EmptyDataError: # ファイルが空だった場合
                fmt_err_msg.append(self.print_error('問題集が空です.'))

            # ファイル形式をチェックする.
            # 必要な列が順番通りに存在していることを確認する.
            if len(fmt_err_msg) == 0:
                fmt_err_msg = self.check_file_format(fmt_err_msg)

            if len(fmt_err_msg) == 0:
                # [学年]、[問題文]、[答え] 列の欠損値を確認.
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

        # ファイルが存在しない.
        else:
            # データを初期化し, エラーメッセージを出力する.
            self.worksheet = pd.DataFrame()
            opn_err_msg.append(self.print_error('問題集が存在しません.'))

        # 結果がself.report_key_list以外の場合は、self.kNotMkに置き換える。
        self.replace_undef_char_with_NotMk()

        # 問題文が漢字プリントに収まるか否かを確認する.
        self.check_print_fit()

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
        num = max(num,  0)  # 出題数が0以下の場合は, 0を設定する.
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

        # 作成日を更新する.
        self.create_date = pd.to_datetime(datetime.datetime.today())

        if   self.mode == self.kMDRW:
            self.create_review_kanji_worksheet()
        elif self.mode == self.kMDWK:
            self.create_weakness_kanji_worksheet()
        else:
            self.create_train_kanji_worksheet()

        return len(err_msg) != 0, err_msg

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

    # 復習モードの問題集を作成する.
    def create_review_kanji_worksheet(self):
        """復習モードの問題集を作成する."""
        self.print_info("Review Mode")

        # 既に出題し、正解している問題を候補に挙げる.
        num = self.get_number_of_problem()
        self.kanji_worksheet_idx = self.get_kanji_worksheet_index(self.kCrctMk, sort=True)[0:num]

        # 指定数だけ問題を得られない場合もあるため、それを考慮して出題数を再設定する.
        self.set_number_of_problem(len(self.kanji_worksheet_idx))

        # 出題する問題が決まったため、最終更新日を更新する.
        self.kanji_worksheet = self.set_lastupdate_kanji_worksheet()

    # 訓練モードの問題集を作成する.
    def create_train_kanji_worksheet(self):
        """訓練モードの問題集を作成する."""
        self.print_info("Train Mode")

        # テスト問題を選定する
        # 間違えた問題のインデックスを取得する.
        self.list_x_idx = self.get_kanji_worksheet_index(self.kIncrctMk, days=0)
        # 昨日間違えた問題のインデックスを取得する.
        self.list_d_idx = self.get_kanji_worksheet_index(self.kDayMk, days=1)
        # 一週間前に間違えた問題のインデックスを取得する.
        self.list_w_idx = self.get_kanji_worksheet_index(self.kWeekMk, days=7-1)
        # 一ヶ月前に間違えた問題のインデックスを取得する.
        self.list_m_idx = self.get_kanji_worksheet_index(self.kMonthMk, days=7*4-7)

        # まだ出題していない問題を抽出する.

        self.list_n_idx = self.get_kanji_worksheet_index(self.kNotMk)
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

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # 出題する問題が決まったため、最終更新日を更新する.
        self.kanji_worksheet = self.set_lastupdate_kanji_worksheet()

    # 苦手モードの問題集を作成する.
    def create_weakness_kanji_worksheet(self):
        """苦手モードの問題集を作成する."""
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

        # ランダムに並び替える.
        np.random.shuffle(self.kanji_worksheet_idx)
        # 出題する問題が決まったため、最終更新日を更新する.
        self.kanji_worksheet = self.set_lastupdate_kanji_worksheet()

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
            logs = pd.read_csv(path , sep=',' , index_col=0 , encoding='shift-jis')
            self.print_info('ログファイル(' + path + ')を読み込みました.')
        # ファイルが存在しない.
        else:
            opn_err_msg.append(self.print_info('ログファイル(' + path + ')が読み込みませんでした.'))
            opn_err_msg.append(self.print_info('問題集にテスト結果を反映することができませんでした.'))
            opn_err_msg.append(self.print_info('テストの履歴を反映しない状態で問題を作成します.'))
            return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

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
                    else:                        # m -> o or - -> o
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

                # ステータスの履歴を更新する.
                hist_pos = self.worksheet.columns.get_loc(self.kHistRlt)
                hist = self.worksheet.iloc[p_i, hist_pos]
                if pd.isna(hist):
                    hist = "'-"
                else:
                    hist = str(hist) + old
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

        return len(opn_err_msg) != 0, opn_err_msg, len(fmt_err_msg) != 0, fmt_err_msg

    # 漢字プリントから指定したステータスに該当する問題数を取得する.
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

    # 問題集から指定したステータスに該当する問題数を取得する.
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

    # 問題集から指定した学年の問題数を取得する.
    def get_number_of_problem_with_grade(self, grade):
        """
        :param grade: 学年
        :type grade: list

        問題集から指定した学年の問題の総数を取得する.
        """
        return len(self.worksheet[self.worksheet[self.kGrade].isin(grade)])

    # 漢字プリントを作成する.
    def print_kanji_worksheet(self, path):
        """
        :param path: 漢字プリントの保存先
        :type path: string

        漢字プリントを作成する.
        """
        draw = KanjiWorkSheet_draw()
        draw.set_page(path)
        draw.set_student_name(self.student_name)
        draw.set_grade(self.grade)
        draw.set_create_date(self.create_date)
        draw.set_number_of_problem(self.number_of_problem)
        draw.set_problem(self.kanji_worksheet[self.kProblem])
        draw.set_problem_idx(self.kanji_worksheet_idx)

        # 漢字プリント作成
        draw.create_kanji_worksheet()

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

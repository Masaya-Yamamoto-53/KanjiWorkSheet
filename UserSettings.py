# UserSettings.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import pandas as pd


class UserSettings:
    def __init__(self):
        self.kStudentName = 'Name'
        self.kProblemPath = 'Path'
        self.kNumber = 'Number'
        self.kMaxNumber = 20
        self.kJS1 = u'小学一年生'
        self.kJS2 = u'小学二年生'
        self.kJS3 = u'小学三年生'
        self.kJS4 = u'小学四年生'
        self.kJS5 = u'小学五年生'
        self.kJS6 = u'小学六年生'
        self.kGradeKeyList = [
            self.kJS1,
            self.kJS2,
            self.kJS3,
            self.kJS4,
            self.kJS5,
            self.kJS6
        ]
        self.kMode = u'出題形式'
        self.kReview_Mode = 0    # 復習モード / Review mode
        self.kTraining_Mode = 1  # 練習モード / Training mode

        self.kModeValueList = [
            self.kReview_Mode,
            self.kTraining_Mode
        ]

        # 設定ファイル
        self.path_of_setting_file = r'./.setting'
        self.setting_data = pd.DataFrame()

        # 設定ファイルの項目
        self.setting_columns = [
            self.kStudentName,
            self.kProblemPath,
            self.kNumber,
            self.kJS1,
            self.kJS2,
            self.kJS3,
            self.kJS4,
            self.kJS5,
            self.kJS6,
            self.kMode
        ]
        # エンコーディング
        self.encoding = u'shift-jis'

    # 設定ファイルを読み込む.
    def load_setting_file(self):
        # 設定ファイルを読み込む.
        try:
            # .setting ファイルを開く.
            self.setting_data = pd.read_csv(
                self.path_of_setting_file,
                sep=',',
                encoding=self.encoding
            )
        # .setting ファイルがない場合は新規作成する.
        except FileNotFoundError:
            # 空の .setting ファイルを新規作成
            self.setting_data = pd.DataFrame(columns=self.setting_columns)
            # 空の .setting ファイルを設定ファイルを保存する.
            self.save_setting_file()

    # 設定ファイルを書き込む.
    def save_setting_file(self):
        wrt_err_msg = []

        # 設定ファイルを書き込む.
        try:
            self.setting_data.to_csv(
                self.path_of_setting_file,
                sep=',',
                index=False,
                encoding=self.encoding
            )
        # 設定ファイルを開くなど, 書き込みができない.
        except PermissionError:
            msg = u'問題集(' + self.path_of_setting_file + ')を閉じてください. 更新できません.'
            wrt_err_msg.append(msg)

        return len(wrt_err_msg) != 0, wrt_err_msg

    # 生徒を設定ファイルに登録する.
    def register_student(self, name):
        pd_data = pd.DataFrame({
            self.kStudentName: [name],
            self.kProblemPath: [''],
            self.kNumber: [self.kMaxNumber],
            self.kJS1: [False],
            self.kJS2: [False],
            self.kJS3: [False],
            self.kJS4: [False],
            self.kJS5: [False],
            self.kJS6: [False],
            self.kMode: [self.kTraining_Mode]
        })
        # 設定ファイルにデータを結合し, インデックスを更新する.
        self.setting_data = pd.concat([self.setting_data, pd_data], axis=0)
        self.setting_data = self.setting_data.reset_index(drop=True)
        # 設定ファイルに保存する.
        self.save_setting_file()

    def delete_student(self, name):
        # 設定ファイルの該当データを削除する.
        i = self.setting_data[self.setting_data[self.kStudentName] == name].index[0]
        self.setting_data = self.setting_data.drop(i)
        self.setting_data = self.setting_data.reset_index(drop=True)

    # 生徒の一覧を取得する.
    def get_student_name_list(self):
        return self.setting_data[self.kStudentName].values.tolist()

    # 生徒が登録済みか否かを確認する.
    def chk_registered_student(self, name):
        if name in self.setting_data[self.kStudentName].values:
            return True
        else:
            return False

    # 設定の行を取得する.
    def get_setting_num(self):
        return len(self.setting_data)

    # 問題集のパスを設定する.
    def set_path_of_problem(self, name, path):
        self.setting_data.at[self.get_index(name), self.kProblemPath] = path

    # 問題集のパスを取得する.
    def get_path_of_problem(self, name):
        path = str(self.setting_data.at[self.get_index(name), self.kProblemPath])
        # Nanの場合は空欄にする.
        if path == 'nan':
            path = ''
        return path

    # 出題数を設定する.
    def set_number_of_problem(self, name, num):
        self.setting_data.at[self.get_index(name), self.kNumber] = num

    # 出題数を取得する.
    def get_number_of_problem(self, name):
        return self.setting_data.at[self.get_index(name), self.kNumber]

    # 学年の設定値を設定する.
    def set_grade_value(self, name, grade_key, value):
        self.setting_data.at[self.get_index(name), grade_key] = value

    # 学年の設定値を取得する.
    def get_grade_value(self, name, grade_key):
        return self.setting_data.at[self.get_index(name), grade_key]

    # 学年の列からTrueになっているものをリストに格納する.
    # 例) '小学一年生' '小学二年生' '小学三年生' '小学四年生' '小学五年生' '小学六年生'
    #     True       True       False      True       False       True
    # grade_list = [1, 2, 4, 6]
    def get_grade_list(self, name):
        grade_list = []
        grade = 1
        for key in self.kGradeKeyList:
            if self.setting_data.at[self.get_index(name), key]:
                grade_list.append(grade)
            grade += 1

        return grade_list

    # 出題形式を設定する.
    def set_mode(self, name, mode):
        self.setting_data.at[self.get_index(name), self.kMode] = mode

    # 出題形式を取得する.
    def get_mode(self, name):
        return self.setting_data.at[self.get_index(name), self.kMode]

    # UserSettingsの該当データのインデックスを取得する.
    def get_index(self, name):
        return self.setting_data[self.setting_data[self.kStudentName] == name].index[0]

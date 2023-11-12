# UserSettings.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import pandas as pd

class UserSettings:
    ########################################################################################
    def __init__(self):
        self.kStudentName = 'Name'

        self.kProblemPath = 'Path'

        self.kNumber = 'Number'
        self.kMaxNumber = 20

        self.kJS1 = '小学一年生'
        self.kJS2 = '小学二年生'
        self.kJS3 = '小学三年生'
        self.kJS4 = '小学四年生'
        self.kJS5 = '小学五年生'
        self.kJS6 = '小学六年生'
        self.kGradeKeyList = [
              self.kJS1
            , self.kJS2
            , self.kJS3
            , self.kJS4
            , self.kJS5
            , self.kJS6
        ]

        self.kMode = '出題形式'
        self.kModeReview = 0  # 復習モード
        self.kModeTrain = 1  # 練習モード
        self.kModeWeak = 2  # 苦手モード
        self.kModeKeyList = [
              self.kModeReview
            , self.kModeTrain
            , self.kModeWeak
        ]

        # 設定ファイル
        self.path_of_setting_file = './.setting'
        self.setting_data = pd.DataFrame()

        # 設定ファイルの項目
        self.setting_columns = [
              self.kStudentName
            , self.kProblemPath
            , self.kNumber
            , self.kJS1
            , self.kJS2
            , self.kJS3
            , self.kJS4
            , self.kJS5
            , self.kJS6
            , self.kMode
        ]

        # エンコーディング
        self.encoding = 'shift-jis'

    ########################################################################################
    # 設定ファイルを読み込む.
    def load_setting_file(self):
        # 設定ファイルを読み込む.
        try:
            # .setting ファイルを開く.
            self.setting_data = pd.read_csv(
                  self.path_of_setting_file
                , sep=','
                , encoding=self.encoding
            )
        # .setting ファイルがない場合は新規作成する.
        except FileNotFoundError:
            # 空の .setting ファイルを新規作成
            self.setting_data = pd.DataFrame(columns=self.setting_columns)
            # 空の .setting ファイルを設定ファイルを保存する.
            self.save_setting_file()

    ########################################################################################
    # 設定ファイルを書き込む.
    def save_setting_file(self):
        wrt_err_msg = []

        # 設定ファイルを書き込む.
        print(self.setting_data)
        try:
            self.setting_data.to_csv(
                  self.path_of_setting_file
                , sep=','
                , index=False
                , encoding=self.encoding
            )
        # 設定ファイルを開くなどして, 書き込みができない.
        except PermissionError:
            msg = '問題集(' + self.path_of_setting_file + ')を閉じてください. 更新できません.'
            wrt_err_msg.append(msg)

        return len(wrt_err_msg) != 0, wrt_err_msg

    ########################################################################################
    # 生徒を設定ファイルに登録する.
    def register_student(self, name):
        pd_data = pd.DataFrame({
              self.kStudentName: [name]
            , self.kProblemPath: ['']
            , self.kNumber: [self.kMaxNumber]
            , self.kJS1: [False]
            , self.kJS2: [False]
            , self.kJS3: [False]
            , self.kJS4: [False]
            , self.kJS5: [False]
            , self.kJS6: [False]
            , self.kMode: [self.kModeTrain]
        })
        # 設定ファイルにデータを結合し, インデックスを更新する.
        self.setting_data = pd.concat([self.setting_data, pd_data], axis=0)
        self.setting_data = self.setting_data.reset_index(drop=True)

        # 設定ファイルに保存する.
        self.save_setting_file()

    ########################################################################################
    # 生徒の一覧を取得する.
    def get_student_name_list(self):
        return self.setting_data[self.kStudentName].values.tolist()

    ########################################################################################
    # 生徒が登録済みか否かを確認する.
    def chk_registered_student(self, name):
        if name in self.setting_data[self.kStudentName]:
            return True
        else:
            return False

    ########################################################################################
    # 設定の行を取得する.
    def get_setting_num(self):
        return len(self.setting_data)

    ########################################################################################
    # 問題集のパスを設定する.
    def set_path_of_problem(self, name, path):
        i = self.setting_data[self.setting_data[self.kStudentName] == name].index[0]
        self.setting_data.iloc[i, self.setting_data.columns.get_loc(self.kProblemPath)] = path

    ########################################################################################
    # 問題集のパスを取得する.
    def get_path_of_problem(self, name):
        path = str(self.setting_data[self.setting_data[self.kStudentName] == name][self.kProblemPath].values[0])
        # Nanの場合は空欄にする.
        if path == 'nan':
            path = ''
        return path

    ########################################################################################
    # 出題数を設定する.
    def set_number_of_problem(self, name, num):
        i = self.setting_data[self.setting_data[self.kStudentName] == name].index[0]
        self.setting_data.iloc[i, self.setting_data.columns.get_loc(self.kNumber)] = num

    ########################################################################################
    # 出題数を取得する.
    def get_number_of_problem(self, name):
        print(name)
        num = self.setting_data[self.setting_data[self.kStudentName] == name][self.kNumber].values[0]
        print(num)
        return num

    ########################################################################################
    # 学年の設定値を設定する.
    def set_grade_value(self, name, grade_key, value):
        i = self.setting_data[self.setting_data[self.kStudentName] == name].index[0]
        self.setting_data.iloc[i, self.setting_data.columns.get_loc(grade_key)] = value

    ########################################################################################
    # 学年の設定値を取得する.
    def get_grade_value(self, name, grade_key):
        return self.setting_data[self.setting_data[self.kStudentName] == name][grade_key].values[0]

    ########################################################################################
    # 出題形式を設定する.
    def set_mode(self, name, mode):
        i = self.setting_data[self.setting_data[self.kStudentName] == name].index[0]
        self.setting_data.iloc[i, self.setting_data.columns.get_loc(self.kMode)] = mode

    ########################################################################################
    # 出題形式を取得する.
    def get_mode(self, name):
        return self.setting_data[self.setting_data[self.kStudentName] == name][self.kMode].values[0]

# CreateFilePath.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os

class CreateFilePath:
    def __init__(self, wg_select_student, wg_select_mode):
        self.WidgetSelectStudent = wg_select_student
        self.WidgetSelectMode = wg_select_mode

    # 漢字プリントのパスを取得する.
    def get_path_of_kanji_worksheet(self):
        name_t = self.WidgetSelectStudent.get_selected_student_name()
        name = ''
        # 苗字と名前の間にスペースがある場合はアンダーバーに変換する.
        for word in list(name_t):
            if word == u' ' or word == u'　':
                name += '_'
            else:
                name += word

        mode = self.WidgetSelectMode.get_selected_student_mode()
        mode_str = self.WidgetSelectMode.kModeKeyList[mode]
        return './' + name + '_漢字テスト_' + mode_str + 'モード' + '.pdf'

    # ログファイルのパスを取得する.
    def get_path_of_log(self):
        name = self.WidgetSelectStudent.get_selected_student_name()

        logdir = './result/'
        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        mode = self.WidgetSelectMode.get_selected_student_mode()

        return logdir + '.' + name + str(mode) + '.log'

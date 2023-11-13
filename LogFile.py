# LogFile.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

import os

class LogFile:
    def __init__(self, wg_select_student, wg_select_mode):
        self.WidgetSelectStudent = wg_select_student
        self.WidgetSelectMode = wg_select_mode

    # ログファイルのパスを取得する.
    def get_path_of_log(self):
        name = self.WidgetSelectStudent.get_selected_student_name()

        logdir = './result/'
        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        mode = self.WidgetSelectMode.get_selected_student_mode()

        return logdir + '.' + name + str(mode) + '.log'

# DebugPrint.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

class DebugPrint:
    def __init__(self, debug):
        self.kDebug = debug

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
# main.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import platform
import ctypes
from KanjiWorkSheet_gui import KanjiWorkSheet_gui
from Student import Student

if __name__ == '__main__':
    # 暫定対策
    if platform.system() == 'Windows':
        try:
            # ディスプレイの拡大/縮小が100%以外に設定されている場合、
            # DPI認識モードが未設定のため、文字が荒くなる。
            ctypes.windll.shcore.SetProcessDpiAwareness(True)
        except (AttributeError, ctypes.WinError):
            pass

    # 漢字プリント作成アプリの起動
    KanjiWorkSheet = KanjiWorkSheet_gui()

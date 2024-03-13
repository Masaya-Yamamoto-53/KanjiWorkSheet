# KanjiWorkSheet_draw.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)
import math

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4, landscape


# 文字が漢字であるか否かを評価する.
def is_kanji(char):
    return '\u4e00' <= char <= '\u9faf'


class KanjiWorkSheet_draw:
    def __init__(self, path, name, grade, date, num, problem, problem_idx):
        self.page = canvas.Canvas(path, pagesize=landscape(A4))  # PDF設定

        self.student_name = name  # 生徒名
        self.grade = grade  # 学年
        self.create_date = date  # 作成日
        self.number_of_problem = num  # 問題数
        self.kanji_problem = problem  # 問題文
        self.kanji_problem_idx = problem_idx  # 問題文の要素番号

        # フォント選択
        self.kFontPath = r'C:\Windows\Fonts\msmincho.ttc'
        self.kFont = 'msmincho'
        pdfmetrics.registerFont(TTFont(self.kFont, self.kFontPath))  # フォント選択

        # PDF設定値
        self.kProbFontSize  = 17  # 問題文のフォントサイズ
        self.kProbFrameSize = 10  # 問題枠のサイズ

        # 問題文のサイズ上限値
        self.kMaxSize = 244.5

        # 問題文の記載位置を定義
        self.kTopPos = 560  # 上の行の開始位置
        self.kBtmPos = 270  # 下の行の開始位置

        # 上下の問題数を定義
        self.kProbTopNum = 0
        self.kProbBtmNum = 0

        # 列の問題数の下限
        self.kColNumMin = 10

        # 問題番号の下にオフセットする
        self.kProblemStartOffset = 20  # 問題文の開始位置

        # 問題の枠のサイズ
        self.rect_size = 48

        self.problem_start_pos = 650  # 問題枠の開始位置
        self.problem_text_frame = []  # 問題枠

    def create_pdf_kanji_worksheet(self):
        """漢字プリントを作成する."""
        # 出題数を上下に分割し、出題する。
        # 分割した時、10未満であれば、記載の間隔を10にする。
        # 問題数が10以下の場合、10問にした方が見栄えが良いため.
        num = self.number_of_problem
        if num < self.kColNumMin:
            self.kProbTopNum = num
            self.kProbBtmNum = 0
        else:
            num = math.ceil(self.number_of_problem / 2)
            num = max(num, self.kColNumMin)

            self.kProbTopNum = num
            self.kProbBtmNum = self.number_of_problem - num
            if self.kProbBtmNum < 0:
                self.kProbBtmNum = 0

        # 列ごとの印字位置を演算する.
        # 問題ごとに印字する位置を決めたいため.
        for i in range(0, num):
            pos = self.problem_start_pos - self.problem_start_pos / max(self.kProbTopNum, self.kColNumMin) * i
            self.problem_text_frame.append(pos)

        # 漢字の問題を出力（上段）
        for i in range(0, self.kProbTopNum):
            self.draw_problem_statement(
                  # self.kTopPosには各問題の番号①～⑩が印字されているため、オフセットする.
                  self.kTopPos - self.kProblemStartOffset
                , self.kanji_problem[self.kanji_problem_idx[i]]
                , i
            )

        # 漢字の問題を出力（下段）
        for i in range(self.kProbTopNum, self.number_of_problem):
            self.draw_problem_statement(
                  # self.kBtmPosには各問題の番号⑪～⑳が印字されているため、オフセットする.
                  self.kBtmPos - self.kProblemStartOffset
                , self.kanji_problem[self.kanji_problem_idx[i]]
                , i - self.kProbTopNum
            )

        # 漢字プリントのタイトルを記述する.
        self.draw_problem_statement_title(775, 525, 30)
        # 名前を記述する.
        self.draw_name(770, 300, 15)
        self.draw_student_name(777.5, 240, 25)
        # 問を記述する.
        self.draw_problem(720, 550, 12)
        # 漢字プリントの出題番号を記述する.
        self.draw_problem_number()
        # 漢字プリントの中央に線を記述する.
        self.draw_center_line()
        # PDFを保存する.
        self.page.save()

    # 漢字プリントのタイトルを記述する.
    def draw_problem_statement_title(self, x_pos, y_pos, font_size):
        """漢字プリントのタイトルを記述する."""
        self.draw_string(x_pos, y_pos, font_size, u'かんじプリント')

    # 名前欄を記述する.
    def draw_name(self, x_pos, y_pos, font_size):
        """名前欄を記述する."""
        # 枠（名前）
        self.page.setStrokeColor('black')
        self.page.setLineWidth(1)
        self.page.setDash([])
        self.page.rect(x_pos - 10, y_pos - 5, 60, height=20, fill=True)

        self.page.setFont(self.kFont, font_size)
        self.page.setFillColorRGB(255, 255, 255)
        self.page.drawString(x_pos - font_size / 3 / 2, y_pos, u'なまえ')
        self.page.setFillColorRGB(0, 0, 0)

        # 枠（欄）
        self.page.setStrokeColor('black')
        self.page.setLineWidth(1)
        self.page.setDash([])
        self.page.rect(x_pos - 10, y_pos - 205, 60, 200, fill=False)

        # 枠（日付）
        self.page.setStrokeColor('black')
        self.page.setLineWidth(1)
        self.page.setDash([])
        self.page.rect(x_pos - 10, y_pos - 245, 60, 40, fill=False)

        # 日付：月
        x_pos_tmp = x_pos + 4
        for month in str(self.create_date.month)[::-1]:
            self.page.drawString(x_pos_tmp, y_pos - 240, month)  # 月
            x_pos_tmp -= 7

        # 日付：日
        x_pos_tmp = x_pos + 29
        for day in str(self.create_date.day)[::-1]:
            self.page.drawString(x_pos_tmp, y_pos - 240, day)  # 日
            x_pos_tmp -= 7

        self.page.drawString(x_pos + 15, y_pos - 240, u'/')

    # 生徒の名前を記述する.
    def draw_student_name(self, x_pos, y_pos, font_size):
        """生徒の名前を記述する."""
        self.draw_string(x_pos, y_pos, font_size, self.student_name)

    # 問を記述する.
    def draw_problem(self, x_pos, y_pos, font_size):
        """問を記述する."""
        # 問をPDFに印字する。
        str_arr = u'つぎの □に かんじ を かきましょう。'
        self.draw_string(x_pos, y_pos, font_size, str_arr)

    # 漢字プリントの出題番号を記述する.
    def draw_problem_number(self):
        """漢字プリントの出題番号を記述する."""
        num = u'①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
        self.page.setFont(self.kFont, self.kProbFontSize)

        # 上の行の番号を印字
        for i in range(0, self.kProbTopNum):
            self.page.drawString(self.problem_text_frame[i], self.kTopPos, num[i])

        # 下の行の番号を印字
        for i in range(0, self.kProbBtmNum):
            self.page.drawString(self.problem_text_frame[i], self.kBtmPos, num[i + self.kProbTopNum])

    # 漢字プリントの中央に線を記述する.
    def draw_center_line(self):
        """漢字プリントの中央に線を記述する."""
        self.page.setStrokeColor('gray')
        self.page.setLineWidth(1)
        self.page.setDash([4])
        self.page.line(50, 300, 700, 300)

    # 問題文を記述する.
    def draw_problem_statement(self, y_pos_const, problem, idx, chk=False):
        """問題文を記述する."""
        kFrameSttInit  = 0
        kFrameSttStart = 1  # 問題枠の開始
        kFrameSttEnd   = 2  # 問題枠の終了
        frame_stt = kFrameSttInit

        kRubySttEnd   = 0
        kRubySttStart = 1
        ruby_stt = kRubySttEnd

        fflg = 0
        arr = []
        kanji = ""
        y_pos = y_pos_const
        frame_num = 0

        count = 0
        for word in problem:
            # 問題枠を印字する。
            if frame_stt == kFrameSttStart:
                # []の内容を格納し終えた。
                if word == u']':
                    # 問題枠が初回の場合
                    if fflg == 0:
                        y_pos = y_pos - self.rect_size / 10 * 0.5
                        fflg = 1
                    if not chk:
                        if len(arr) <= 0:
                            self.draw_frame(self.problem_text_frame[idx] - self.rect_size / 3, y_pos, self.rect_size, 0, arr)
                            frame_num += 1
                        else:
                            self.draw_frame(self.problem_text_frame[idx] - self.rect_size / 3, y_pos, self.rect_size, frame_num,
                                            arr)
                            frame_num = 0
                    frame_stt = kFrameSttEnd
                    arr = []
                else:
                    arr.append(word)  # 問題の文字列をarrに格納する。
            # ルビを印字する。
            elif ruby_stt == kRubySttStart:
                # <>の内容を格納し終えた。
                if word == u'>':
                    if not chk:
                        self.draw_ruby(self.problem_text_frame[idx], y_pos, kanji, arr)
                    ruby_stt = kRubySttEnd
                    arr = []
                    kanji = ""
                else:
                    arr.append(word)  # ルビの文字列をarrに格納する。
            # 問題枠の開始
            elif word == u'[':
                # 問題枠を印字した直後の場合は位置を調整する。
                if frame_stt == kFrameSttEnd:
                    y_pos = y_pos - self.rect_size
                frame_stt = kFrameSttStart  # 問題枠の開始
            # ルビの開始
            elif word == u'<':
                ruby_stt = kRubySttStart  # ルビの開始
            # 問題文を印字する。
            else:
                # 問題枠、ルビの開始、終了でない場合
                font_size = self.kProbFontSize
                # 問題枠を印字した直後の場合は位置を調整する。
                if frame_stt == kFrameSttEnd:
                    y_pos = y_pos - font_size - self.rect_size / 10 * 8
                    frame_stt = kFrameSttInit
                if not chk:
                    y_pos = self.draw_string(self.problem_text_frame[idx], y_pos, font_size, word)

                if is_kanji(word):
                    kanji = kanji + word
                else:
                    kanji = ""

            count += 1

        return y_pos_const - y_pos

    def draw_string(self, x_pos, y_pos, font_size, str_arr):
        """文を書く"""
        self.page.setFont(self.kFont, font_size)
        for word in str_arr:
            # 句読点の場合
            if word == u'。' or word == u'、':
                self.page.drawString(x_pos + (font_size / 3) * 2, y_pos + font_size / 1.5, word)
                y_pos = y_pos - font_size
            # 拗音の場合
            elif word == u'ゃ' or word == u'ゅ' or word == u'ょ' or word == u'っ' \
              or word == u'ャ' or word == u'ュ' or word == u'ョ' or word == u'ッ':
                # 拗音のサイズを指定する.
                #self.page.setFont(self.kFont, font_size / 10 * 8)
                self.page.setFont(self.kFont, font_size * 0.8)
                self.page.drawString(x_pos + (font_size / 3), y_pos + font_size / 3, word)
                # 文字のサイズを元に戻す.
                self.page.setFont(self.kFont, font_size)
                #y_pos = y_pos - font_size / 10 * 8
                y_pos = y_pos - font_size * 0.8
            # スペースの場合
            elif word == u' ' or word == u'　':
                self.page.drawString(x_pos, y_pos, word)
                y_pos = y_pos - font_size / 3
            # 長音符の場合
            elif word == u'ー' or word == u'「' or word == u'」':
                # 用紙を-90度回転し、長音符を印字する.
                self.page.rotate(-90)
                self.page.drawString(-1 * y_pos - font_size + font_size / 8, x_pos + font_size / 8, word)
                # 用紙を90度回転し、基に戻す.
                self.page.rotate(90)
                y_pos = y_pos - font_size
            else:
                self.page.drawString(x_pos, y_pos, word)
                y_pos = y_pos - font_size

        return y_pos

    def draw_ruby(self, x_pos, y_pos, kanji, string=u''):
        """漢字プリントの出題の漢字にルビを書く."""
        # 直前の漢字の右隣にルビを振るため, 1文字分だけ移動する.
        x_pos = x_pos + self.kProbFontSize

        # 直前の漢字にルビを振るため, 文字分だけ移動する.
        if len(kanji) == 1:
            y_pos = y_pos + self.kProbFontSize
        elif len(kanji) == 2:
            y_pos = y_pos + self.kProbFontSize * 1.5
        elif len(kanji) == 3:
            y_pos = y_pos + self.kProbFontSize * 2.0
        else:
            y_pos = y_pos + self.kProbFontSize * 2.5

        # ルビの文字サイズを問題文の 1/3 にする.
        font_size = self.kProbFontSize / 3
        self.page.setFont(self.kFont, font_size)

        # ルビの文字数によって, 縦軸の描写位置を変更する.
        if len(string) == 1:
            y_start_offset = self.kProbFontSize / 4  # ルビ描写開始オフセット(文字数によって開始位置をずらす)
            y_pos_offset = self.kProbFontSize / 4  # ルビが 1文字 のとき
        elif len(string) == 2:
            y_start_offset = self.kProbFontSize / 2  # ルビ描写開始オフセット(文字数によって開始位置をずらす)
            y_pos_offset = self.kProbFontSize / 2  # ルビが 2文字 のとき
        elif len(string) == 3:
            y_start_offset = self.kProbFontSize / 6 * 3  # ルビ描写開始オフセット(文字数によって開始位置をずらす)
            y_pos_offset = self.kProbFontSize / 3  # ルビが 3文字 のとき
        else:
            y_start_offset = self.kProbFontSize / 4 * 3  # ルビ描写開始オフセット(文字数によって開始位置をずらす)
            y_pos_offset = self.kProbFontSize / 3  # ルビが 4文字 以外のとき

        if len(kanji) == 1:
            y_start_offset = y_start_offset
            y_pos_offset = y_pos_offset
        elif len(kanji) == 2:
            y_start_offset = y_start_offset * 1.3
            y_pos_offset = y_pos_offset * 1.3
        elif len(kanji) == 3:
            y_start_offset = y_start_offset * 1.6
            y_pos_offset = y_pos_offset * 1.6

        # ルビを記述する.
        for word in string:
            self.draw_string(x_pos, y_pos + y_start_offset, font_size, word)
            y_pos -= y_pos_offset

    # 漢字プリントの問題文の枠を書く.
    def draw_frame(self, x_pos, y_pos, size, frame_num=0, string=u''):
        """漢字プリントの問題文の枠を書く."""
        rect_width = size
        rect_height = size

        y_pos -= (size + self.kProbFontSize) / 1.8

        # 枠内を点線で十字の線を記述する.
        self.page.setLineWidth(0.8)
        self.page.setStrokeColor('silver')
        self.page.setDash([2])
        self.page.line(x_pos + (rect_width / 2), y_pos, x_pos + (rect_width / 2), y_pos + rect_height)  # 縦
        self.page.line(x_pos, y_pos + (rect_height / 2), x_pos + rect_width, y_pos + (rect_height / 2))  # 横

        # 枠
        self.page.setStrokeColor('gray')
        #self.page.setStrokeColor('black')
        self.page.setLineWidth(1)
        self.page.setDash([])
        self.page.rect(x_pos, y_pos, rect_width, rect_height, fill=False)

        # フリガナの文字数によって、間隔を空ける.
        if len(string) == 1:  # 文字数が1の場合
            y_bias = 1 * (frame_num + 1)
            start_pos_bias = 2
        elif len(string) == 2:  # 文字数が2の場合
            y_bias = 2 * (frame_num + 1)
            start_pos_bias = 1
        elif len(string) == 3:  # 文字数が3の場合
            y_bias = 1.5 * (frame_num + 1)
            start_pos_bias = 0.5
        elif len(string) == 4:  # 文字数が4の場合
            y_bias = 1 * (frame_num + 1)
            start_pos_bias = 0.5
        else:
            y_bias = 1 * (frame_num + 1)
            start_pos_bias = 0.1

        if frame_num > 0:
            if len(string) == 1:  # 文字数が1の場合
                y_pos = y_pos + (rect_height * frame_num) * 0.5
            elif len(string) == 2:  # 文字数が2の場合
                y_pos = y_pos + (rect_height * frame_num) * 0.75
            elif len(string) == 3:  # 文字数が3の場合
                y_pos = y_pos + (rect_height * frame_num) * 0.75
            elif len(string) == 4:  # 文字数が4の場合
                y_pos = y_pos + (rect_height * frame_num) * 0.75
            elif len(string) == 5:  # 文字数が4の場合
                y_pos = y_pos + (rect_height * frame_num) * 0.90
            else:
                y_pos = y_pos + rect_height

        x_space = 2  # 枠にピッタリ付かないように少し間を空ける.
        next_print_pos = 0
        for word in string:
            if word == u'ゃ' or word == u'ゅ' or word == u'ょ' or word == u'っ':
                # 拗音(contracted sound)のオフセット
                cs_x_offset = self.kProbFrameSize / 10 * 3
                cs_y_offset = 5
                font_size = self.kProbFrameSize / 10 * 8
                self.page.setFont(self.kFont, font_size)
            else:
                cs_x_offset = 0
                cs_y_offset = 0
                font_size = self.kProbFrameSize
                self.page.setFont(self.kFont, font_size)

            # 問題枠の右端に位置を調整する.
            std_x_pos = x_pos + rect_width
            std_y_pos = y_pos + rect_height * (1 + 0.05) - self.kProbFrameSize

            y_start_offset = font_size * start_pos_bias

            self.page.drawString(
                std_x_pos + cs_x_offset + x_space
                , std_y_pos - next_print_pos - y_start_offset
                , word
            )
            next_print_pos += font_size * y_bias + cs_y_offset

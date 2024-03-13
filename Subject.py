# Subject.py
# Copyright (c) 2023 Masaya Yamamoto
# Released under the MIT license.
# see https://opensource.org/licenses/MIT (英語)
# see https://licenses.opensource.jp/MIT/MIT.html (日本語)

class Subject:
    def __init__(self):
        self._observers = []

        self.kNotify_delete_student = 0
        self.kNotify_select_student = 1
        self.KNotify_load_successful = 2
        self.kNotify_load_failed = 3
        self.kNotify_valid_file_path = 4
        self.kNotify_create_worksheet = 5
        self.notify_status = self.kNotify_delete_student

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, status, modifier=None):
        self.notify_status = status
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)

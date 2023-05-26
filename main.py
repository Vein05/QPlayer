from PyQt5.QtWidgets import QApplication
import sys
from core.api import Api
from pages.songs_list_page import SongListPage



class App(Api):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.app = QApplication(sys.argv)
        self.initialize()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())

    def initialize(self):
        self.window = SongListPage(api)
        self.load_songs()


    def load_songs(self):
        self.window.load_songs()

    def run(self):
        self.app.installEventFilter(self.window)
        self.window.show()
        sys.exit(self.app.exec_())


api = Api()
app = App(api)
app.run()

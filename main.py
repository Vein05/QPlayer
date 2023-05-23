from PyQt5.QtWidgets import QWidget, QListView, QComboBox, QPushButton, QLabel, QMessageBox, QApplication, QHBoxLayout,QVBoxLayout, QProgressBar, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QEvent, QAbstractListModel, QModelIndex, QVariant, QUrl, QSize, QRect, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os, math
import sys
import sqlite3, json
from utils.tag import Tag


class SongListModel(QAbstractListModel):
    def __init__(self, songs=[]):
        super().__init__()
        self.songs = songs
        self.default_icon = "icons/default.png"

    def rowCount(self, parent=QModelIndex()):
        return len(self.songs)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        elif role == Qt.DisplayRole:
            return self.songs[index.row()].get('name', "Unknown Song")
        elif role == Qt.DecorationRole:
            song_data = self.songs[index.row()]
            if 'cover_image' in song_data and song_data['cover_image']:
                image = QImage.fromData(song_data['cover_image'])
                if not image.isNull():
                    return QPixmap.fromImage(image)
            return self.default_icon
        elif role == Qt.UserRole:
            return self.songs[index.row()]
        elif role == Qt.FontRole:
            font = QFont()
            font.setBold(True)
            font.setFamily("Noto Mono")
            font.setPointSize(17)
            font.setCapitalization(4)
            return font
        else:
            return QVariant()



class Api:
    def __init__(self):
        user = os.environ.get('USER')
        self.PATH = f"/home/{user}/Music"
        with open("./data/info.json", "w") as w:
            json.dump({"PATH" : self.PATH}, w)
        self.get_songs(self.PATH)

    def get_songs(self, path):
        self.MINIMAL_DURATION = 10
        self.music_extensions = [".mp3", ".ogg", ".wav", ".flac", ".m4a", ".m3u", ".mpa", ".aiff", ".wma"]
        entries = os.scandir(self.PATH)
        songs = []
        for root, dirs, files in os.walk(path):
            for val in files:
                extension = os.path.splitext(val)[1]
                if extension in self.music_extensions:
                    songs.append(os.path.join(root, val))
        self.insert_songs(songs)

    def insert_songs(self, songs):
        self.conn = sqlite3.connect("./data/music.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS music_files (
            path TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            album_artist TEXT,
            composer TEXT,
            genre TEXT,
            duration INTEGER,
            size INTEGER,
            year INTEGER,
            bitrate INTEGER
        );'''
                       )
        query = 'INSERT INTO music_files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        song_data_list = []
        for path in songs:
            tag = Tag(path)
            if not tag.duration:
                pass
            try:
                if tag.duration < self.MINIMAL_DURATION:
                    pass
            except TypeError:
                pass
            # add path too
            name = tag.name()
            artist = tag.artist
            album = tag.album
            album_artist = tag.album_artist
            composer = tag.composer
            genre = tag.genre
            duration = tag.duration
            size = tag.size
            year = tag.year
            bitrate = tag.bitrate
            song_data_list.append((path, name, artist, album, album_artist, composer, genre, duration, size, year, bitrate))

        try:
            self.c.executemany(query, song_data_list)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
        self.conn.close()

    def user_songs(self):
        self.conn = sqlite3.connect("./data/music.db")
        self.c = self.conn.cursor()
        self.c.execute(
            'SELECT path, name, artist, album, album_artist, composer, genre, duration, size, year, bitrate FROM music_files')
        rows = self.c.fetchall()

        songs = []
        
        for row in rows:
            tag = Tag(row[0])
            song = {
                'path': row[0],
                'name': row[1],
                'artist': row[2],
                'album': row[3],
                'album_artist': row[4],
                'composer': row[5],
                'genre': row[6],
                'duration': row[7],
                'size': row[8],
                'year': row[9],
                'bitrate': row[10],
                'cover_image': tag.cover_image(),

            }
            songs.append(song)
        self.conn.close()
        return songs


class MusicControlsWidget(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.api = parent #here parent is the main class of the window, i named it self.api for easier use

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)

        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.elapsed_label = QLabel("0:00")
        self.total_label = QLabel("")
        progress_layout.addWidget(self.elapsed_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.total_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        css = "background-color: transparent; border: none;"
        size = QSize(50,50)

        self.play_button = QPushButton("")
        self.play_button.setIcon(QIcon("./icons/play.png"))
        self.play_button.setStyleSheet(css)
        self.play_button.setIconSize(size)
        self.play_button.setVisible(False)
        self.play_button.clicked.connect(self.on_play_pause)

        self.pause_button = QPushButton("")
        self.pause_button.setIcon(QIcon("./icons/pause.png"))
        self.pause_button.setStyleSheet(css)
        self.pause_button.setIconSize(size)
        self.pause_button.clicked.connect(self.on_play_pause)


        self.next_button = QPushButton("")
        self.next_button.setIcon(QIcon("./icons/next.png"))
        self.next_button.setStyleSheet(css)
        self.next_button.setIconSize(size)
        self.next_button.clicked.connect(self.on_next)

        self.previous_button = QPushButton("")
        self.previous_button.setIcon(QIcon("./icons/previous.png"))
        self.previous_button.setStyleSheet(css)
        self.previous_button.setIconSize(size)
        self.previous_button.clicked.connect(self.on_previous)


        self.shuffle_button = QPushButton("")
        self.shuffle_button.setIcon(QIcon("./icons/shuffle.png"))
        self.shuffle_button.setStyleSheet(css)
        self.shuffle_button.setIconSize(size)
        self.shuffle_button.clicked.connect(self.on_shuffle)
        self.shuffle_button.setVisible(False)


        self.repeat_button = QPushButton("")
        self.repeat_button.setIcon(QIcon("./icons/repeat.png"))
        self.repeat_button.setStyleSheet(css)
        self.repeat_button.setIconSize(size)
        self.repeat_button.clicked.connect(self.on_repeat)
        self.repeat_button.setVisible(False)


        self.straight_button = QPushButton("")
        self.straight_button.setIcon(QIcon("./icons/straight.png"))
        self.straight_button.setStyleSheet(css)
        self.straight_button.setIconSize(size)
        self.straight_button.clicked.connect(self.on_straight)
        self.straight_button.setVisible(True)

        

        buttons_layout.addWidget(self.previous_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.straight_button)

        layout.addLayout(progress_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def update_progress(self):
        pass

    def on_play_pause(self):
        self.api.play_pause_song(self.api.current_index)

    def on_next(self):

        pass
    def on_previous(self):

        pass

    def on_shuffle(self):
        pass

    def on_straight(self):
        pass
    

    def on_repeat(self):
        pass


class MainWindow(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()
        self.media_player = QMediaPlayer()
        self.media_player.error.connect(self.handle_media_error)
        self.current_index = QModelIndex()

    def setup_ui(self):
        # Initialize and set up the UI components
        self.setGeometry(500, 500, 534, 900)
        self.setWindowTitle("Simple Music Player")
        self.setStyleSheet("""
            background-color: #a9d6e5;
            
        """)
        self.song_list_model = None

        #Addin the buttonso on the lower screen 
        main_layout = QVBoxLayout(self)

        self.music_controls_widget = MusicControlsWidget(self)

        main_layout.addStretch()
        main_layout.addWidget(self.music_controls_widget)

        self.setLayout(main_layout)


    def load_songs(self):
        songs = self.api.user_songs()
        self.song_list_model = SongListModel(songs)
        self.song_list_view = QListView(self)
        self.song_list_view.setModel(self.song_list_model)
        self.song_list_view.setStyleSheet('''
            QListView {
                background-color: #bee9e8;
                border-radius: 2px ;
                padding: 10px;
                font: bold 12px;
                font-family: "Arial", sans-serif;
                font-size: 30px;
            }

            QListView::item {
                padding: 5px;
                outline:none;
            }

            QListView::item:selected {
                background-color: #8ecae6;
                
            }



            ''')
        self.song_list_view.setGeometry(0, 130, 521, 600)
        self.song_list_view.clicked.connect(self.handle_song_list_item_clicked)

        # Add sorting options combo box
        self.sort_combo = QComboBox(self)
        self.sort_combo.setGeometry(150, 50, 135, 35)
        self.sort_combo.addItem("Name")
        self.sort_combo.addItem("Date Added")
        self.sort_combo.currentIndexChanged.connect(self.sort_songs)

        # Add sort button
        self.sort_button = QPushButton("Sort", self)
        self.sort_button.setGeometry(10, 50, 135, 35)
        self.sort_button.clicked.connect(self.sort_songs)

        j = json.load(open("./data/info.json"))
        self.current_director = QLabel(self)
        self.current_director.setText(f"Current dir : {j['PATH']}")
        self.current_director.setGeometry(10,90,521, 30)


    def sort_songs(self):
        sort_option = self.sort_combo.currentText()
        if sort_option == "Name":
            self.sort_by_name()
        elif sort_option == "Date Added":
            self.sort_by_date_added()

    def sort_by_name(self):
        songs = self.song_list_model.songs
        sorted_songs = sorted(songs, key=lambda x: x['name'])
        self.song_list_model = SongListModel(sorted_songs)
        self.song_list_view.setModel(self.song_list_model)

    def sort_by_date_added(self):
        songs = self.song_list_model.songs
        sorted_songs = sorted(songs, key=lambda x: x['path'])
        self.song_list_model = SongListModel(sorted_songs)
        self.song_list_view.setModel(self.song_list_model)

    def play_pause_song(self, index):
        song_data = self.song_list_model.songs[index.row()]
        # Create a QMediaContent object with the path
        media_content = QMediaContent(QUrl.fromLocalFile(song_data['path']))
        # If the selected song is already playing, pause it. Otherwise, play it.
        if index == self.current_index:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.music_controls_widget.play_button.setVisible(True)
                self.music_controls_widget.pause_button.setVisible(False)
            else:
                self.media_player.play()
                self.music_controls_widget.play_button.setVisible(False)
                self.music_controls_widget.pause_button.setVisible(True)

        # If a different song is clicked, play it and update the current index
        else:
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.music_controls_widget.play_button.setVisible(False)
            self.music_controls_widget.pause_button.setVisible(True)
            self.current_index = index
            self.current_index = index

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if obj == self.song_list_view:  # Handle events only for the QListView
                if event.key() == Qt.Key_Space:
                    self.play_pause_song(self.current_index)
        return super().eventFilter(obj, event)

    def handle_song_list_item_clicked(self, index):
        self.play_pause_song(index)

    def handle_media_error(self, error):
        if error == QMediaPlayer.NoError:
            return
        elif error == QMediaPlayer.ResourceError:
            error_message = "Error: No data in file"
        else:
            error_message = "Error: " + self.media_player.errorString()
        QMessageBox.critical(self, "Error", error_message)

class App(Api):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.HEIGHT = 534
        self.WIDTH = 840
        self.X = 500
        self.Y = 500
        self.app = QApplication(sys.argv)
        self.initialize()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())

    def initialize(self):
        self.window = MainWindow(self.api)
        self.window.setGeometry(self.X, self.Y, self.HEIGHT, self.WIDTH)
        self.window.setWindowTitle("QPlayer")
        self.window.setStyleSheet("""
            background-color: #F5F5F5;
            color: #333333;
        """)

        heading = QLabel(self.window)
        heading.setText("Hello, Welcome!")
        heading.setGeometry(140, 10, 270, 36)
        heading.setStyleSheet(
            '''
                font: 14px "Noto Mono";
                font-size : 30px;
                color: #333333;
            '''
        )

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

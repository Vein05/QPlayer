from PyQt5.QtWidgets import QWidget, QListView, QComboBox, QPushButton, QLabel, QMessageBox, QApplication, QHBoxLayout,QVBoxLayout, QProgressBar, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QEvent, QAbstractListModel, QModelIndex, QVariant, QUrl, QSize, QRect, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
import os, math
import sys
import sqlite3, json
from utils.tag import Tag
from utils import helper
import random




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
        self.total_label = QLabel("0:00")
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
        self.shuffle_button.clicked.connect(self.on_shuffle_clicked)
        self.shuffle_button.setVisible(False)


        self.repeat_button = QPushButton("")
        self.repeat_button.setIcon(QIcon("./icons/repeat.png"))
        self.repeat_button.setStyleSheet(css)
        self.repeat_button.setIconSize(size)
        self.repeat_button.clicked.connect(self.on_repeat_clicked)
        self.repeat_button.setVisible(False)


        self.straight_button = QPushButton("")
        self.straight_button.setIcon(QIcon("./icons/straight.png"))
        self.straight_button.setStyleSheet(css)
        self.straight_button.setIconSize(size)
        self.straight_button.clicked.connect(self.on_straight_clicked)
        self.straight_button.setVisible(True)

        #make sure to update this when the song is changed

        self.cover_button = QPushButton("")
        self.cover_button.setStyleSheet(css)
        self.cover_button.setIconSize(size)
        self.cover_button.clicked.connect(self.on_cover_clicked)
        # self.cover_button.setIcon(QIcon("/icons/default.png"))
        # self.cover_button.setStyleSheet("")
        

        buttons_layout.addWidget(self.cover_button)
        buttons_layout.addWidget(self.previous_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.straight_button)
        buttons_layout.addWidget(self.repeat_button)
        buttons_layout.addWidget(self.shuffle_button)

        layout.addLayout(progress_layout)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)


    def on_play_pause(self):
        self.api.play_pause_song(self.api.current_index)

    def on_next(self):
        current_row = self.api.current_index.row()
        next_row = current_row + 1

        if next_row < self.api.song_list_model.rowCount():
            index = self.api.song_list_model.index(next_row, 0)
            self.api.play_pause_song(index)

    def on_previous(self):
        current_row = self.api.current_index.row()
        previous_row = current_row - 1

        if previous_row >= 0:
            index = self.api.song_list_model.index(previous_row, 0)
            self.api.play_pause_song(index)

    def on_shuffle_clicked(self):
        #do repeat
        self.shuffle_button.setVisible(False)
        self.repeat_button.setVisible(True)
        self.straight_button.setVisible(False)
        self.api.repeat_playback_queue()

    def on_straight_clicked(self):
        #do shuffle
        self.shuffle_button.setVisible(True)
        self.repeat_button.setVisible(False)
        self.straight_button.setVisible(False)
        self.api.shuffle_playback_queue()

    

    def on_repeat_clicked(self):
        #do straight 
        self.shuffle_button.setVisible(False)
        self.repeat_button.setVisible(False)
        self.straight_button.setVisible(True)
        self.api.straight_playback_queue()


    def on_cover_clicked(self):

        pass


    def update_progress(self):
        if self.api.media_player.duration() is not None and self.api.media_player.position() is not None:
            if self.api.progress_timer is None:
                self.create_progress_timer()
                self.api.progress_timer.start(1000)
            duration = self.api.media_player.duration() / 1000  # Convert to seconds
            position = self.api.media_player.position() / 1000  # Convert to seconds
            progress = int((position / duration) * 100) if duration != 0 else 0
            self.progress_bar.setValue(progress)
            self.elapsed_label.setText(helper.get_time(int(position)))

        # Check if the song has finished playing
        if position >= duration:
            self.api.progress_timer.stop()
            self.api.stop_song()

class MainWindow(QWidget):
    def __init__(self, api, parent=None):
        super().__init__()
        self.api = api

        
        self.setup_ui()
        self.media_player = QMediaPlayer()
        self.media_player.error.connect(self.handle_media_error)
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_changed)
        self.media_player.stateChanged.connect(self.handle_media_status_changed)
        self.current_index = QModelIndex()
        self.playback_queue = []
        self.progress_timer = None

        
        
    def setup_ui(self):
        # Initialize and set up the UI components
        # self.setGeometry(500, 500, 534, 900)
        self.setFixedSize(535, 900)
        self.setWindowTitle("QPlayer")
        self.setStyleSheet("""
            background-color: #a9d6e5;
            
        """)
        self.heading = QLabel(self)
        self.heading.setText("Hello, Welcome!")
        self.heading.setGeometry(0,0,531,36)
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-family: monospace;
            }
        """)

        self.song_list_model = None

        #Addin the buttonso on the lower screen 
        main_layout = QVBoxLayout(self)

        self.music_controls_widget = MusicControlsWidget(self)
        self.music_controls_widget.progress_bar.mousePressEvent = self.handle_progress_bar_click


        main_layout.addStretch()
        main_layout.addWidget(self.music_controls_widget)

        self.setLayout(main_layout)


    def load_songs(self):
        songs = self.api.user_songs()
        self.song_list_model = SongListModel(songs)
        self.populate_playback_queue()
        self.song_list_view = QListView(self)
        self.song_list_view.setModel(self.song_list_model)
        self.song_list_view.setStyleSheet('''
                /* QListView styles */
                QListView {
                    background-color: transparent; /* Remove background color */
                    border: 4px solid ; /* Increase border thickness */
                    border-radius: 8px; /* Increase border radius */
                    padding: 10px;
                    margin: 10px;
                }
            ''')
        self.song_list_view.setGeometry(0, 130, 521, 600)
        self.song_list_view.clicked.connect(self.handle_song_list_item_clicked)

        # Add sorting options combo box
        size = QSize(30, 30)
        self.sort_combo = QComboBox(self)
        self.sort_combo.setGeometry(470, 40, 75, 60)
        name = QIcon("./icons/sort_name.png")
        date = QIcon("./icons/sort_date.png")
        self.sort_combo.addItem(name,"")
        self.sort_combo.addItem(date,"")
        self.sort_combo.setIconSize(size)
        self.sort_combo.currentIndexChanged.connect(self.sort_songs)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 2px;
                border: none;
                background-color: transparent;
            }

            QComboBox::down-arrow {
                image: none;
            }

            QComboBox:hover, QComboBox:focus {
                border: none;
            }
        """)
        

        # Add sort button
        self.sort_button = QPushButton("", self)
        self.sort_button.setGeometry(420, 40, 60, 60)
        self.sort_button.clicked.connect(self.sort_songs)
        self.sort_button.setIcon(QIcon("./icons/sort.png"))
        self.sort_button.setIconSize(size)
        self.sort_button.setStyleSheet("background-color: transparent; border: none;")

        j = json.load(open("./data/info.json"))
        self.current_director = QLabel(self)
        self.current_director.setText(f"Current dir : {j['PATH']}")
        self.current_director.setGeometry(10,90,521, 30)


    def sort_songs(self):
        sort_option_index = self.sort_combo.currentIndex()
        if sort_option_index == 0:
            self.sort_by_name()
        elif sort_option_index == 1:
            self.sort_by_date_added()

    def sort_by_name(self):
        songs = self.song_list_model.songs
        sorted_songs = sorted(songs, key=lambda x: x['name'])
        self.song_list_model_new = SongListModel(sorted_songs)
        self.song_list_view.setModel(self.song_list_model_new)
        self.playback_queue = ((self.song_list_model_new.songs))

    def sort_by_date_added(self):
        songs = self.song_list_model.songs
        sorted_songs = sorted(songs, key=lambda x: os.path.getmtime(x['path']))
        self.song_list_model_new = SongListModel(sorted_songs)
        self.song_list_view.setModel(self.song_list_model_new)
        self.playback_queue = ((self.song_list_model_new.songs))




    def populate_playback_queue(self):
        self.playback_queue = list((self.song_list_model.songs))

    def shuffle_playback_queue(self):
        random.shuffle(self.playback_queue)

    def repeat_playback_queue(self):
        if self.current_index is not None:
            current_row = self.current_index.row()
            self.playback_queue = [self.playback_queue[current_row]]

    def straight_playback_queue(self):
        current_row = self.current_index.row()
        self.playback_queue = self.playback_queue[current_row:] + self.playback_queue[:current_row]

    def create_progress_timer(self):
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.music_controls_widget.update_progress)


    def play_pause_song(self, index):

        if self.progress_timer is None:
            self.create_progress_timer()

        if index.row() >= len(self.playback_queue):
            index = self.song_list_model.index(0)

        song_data = self.playback_queue[index.row()]
        media_content = QMediaContent(QUrl.fromLocalFile(song_data['path']))

        if index == self.current_index:
            if self.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.music_controls_widget.play_button.setVisible(True)
                self.music_controls_widget.pause_button.setVisible(False)
                if self.progress_timer is None:
                    self.create_progress_timer()

                self.progress_timer.stop()
            else:
                self.media_player.play()
                self.music_controls_widget.play_button.setVisible(False)
                self.music_controls_widget.pause_button.setVisible(True)
                self.progress_timer.start(1000)
        else:
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.music_controls_widget.play_button.setVisible(False)
            self.music_controls_widget.pause_button.setVisible(True)
            self.current_index = index

            try:
                self.progress_timer.start(1000)
            except AttributeError:
                pass

        # Update cover image and time display
        if song_data['cover_image']:
            default_icon_path = "./icons/default.png"
            current_icon_path = self.music_controls_widget.cover_button.icon().pixmap(256, 256).cacheKey()
            if current_icon_path != default_icon_path:
                pixmap = QPixmap()
                pixmap.loadFromData(song_data['cover_image'])
                self.music_controls_widget.cover_button.setIcon(QIcon(pixmap))
        time = helper.get_time(song_data['duration'])
        self.music_controls_widget.total_label.setText(f"{time}")



        # self.heading.setAlignment(Qt.AlignCenter)
        heading = self.heading
        heading.setText(song_data['name'])


        if hasattr(self, 'marquee_timer'):
            self.marquee_timer.stop()
        self.marquee_timer = QTimer()
        self.marquee_timer.timeout.connect(lambda: self.scroll_heading(heading))
        self.marquee_timer.start(30)  # 30ms timer

    def scroll_heading(self, label):
        width = label.fontMetrics().boundingRect(label.text()).width()
        x = label.x()
        if x <= -width:
            x = self.width()

        x -= 1  # Scroll

        label.move(x, label.y())  # Update label position


    def stop_song(self):
        # Stop the progress timer
        if self.progress_timer is not None:
            try:
                self.progress_timer.stop()
                # Reset the progress bar and labels
                self.music_controls_widget.progress_bar.setValue(0)
                self.music_controls_widget.elapsed_label.setText("0:00")
                # self.music_controls_widget.total_label.setText("0:00")
                        
            except AttributeError:
                pass



    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            current_index = self.current_index.row()
            
            #+1 for other conditions 0 for repeat condition
            next_index = current_index + 1 if current_index < (self.song_list_model.rowCount() - 1) else 0
            
            self.play_pause_song(self.song_list_model.index(next_index))

        if status == QMediaPlayer.PlayingState:
            pass
        
        
        elif status == QMediaPlayer.PausedState:
            pass

        elif status == QMediaPlayer.StoppedState:
            pass
        


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if obj == self.song_list_view:  # Handle events only for the QListView
                if event.key() == Qt.Key_Space:
                    self.play_pause_song(self.current_index)
        return super().eventFilter(obj, event)

    def handle_song_list_item_clicked(self, index):
        self.play_pause_song(index)

    def handle_media_error(self, error):
        self.play_pause_song(self.song_list_model.index(self.current_index.row()+1, 0))
        if error == QMediaPlayer.NoError:
            return
        elif error == QMediaPlayer.ResourceError:
            error_message = "Paying next song in song list because of error : "
            QMessageBox.critical(self,"Error:" ,error_message)
        else:
            error_message =  "Paying next song in song list because of error : " + self.media_player.errorString()
       

    def handle_player_state_changed(self, new_state):
        if new_state == QMediaPlayer.StoppedState or new_state == QMediaPlayer.PausedState:
            
            # Stop the timer or pause the progress bar update
            try:
                self.progress_timer.stop()
                self.stop_song()
            except AttributeError:
                pass
        elif new_state == QMediaPlayer.PlayingState:
            # Resume the timer or resume the progress bar update
            try:
                self.progress_timer.start(1000)
            except AttributeError:
                pass

    def handle_progress_bar_click(self, event):
        if event.button() == Qt.LeftButton:  
            progress_rect = QRect(0, 0, self.music_controls_widget.progress_bar.width(), self.music_controls_widget.progress_bar.height())   
            if progress_rect.contains(event.pos()):
                click_pos = event.pos().x()                
                duration = self.media_player.duration()       
                position = (click_pos / self.music_controls_widget.progress_bar.width()) * duration       
                self.media_player.setPosition(int(position))



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
        self.window = MainWindow(self.api,self)
        self.window.setStyleSheet("""
            font: 16px "Helvetica Neue", sans-serif;

        """)
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

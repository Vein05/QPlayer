#create a skeleton for the pages that list the songs in a certian folder
import os, json, random

from PyQt5.QtWidgets import QWidget, QListView, QComboBox, QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtMultimedia import QMediaPlayer



from core.music_control import MusicControlsWidget
from pages.song_list_model import SongListModel
from utils.errors import Handler
from utils.shadow import ShadowButton

class SongListPage(QWidget):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.media_player = QMediaPlayer()

        


    def load_songs(self):
        songs = self.api.user_songs() #edit this to take in the path and all of that so we can load many pages from here
        self.song_list_model = SongListModel(songs)
        self.music = MusicControlsWidget(self.song_list_model, parent=self)
        self.handler = Handler(self.music, parent = self)
        self.setup_ui()
        self.music.populate_playback_queue()



        
        self.song_list_view = QListView(self)
        self.song_list_view.setModel(self.song_list_model)
        self.song_list_view.setStyleSheet('''
                /* QListView styles */
                QListView {
                    background-color: transparent; 
                    border: 4px solid ;
                    border-radius: 8px; 
                    padding: 10px;
                    margin: 10px;
                }
            ''')
        self.song_list_view.setGeometry(0, 130, 521, 600)
        self.song_list_view.clicked.connect(self.handler.handle_song_list_item_clicked)

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

        self.media_player.error.connect(self.handler.handle_media_error)
        self.media_player.mediaStatusChanged.connect(self.handler.handle_media_status_changed)
        self.media_player.stateChanged.connect(self.handler.handle_media_status_changed)


    def setup_ui(self):
        # Initialize and set up the UI components
        # self.setGeometry(500, 500, 534, 900)
        self.setFixedSize(535, 900)
        self.setWindowTitle("QPlayer")
        self.setStyleSheet("""
            font: 16px "Helvetica Neue", sans-serif;
            background-color: #a9d6e5;
        """)
        self.heading = QLabel(self)
        self.heading.setText("Hello, Welcome!")
        self.heading.setGeometry(0, 0, 531, 36)
        self.heading.setAlignment(Qt.AlignCenter)
        self.heading.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-family: monospace;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        container_layout = QVBoxLayout()
        

        progress_layout = QHBoxLayout() 
        self.elapsed_label = QLabel("0:00")
        self.total_label = QLabel("0:00") 
        progress_layout.addWidget(self.elapsed_label)
        progress_layout.addWidget(self.music.progress_bar)
        progress_layout.addWidget(self.total_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        css = "background-color: transparent; border: none;"
        size = QSize(50, 50)

        self.play_button = QPushButton("")
        self.play_button.setIcon(QIcon("./icons/play.png"))
        self.play_button.setStyleSheet(css)
        self.play_button.setIconSize(size)
        self.play_button.setVisible(False)
        self.play_button.clicked.connect(self.music.on_play_pause)

        self.pause_button = QPushButton("")
        self.pause_button.setIcon(QIcon("./icons/pause.png"))
        self.pause_button.setStyleSheet(css)
        self.pause_button.setIconSize(size)
        self.pause_button.clicked.connect(self.music.on_play_pause)

        self.next_button = QPushButton("")
        self.next_button.setIcon(QIcon("./icons/next.png"))
        self.next_button.setStyleSheet(css)
        self.next_button.setIconSize(size)
        self.next_button.clicked.connect(self.music.on_next)

        self.previous_button = QPushButton("")
        self.previous_button.setIcon(QIcon("./icons/previous.png"))
        self.previous_button.setStyleSheet(css)
        self.previous_button.setIconSize(size)
        self.previous_button.clicked.connect(self.music.on_previous)

        self.shuffle_button = QPushButton("")
        self.shuffle_button.setIcon(QIcon("./icons/shuffle.png"))
        self.shuffle_button.setStyleSheet(css)
        self.shuffle_button.setIconSize(size)
        self.shuffle_button.clicked.connect(self.music.on_shuffle_clicked)
        self.shuffle_button.setVisible(False)

        self.repeat_button = QPushButton("")
        self.repeat_button.setIcon(QIcon("./icons/repeat.png"))
        self.repeat_button.setStyleSheet(css)
        self.repeat_button.setIconSize(size)
        self.repeat_button.clicked.connect(self.music.on_repeat_clicked)
        self.repeat_button.setVisible(False)

        self.straight_button = QPushButton("")
        self.straight_button.setIcon(QIcon("./icons/straight.png"))
        self.straight_button.setStyleSheet(css)
        self.straight_button.setIconSize(size)
        self.straight_button.clicked.connect(self.music.on_straight_clicked)
        self.straight_button.setVisible(True)

        self.cover_button = ShadowButton("")
        self.cover_button.setStyleSheet("""    
        QPushButton {
            background-color: transparent;
            border: none;
            border-radius: 25px;
        }
    

        """)
        self.cover_button.setIconSize(size)
        self.cover_button.setIcon(QIcon("./icons/default.png"))
        self.cover_button.setCursor(Qt.PointingHandCursor)
        self.cover_button.clicked.connect(self.music.on_cover_clicked)


        buttons_layout.addWidget(self.cover_button)
        buttons_layout.addWidget(self.previous_button)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.straight_button)
        buttons_layout.addWidget(self.repeat_button)
        buttons_layout.addWidget(self.shuffle_button)


        container_layout.addLayout(progress_layout)
        container_layout.addLayout(buttons_layout)
        layout.addStretch()
        container_layout.addWidget(self.music)
        layout.addLayout(container_layout)  # Add main container to overall layout
        self.setLayout(layout)



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
        self.music.playback_queue = ((self.song_list_model_new.songs))

    def sort_by_date_added(self):
        songs = self.song_list_model.songs
        sorted_songs = sorted(songs, key=lambda x: os.path.getmtime(x['path']))
        self.song_list_model_new = SongListModel(sorted_songs)
        self.song_list_view.setModel(self.song_list_model_new)
        self.music.playback_queue = ((self.song_list_model_new.songs))





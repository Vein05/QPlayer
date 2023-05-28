from PyQt5.QtWidgets import QWidget,QPushButton, QLabel, QHBoxLayout,QVBoxLayout, QProgressBar
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, QUrl, QTimer, Qt, QRect, QModelIndex
from utils import helper
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent 
import random
from utils.scroll import ScrollableProgressBar


class MusicControlsWidget(QWidget):
    def __init__(self, song_list_model, parent=None, **kwargs):
        super().__init__()
        self.song_list_model = song_list_model
        self.progress_bar = ScrollableProgressBar(self)
        self.current_index = QModelIndex()
        self.playback_queue = []
        self.progress_timer = None
        self.parent = parent
        self.media_player = parent.media_player

    def on_play_pause(self):
        self.play_pause_song(self.current_index)

    def on_next(self):
        current_row = self.current_index.row()
        next_row = current_row + 1

        if next_row < self.song_list_model.rowCount():
            index = self.song_list_model.index(next_row, 0)
            self.play_pause_song(index)

    def on_previous(self):
        current_row = self.current_index.row()
        previous_row = current_row - 1

        if previous_row >= 0:
            index = self.song_list_model.index(previous_row, 0)
            self.play_pause_song(index)

    def on_shuffle_clicked(self):
        #do repeat
        self.parent.shuffle_button.setVisible(False)
        self.parent.repeat_button.setVisible(True)
        self.parent.straight_button.setVisible(False)
        self.repeat_playback_queue()

    def on_straight_clicked(self):
        #do shuffle
        self.parent.shuffle_button.setVisible(True)
        self.parent.repeat_button.setVisible(False)
        self.parent.straight_button.setVisible(False)
        self.shuffle_playback_queue()

    

    def on_repeat_clicked(self):
        #do straight 
        self.parent.shuffle_button.setVisible(False)
        self.parent.repeat_button.setVisible(False)
        self.parent.straight_button.setVisible(True)
        self.straight_playback_queue()


    def on_cover_clicked(self):

        pass


    def update_progress(self):
        if self.media_player.duration() is not None and self.media_player.position() is not None:
            if self.progress_timer is None:
                self.create_progress_timer()
                self.progress_timer.start(1000)
            duration = self.media_player.duration() / 1000  # Convert to seconds
            position = self.media_player.position() / 1000  # Convert to seconds
            progress = int((position / duration) * 100) if duration != 0 else 0
            self.progress_bar.setValue(progress)
            self.parent.elapsed_label.setText(helper.get_time(int(position)))

        # Check if the song has finished playing
        if position >= duration:
            self.progress_timer.stop()
            self.stop_progress()


    def play_pause_song(self, index):

        if self.progress_timer is None:
            self.create_progress_timer()

        if index.row() >= len(self.playback_queue):
            index = self.song_list_model.index(0)

        song_data = self.playback_queue[index.row()]
        media_content = QMediaContent(QUrl.fromLocalFile(song_data['path']))
        if index == self.current_index:

            if self.parent.media_player.state() == QMediaPlayer.PlayingState:
                self.media_player.pause()
                self.parent.play_button.setVisible(True)
                self.parent.pause_button.setVisible(False)
                if self.progress_timer is None:
                    self.create_progress_timer()

                self.progress_timer.stop()
            else:
                print("stoped")
                self.media_player.play()
                self.parent.play_button.setVisible(False)
                self.parent.pause_button.setVisible(True)
                self.progress_timer.start(1000)
        else:
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.parent.play_button.setVisible(False)
            self.parent.pause_button.setVisible(True)
            self.current_index = index

            try:
                self.progress_timer.start(1000)
            except AttributeError:
                pass

        # Update cover image and time display
        if song_data['cover_image']:
            default_icon_path = "./icons/default.png"
            current_icon_path = self.parent.cover_button.icon().pixmap(256, 256).cacheKey()
            if current_icon_path != default_icon_path:
                pixmap = QPixmap()
                pixmap.loadFromData(song_data['cover_image'])
                self.parent.cover_button.setIcon(QIcon(pixmap))
        time = helper.get_time(song_data['duration'])
        self.parent.total_label.setText(f"{time}")



        
        heading = self.parent.heading
        heading.setText(song_data['name'])


        if hasattr(self, 'marquee_timer'):
            self.marquee_timer.stop()
        self.marquee_timer = QTimer()
        self.marquee_timer.timeout.connect(lambda: self.scroll_heading(heading))
        self.marquee_timer.start(20)  # 30ms timer

    def scroll_heading(self, label):
        width = label.width()  
        x = label.x()

        if x <= -width:
            x = self.width()

        x -= 1 

        if x + width <= 0:
            x = self.width()

        label.move(x, label.y())  


    def set_song_list_model(self, new_model):
        self.song_list_model = new_model
        self.populate_playback_queue()


    def create_progress_timer(self):
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)


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


    def stop_progress(self):
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
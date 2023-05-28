from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QMessageBox



class Handler:

    def __init__(self,music_control,parent=None):
        super().__init__()
        self.parent = parent
        self.music_control = music_control









    def handle_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            current_index = self.music_control.current_index.row()
            
            #+1 for other conditions 0 for repeat condition
            next_index = current_index + 1 if current_index < (self.music_control.song_list_model.rowCount() - 1) else 0
            
            self.music_control.play_pause_song(self.music_control.song_list_model.index(next_index))

        if status == QMediaPlayer.PlayingState:
            pass
        
        
        elif status == QMediaPlayer.PausedState:
            pass

        elif status == QMediaPlayer.StoppedState:
            pass
        




    def handle_song_list_item_clicked(self, index):
        self.music_control.play_pause_song(index)

    def handle_media_error(self, error):
        self.music_control.play_pause_song(self.music_control.song_list_model.index(self.music_control.current_index.row()+1, 0))
        if error == QMediaPlayer.NoError:
            return
        elif error == QMediaPlayer.ResourceError:
            error_message = "Paying next song in song list because of error : "
            QMessageBox.critical(self.music_control,"Error:" ,error_message)
        else:
            error_message =  "Paying next song in song list because of error : " + self.music_control.media_player.errorString()
       

    def handle_player_state_changed(self, new_state):
        if new_state == QMediaPlayer.StoppedState or new_state == QMediaPlayer.PausedState:
            
            # Stop the timer or pause the progress bar update
            try:
                self.music_control.progress_timer.stop()
                self.music_control.stop_song()
            except AttributeError:
                pass
        elif new_state == QMediaPlayer.PlayingState:
            # Resume the timer or resume the progress bar update
            try:
                self.music_control.progress_timer.start(1000)
            except AttributeError:
                pass

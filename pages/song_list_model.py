from PyQt5.QtGui import QFont, QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


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

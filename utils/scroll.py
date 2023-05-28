from PyQt5.QtWidgets import QProgressBar, QStyleOptionSlider 
from PyQt5.QtGui import QPainter, QCursor
from PyQt5.QtCore import Qt, QRect, QPoint

class ScrollableProgressBar(QProgressBar):
    def __init__(self, parent):
        super().__init__(parent) 
        self.setTextVisible(False)
        self.parent = parent
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #8d5fff;
                border-radius: 5px;
                height: 10px;
                background:transparent;
            }

            QProgressBar::chunk {
                background-color: #bc99ff;    
            }

        """)
        self.dragging = False
        
        
    def mousePressEvent(self, event):        
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.startPos = event.pos()
         
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.updateProgressFromPos(event.pos())
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            click_pos = event.pos().x()
            
            self.setValue(int(click_pos / self.rect().width() * self.maximum()))  
            
            self.updateSongPosition(click_pos)
            
    def updateSongPosition(self, click_pos):      
        duration = self.parent.media_player.duration()  
        time_value = click_pos / self.rect().width() * duration    
        self.parent.media_player.setPosition(int(time_value))
            
    def updateProgressFromPos(self, pos):
        progress = self.width() * (pos.x() - self.startPos.x()) / self.width()       
        self.setValue(int(progress))  
        self.updateSongPosition(pos)

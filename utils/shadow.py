# Import the necessary classes
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize

# Create a custom QPushButton subclass
class ShadowButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shadow_effect = None
        self.setMouseTracking(True)

    def enterEvent(self, event):
        # Increase icon size and apply shadow effect on hover
        self.setIconSize(QSize(60, 60))
        self.addShadowEffect()

    def leaveEvent(self, event):
        # Revert icon size and remove shadow on leave
        self.setIconSize(QSize(50, 50))
        self.removeShadowEffect()

    def addShadowEffect(self):
        # Create and set the drop shadow effect
        if not self.shadow_effect:
            self.shadow_effect = QGraphicsDropShadowEffect(self)
            self.shadow_effect.setBlurRadius(25)
            self.shadow_effect.setColor(QColor(0, 0, 0, 128))
            self.shadow_effect.setOffset(3, 3)
            self.setGraphicsEffect(self.shadow_effect)

    def removeShadowEffect(self):
        # Remove the drop shadow effect
        if self.shadow_effect:
            self.shadow_effect.setEnabled(False)
            self.setGraphicsEffect(None)
            self.shadow_effect = None



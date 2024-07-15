import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_following_cursor = False
        self.home_position = QPoint(100, 100)
        self.setGeometry(self.home_position.x(), self.home_position.y(), 100, 100)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        label = QLabel(self)
        pixmap = QPixmap('pet.png')  # Replace with your pet image
        label.setPixmap(pixmap)
        label.resize(pixmap.width(), pixmap.height())

        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_following_cursor = not self.is_following_cursor
            if self.is_following_cursor:
                QTimer.singleShot(100, self.follow_cursor)

    def follow_cursor(self):
        if self.is_following_cursor:
            self.move(QCursor.pos() - QPoint(50, 50))
            QTimer.singleShot(50, self.follow_cursor)

    def enterEvent(self, event):
        self.setWindowOpacity(0.5)

    def leaveEvent(self, event):
        self.setWindowOpacity(1.0)

    def contextMenuEvent(self, event):
        self.is_following_cursor = False
        self.move(self.home_position)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec_())
from PyQt5.QtWidgets import QLabel,  QWidget,  QRubberBand
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import  QGuiApplication

class FullScreenSelection(QWidget):
    def __init__(self, parent, continuous_mode=False):
        super().__init__()
        self.parent = parent
        self.continuous_mode = continuous_mode
        self.setWindowTitle("選擇螢幕範圍")
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)

        # 擷取螢幕快照
        self.screenshot = QGuiApplication.primaryScreen().grabWindow(0)
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setPixmap(self.screenshot)
        self.screenshot_label.setGeometry(self.screenshot.rect())

        # 選擇範圍的相關屬性
        self.start_point = None
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.rubber_band.setGeometry(QRect(self.start_point, event.pos()).normalized())
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if self.rubber_band.isVisible():
            self.rubber_band.setGeometry(QRect(self.start_point, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        '''
        if event.button() == Qt.LeftButton:
            rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.parent.set_selected_area(rect)
            self.parent.run_ocr()
            self.close()
        '''
        if event.button() == Qt.LeftButton and self.rubber_band.isVisible():
            end_point = event.pos()
            selected_area = QRect(self.start_point, end_point).normalized()
            self.parent.set_selected_area(selected_area)
            self.close()
            if self.continuous_mode:
                pass
            else:
                self.parent.run_ocr()




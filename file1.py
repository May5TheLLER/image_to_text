import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QRubberBand
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPixmap, QGuiApplication


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螢幕擷取與 OCR 工具")
        self.setGeometry(100, 100, 500, 300)
        
        # 初始化 UI
        self.init_ui()

        # 範圍選擇的相關屬性
        self.selected_area = None

    def init_ui(self):
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 按鈕：選擇螢幕範圍
        self.select_area_button = QPushButton("選擇螢幕範圍", self)
        self.select_area_button.clicked.connect(self.start_screen_selection)
        layout.addWidget(self.select_area_button)

        # 標籤：顯示選擇的範圍資訊
        self.area_label = QLabel("尚未選擇範圍", self)
        layout.addWidget(self.area_label)

        # 按鈕：執行 OCR
        self.ocr_button = QPushButton("執行 OCR", self)
        self.ocr_button.clicked.connect(self.run_ocr)
        self.ocr_button.setEnabled(False)  # 尚未選擇範圍時禁用
        layout.addWidget(self.ocr_button)

        # 按鈕：儲存文字
        self.save_button = QPushButton("儲存文字", self)
        self.save_button.clicked.connect(self.save_text)
        self.save_button.setEnabled(False)  # 尚未執行 OCR 時禁用
        layout.addWidget(self.save_button)

        # 設定佈局
        central_widget.setLayout(layout)

    def start_screen_selection(self):
        # 進入範圍選擇模式，隱藏主視窗
        self.hide()
        self.fullscreen_window = FullScreenSelection(self)
        self.fullscreen_window.show()

    def set_selected_area(self, rect):
        self.selected_area = rect
        self.area_label.setText(f"選擇的範圍：x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}")
        self.ocr_button.setEnabled(True)  # 啟用 OCR 按鈕
        self.show()

    def run_ocr(self):
        # TODO: 實作 OCR 功能
        # 假設 OCR 提取了文字
        self.extracted_text = "這是 OCR 提取的文字"
        print(f"OCR 提取結果：{self.extracted_text}")
        self.save_button.setEnabled(True)  # 啟用儲存按鈕

    def save_text(self):
        # 儲存文字到檔案
        file_path, _ = QFileDialog.getSaveFileName(self, "儲存文字", "", "文字檔案 (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.extracted_text)
            print(f"文字已儲存到：{file_path}")


class FullScreenSelection(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("選擇螢幕範圍")
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)

        # 擷取螢幕快照
        self.screenshot = QGuiApplication.primaryScreen().grabWindow(0)
        self.screenshot_label = QLabel(self)
        self.screenshot_label.setPixmap(QPixmap(self.screenshot))
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
        if event.button() == Qt.LeftButton:
            rect = self.rubber_band.geometry()
            self.rubber_band.hide()
            self.parent.set_selected_area(rect)
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

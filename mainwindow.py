import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QRubberBand,QTextEdit
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QPixmap, QGuiApplication, QImage
from full_screen_selection import FullScreenSelection
import pytesseract
from PIL import Image
import time
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螢幕擷取與 OCR 工具")
        self.setGeometry(0, 0, 400, 200)
        
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
        self.area_label = QTextEdit("尚未選擇文字", self)
        self.area_label.setReadOnly(False) 
        layout.addWidget(self.area_label)

        # 按鈕：執行 OCR
        #self.ocr_button = QPushButton("執行 OCR", self)
        #self.ocr_button.clicked.connect(self.run_ocr)
        #self.ocr_button.setEnabled(False)  # 尚未選擇範圍時禁用
        #layout.addWidget(self.ocr_button)

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
        time.sleep(0.2)
        self.fullscreen_window = FullScreenSelection(self)
        self.fullscreen_window.show()

    def set_selected_area(self, rect):
        self.selected_area = rect
        #self.area_label.setText(f"選擇的範圍：x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}")
        #self.ocr_button.setEnabled(True)  # 啟用 OCR 按鈕
        self.show()

    pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"
    def run_ocr(self):
        if not self.selected_area:
            return

        # 擷取選定範圍影像
        screenshot = QGuiApplication.primaryScreen().grabWindow(0)
        cropped = screenshot.copy(self.selected_area)  # 根據選定範圍裁剪

        # 將 QPixmap 轉換為 QImage
        cropped_qimage = cropped.toImage()

        # 將 QImage 轉換為 PIL Image
        width = cropped_qimage.width()
        height = cropped_qimage.height()
        buffer = cropped_qimage.bits().asstring(width * height * 4)  # ARGB 格式的每像素 4 位元組
        image = Image.frombytes("RGBA", (width, height), buffer, "raw", "BGRA")

        # 使用 Tesseract OCR 提取文字
        self.extracted_text = pytesseract.image_to_string(image, lang="eng")# 根據需要更改語言
        self.area_label.setText(self.extracted_text)
        print(f"OCR 提取結果：{self.extracted_text}")


        # 在 GUI 上啟用儲存文字按鈕
        self.save_button.setEnabled(True)


    def save_text(self):
        if not hasattr(self, "extracted_text"):
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "儲存文字", "", "文字檔案 (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.extracted_text)
            print(f"文字已儲存到：{file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

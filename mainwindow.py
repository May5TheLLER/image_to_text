import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog, QRubberBand,QTextEdit,QComboBox
from PyQt5.QtCore import QRect, Qt,QTimer
from PyQt5.QtGui import QPixmap, QGuiApplication, QImage
from full_screen_selection import FullScreenSelection
from pix2tex.cli import LatexOCR
import pytesseract
from PIL import Image
import time
import os
import keyboard
import requests


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螢幕擷取與 OCR 工具")
        self.setGeometry(0, 0, 400, 200)
        
        # 初始化 UI
        self.init_ui()

        # 範圍選擇的相關屬性
        self.selected_area = None
        self.iscontinuous = False

    def init_ui(self):
        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # 按鈕：選擇螢幕範圍
        self.select_area_button = QPushButton("選擇螢幕範圍", self)
        self.select_area_button.clicked.connect(self.start_screen_selection)
        layout.addWidget(self.select_area_button)

        #設定下拉選單
        self.select_lang = QComboBox(self)
        self.select_lang.addItem("英文 (eng)", "eng")
        self.select_lang.addItem("日文 (jpn)", "jpn")
        self.select_lang.addItem("繁體中文 (chi_tra)", "chi_tra")
        self.select_lang.addItem("簡體中文 (chi_sim)", "chi_sim")
        self.select_lang.addItem("數學公式 (Latex)", "Latex")
        layout.addWidget(self.select_lang)

        # 標籤：顯示選擇的範圍資訊
        self.area_label = QTextEdit("尚未選擇文字", self)
        self.area_label.setReadOnly(False) 
        layout.addWidget(self.area_label)

        self.translate_label = QTextEdit("翻譯結果將顯示於此", self)
        self.translate_label.setReadOnly(False) 
        layout.addWidget(self.translate_label)

        # 按鈕：執行 OCR
        #self.ocr_button = QPushButton("執行 OCR", self)
        #self.ocr_button.clicked.connect(self.run_ocr)
        #self.ocr_button.setEnabled(False)  # 尚未選擇範圍時禁用
        #layout.addWidget(self.ocr_button)




        # 按鈕：持續抓取文字
        self.continuous_button = QPushButton("持續抓取範圍文字", self)
        self.continuous_button.clicked.connect(self.start_continuous_mode)
        layout.addWidget(self.continuous_button)

        # 設定佈局
        central_widget.setLayout(layout)

    def start_screen_selection(self):
        # 進入範圍選擇模式，隱藏主視窗
        self.hide()
        time.sleep(0.2)
        self.iscontinuous = False
        self.fullscreen_window = FullScreenSelection(self)
        self.fullscreen_window.show()

    def set_selected_area(self, rect):
        self.selected_area = rect
        #self.area_label.setText(f"選擇的範圍：x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}")
        #self.ocr_button.setEnabled(True)  # 啟用 OCR 按鈕
        self.show()
    
    def start_continuous_mode(self):
        self.iscontinuous = True
        self.hide()
        time.sleep(0.2)
        self.fullscreen_window = FullScreenSelection(self, continuous_mode=True)
        self.fullscreen_window.show()
        self.listen_for_shortcut()
        
    def listen_for_shortcut(self):
        """啟動全域鍵盤監聽，確保操作在主執行緒執行"""
        def on_shortcut():
            QTimer.singleShot(0, self.run_ocr)  # 將 run_ocr 移動到主執行緒執行
        keyboard.add_hotkey("/", on_shortcut)
    pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"
    #pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), 'tesseract', 'tesseract.exe')
    def translate_text(self, text, target_language="zh-Hant"):
        """ 使用 Azure 翻譯 API 翻譯 OCR 擷取的文字 """
        
        # 設定 Azure 翻譯 API 相關資訊
        subscription_key = "38CTfjTTgS6XVfUsqPZ6Ud9SGmWQ0oqrkbo1vFSgCIkWPLPg6cysJQQJ99BCAC3pKaRXJ3w3AAAbACOGgvW3"
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        location = "eastasia"  # 根據你的 Azure 服務區域
        
        path = "/translate"
        url = endpoint + path

        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json'
        }
        
        params = {
            'api-version': '3.0',
            'to': target_language  # 目標語言
        }

        body = [{'text': text}]

        response = requests.post(url, params=params, headers=headers, json=body)
        
        if response.status_code == 200:
            translation = response.json()
            translated_text = translation[0]['translations'][0]['text']
            return translated_text
        else:
            print("翻譯 API 請求失敗:", response.text)
            return None
    
    def run_ocr(self):
        selected_lang = self.select_lang.currentData()
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
        if (selected_lang != 'Latex'):
            self.extracted_text = pytesseract.image_to_string(image, lang=selected_lang)# 根據需要更改語言
        elif(selected_lang == 'Latex'):
            #image = image.convert("RGB")
            latex_ocr = LatexOCR()
            self.extracted_text = latex_ocr(image)

        if (self.iscontinuous == True):
            with open("script.txt", "a", encoding="utf-8") as file:
                file.write(self.extracted_text + "\n")


        self.area_label.setText(self.extracted_text)
        print(f"OCR 提取結果：{self.extracted_text}")
        translated_text = self.translate_text(self.extracted_text, "zh-Hant")

        if translated_text and selected_lang != 'Latex':
            self.translate_label.setText(translated_text)
            print(f"翻譯結果：{translated_text}")

        self.ocr_ready = False
        # 在 GUI 上啟用/儲存文字按鈕


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

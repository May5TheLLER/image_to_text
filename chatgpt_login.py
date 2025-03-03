import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class ChatGPTController:
    def __init__(self):
        """ 初始化 ChatGPT 瀏覽器，只在第一次呼叫時開啟 """
        self.driver = None  # 儲存瀏覽器實例
        self.init_browser()  # 開啟 ChatGPT

    def init_browser(self):
        """ 啟動 ChatGPT 瀏覽器並開啟頁面 """
        if self.driver is None:
            print("🔵 啟動 ChatGPT 瀏覽器...")
            self.driver = uc.Chrome()
            self.driver.get("https://chat.openai.com/")

            # 等待 ChatGPT 頁面載入
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "prompt-textarea"))
            )
            print("✅ ChatGPT 準備完成，等待翻譯請求...")

    def send_request(self, text, target_language="繁體中文"):
        """ 傳送翻譯請求到 ChatGPT，並獲取翻譯結果 """

        if self.driver is None:
            print("❌ 瀏覽器未啟動！")
            return "錯誤：瀏覽器未啟動"

        try:
            print(f"✉️ 發送翻譯請求：{text} -> {target_language}")

            # 找到輸入框，輸入翻譯請求
            input_box = self.driver.find_element(By.ID, "prompt-textarea")
            input_box.clear()
            #input_box.send_keys(f"請將以下內容翻譯成 {target_language}:\n{text}")
            input_box.send_keys("請將以下內容翻譯成" + target_language + text)
            input_box.send_keys(Keys.RETURN)

            # 等待 ChatGPT 回應
            time.sleep(10)  # 避免請求太快，讓 ChatGPT 有時間生成回應

            # 抓取最新的回應
            response_divs = self.driver.find_elements(By.CSS_SELECTOR, ".markdown")
            if response_divs:
                translated_text = response_divs[-1].text  # 取得最新的回應
                print(f"✅ 翻譯結果: {translated_text}")
            else:
                translated_text = "未能獲取翻譯內容"

            return translated_text

        except Exception as e:
            print(f"❌ ChatGPT 翻譯錯誤: {e}")
            return "錯誤：無法翻譯"

    def close_browser(self):
        """ 關閉 ChatGPT 瀏覽器 """
        if self.driver:
            print("🔴 關閉 ChatGPT 瀏覽器...")
            self.driver.quit()
            self.driver = None

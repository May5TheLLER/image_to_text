import requests
import json, httpx

def azure_translate_text(text, target_language="zh-Hant"):
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
        
def deeplx_translate_text(text, target_language="ZH"):
    """ 使用 DeepLx 免費 API 進行翻譯 """
    
    # 1️⃣ 設定免費 DeepLx API 端點
    url = "https://api.deeplx.org/translate"  # 免費 API，不需 API 金鑰

    # 2️⃣ 準備請求主體（Request Body）
    data = {
        "text": text,  # 要翻譯的文字
        "source_lang": "auto",  # 自動偵測語言
        "target_lang": target_language.upper()  # 目標語言（例如 "ZH" 代表中文）
    }

    # 3️⃣ 發送 HTTP POST 請求
    try:
        response = requests.post(url, json=data, timeout=5)  # 設定 5 秒超時
        response.raise_for_status()  # 檢查是否請求成功
        translated_text = response.json().get("data", "翻譯失敗")
        return translated_text
    except requests.exceptions.RequestException as e:
        print(f"DeepLx 翻譯錯誤: {e}")
        return None

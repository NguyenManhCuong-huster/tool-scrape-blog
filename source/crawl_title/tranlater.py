from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time
import selenium_driver

def translate_with_selenium(driver, text: str, src_lang: str = 'en', dest_lang: str = 'vi') -> str:
    """
    Dịch văn bản bằng cách điều khiển Google Translate bằng Selenium.

    Parameters:
        text (str): Chuỗi cần dịch.
        src_lang (str): Mã ngôn ngữ nguồn (vd: 'en', 'vi')
        dest_lang (str): Mã ngôn ngữ đích (vd: 'vi', 'en')

    Returns:
        str: Kết quả dịch.
    """
    try:
        driver = selenium_driver.get_chrome_driver()

        # Mở Google Dịch
        url = f"https://translate.google.com/?sl={src_lang}&tl={dest_lang}&text={text}&op=translate"
        driver.get(url)

        # Chờ kết quả dịch xuất hiện
        time.sleep(5)  # Có thể thay bằng WebDriverWait

        # Lấy kết quả dịch
        result_elem = driver.find_element(By.CSS_SELECTOR, 'span[jsname="W297wb"]')
        translated_text = result_elem.text

        driver.quit()
        return translated_text
    except Exception as e:
        return f"[Lỗi dịch bằng Selenium]: {e}"

def translate_once(driver, text: str, src_lang: str = 'auto', dest_lang: str = 'vi', timeout=10) -> str:
    try:
        time.sleep(2)
        # Mã hóa văn bản trong URL
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.google.com/?sl={src_lang}&tl={dest_lang}&text={encoded_text}&op=translate"
        driver.get(url)

        # Chờ kết quả dịch xuất hiện
        time.sleep(3)

        # Chờ có ít nhất 1 phần tử xuất hiện
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[jsname="W297wb"]')))

        # Lấy tất cả các phần tử kết quả
        elements = driver.find_elements(By.CSS_SELECTOR, 'span[jsname="W297wb"]')
        translated_text = " ".join([el.text for el in elements if el.text.strip()])

        return translated_text.strip()
    except Exception as e:
        return f"[Lỗi]: {e}"

    

if __name__ == "__main__":
    driver = selenium_driver.get_chrome_driver()
    print(translate_once(driver, "I love Python.", src_lang="en", dest_lang="vi"))
    print(translate_once(driver, "Ngành IT là gì? Mô tả chi tiết công việc của ngành IT", src_lang="vi", dest_lang="en"))
    driver.quit()

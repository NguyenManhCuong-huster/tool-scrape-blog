import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException

def get_chrome_driver():
    try:
        # Tính đường dẫn tuyệt đối tới chromedriver dựa theo vị trí file này
        base_path = os.path.dirname(os.path.abspath(__file__))
        chrome_path = os.path.join(base_path, "..//..//chromedriver-win64//chromedriver.exe")

        # Tùy chọn trình duyệt
        options = webdriver.ChromeOptions()
        #options.add_argument("--headless")  # Xóa nếu muốn hiện trình duyệt
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0.7204.101 Safari/537.36")

        # Khởi tạo webdriver
        driver = webdriver.Chrome(service=Service(chrome_path), options=options)
        return driver

    except WebDriverException as e:
        print(f"[!] Lỗi khi khởi tạo ChromeDriver: {e}")
        return None

    except Exception as e:
        print(f"[!] Lỗi không xác định: {e}")
        return None


if __name__ == "__main__":
    
    driver = get_chrome_driver()
    if(driver != None):
        print("ok")
        driver.quit()

    else: print("@@")
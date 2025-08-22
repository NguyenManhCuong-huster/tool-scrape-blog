from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import time
import selenium_driver

def translate_once(driver, text: str, src_lang: str = 'auto', dest_lang: str = 'vi', timeout=10) -> str:
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
        time.sleep(2)
        # Mã hóa văn bản trong URL
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.google.com/?sl={src_lang}&tl={dest_lang}&text={encoded_text}&op=translate"
        driver.get(url)

        # Chờ kết quả dịch xuất hiện
        time.sleep(8)

        # Chờ có ít nhất 1 phần tử xuất hiện
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[jsname="W297wb"]')))

        # Lấy tất cả các phần tử kết quả
        elements = driver.find_elements(By.CSS_SELECTOR, 'span[jsname="W297wb"]')
        translated_text = " ".join([el.text for el in elements if el.text.strip()])

        return translated_text.strip()
    except Exception as e:
        return f"[Lỗi]: {e}"

import pandas as pd
import time
import os
from googletrans import Translator

def translate_with_googletrans(text: str) -> str:
    translator = Translator()
    try:
        result = translator.translate(text, src='vi', dest='en')
        return result.text
    except Exception as e:
        print("Lỗi khi dịch:", e)
        return ""

def translate_title_database(input_path, output_path, start, end, batch_size=20, save_every=10, delay=5.0):
    """
    Dịch các title trong khoảng [start, end], mỗi batch có batch_size title.
    Sau mỗi save_every batch -> nối (append) vào file output_path.
    """
    df = pd.read_excel(input_path)
    subset = df.iloc[start:end+1]

    titles = subset["title"].astype(str).tolist()
    ids = subset["_id"].tolist()
    links = subset["link"].tolist()

    results_buffer = []
    batch_counter = 0

    for i in range(0, len(titles), batch_size):
        batch_titles = titles[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        batch_links = links[i:i+batch_size]

        # Ghép text
        text_to_translate = " \n ".join(batch_titles)
        #print(text_to_translate + "\n")
        # Gọi hàm dịch

        #translated_text = translate_once(driver, text_to_translate, src_lang="vi", dest_lang="en")
        translated_text = translate_with_googletrans(text_to_translate)
        #print(translated_text)
        # Tách kết quả
        translated_list = translated_text.split("\n")
        #translated_list = [t.strip(" #") for t in translated_list]
        if len(translated_list) != len(batch_titles):
            print(f"[Cảnh báo] Batch {i//batch_size}: số câu dịch không khớp!")

        # Lưu vào buffer
        for idx in range(len(batch_titles)):
            results_buffer.append({
                "_id": batch_ids[idx],
                "link": batch_links[idx],
                "title_vie": batch_titles[idx],
                "title_eng": translated_list[idx] if idx < len(translated_list) else ""
            })

        batch_counter += 1
        print(f"✔ Đã dịch batch {batch_counter}, tổng {len(results_buffer)} dòng")

        # Nếu đủ số batch, thì append ra file
        if batch_counter % save_every == 0:
            _append_to_excel(output_path, results_buffer)
            print(f"💾 Đã lưu {len(results_buffer)} dòng vào {output_path}")
            results_buffer = []  # reset buffer

        time.sleep(delay)

    # Lưu phần còn lại nếu chưa đủ save_every batch
    if results_buffer:
        _append_to_excel(output_path, results_buffer)
        print(f"💾 Đã lưu phần cuối: {len(results_buffer)} dòng vào {output_path}")

def translate_test_dataset(input_path, output_path, start, end, batch_size=20, save_every=10, delay=5.0):
    """
    Dịch các title trong khoảng [start, end], mỗi batch có batch_size title.
    Sau mỗi save_every batch -> nối (append) vào file output_path.
    """
    df = pd.read_excel(input_path)
    subset = df.iloc[start:end+1]

    titles = subset["title"].astype(str).tolist()
    values = subset["value"].tolist()
    links = subset["link"].tolist()

    results_buffer = []
    batch_counter = 0

    for i in range(0, len(titles), batch_size):
        batch_titles = titles[i:i+batch_size]
        batch_values = values[i:i+batch_size]
        batch_links = links[i:i+batch_size]

        # Ghép text
        text_to_translate = " \n ".join(batch_titles)
        #print(text_to_translate + "\n")
        # Gọi hàm dịch

        #translated_text = translate_once(driver, text_to_translate, src_lang="vi", dest_lang="en")
        translated_text = translate_with_googletrans(text_to_translate)
        #print(translated_text)
        # Tách kết quả
        translated_list = translated_text.split("\n")
        #translated_list = [t.strip(" #") for t in translated_list]
        if len(translated_list) != len(batch_titles):
            print(f"[Cảnh báo] Batch {i//batch_size}: số câu dịch không khớp!")

        # Lưu vào buffer
        for idx in range(len(batch_titles)):
            results_buffer.append({
                "value": batch_values[idx],
                "link": batch_links[idx],
                "title_vie": batch_titles[idx],
                "title_eng": translated_list[idx] if idx < len(translated_list) else ""
            })

        batch_counter += 1
        print(f"✔ Đã dịch batch {batch_counter}, tổng {len(results_buffer)} dòng")

        # Nếu đủ số batch, thì append ra file
        if batch_counter % save_every == 0:
            _append_to_excel(output_path, results_buffer)
            print(f"💾 Đã lưu {len(results_buffer)} dòng vào {output_path}")
            results_buffer = []  # reset buffer

        time.sleep(delay)

    # Lưu phần còn lại nếu chưa đủ save_every batch
    if results_buffer:
        _append_to_excel(output_path, results_buffer)
        print(f"💾 Đã lưu phần cuối: {len(results_buffer)} dòng vào {output_path}")


def _append_to_excel(file_path, data_list):
    new_df = pd.DataFrame(data_list)
    if os.path.exists(file_path):
        old_df = pd.read_excel(file_path)
        combined = pd.concat([old_df, new_df], ignore_index=True)
    else:
        combined = new_df
    combined.to_excel(file_path, index=False)

if __name__ == "__main__":
    from selenium import webdriver

    #driver = webdriver.Chrome()
    #driver.get("https://translate.google.com")
    '''
    translate_title_database(
        input_path="blog_list.xlsx",
        output_path="translated6.xlsx",
        #driver=driver,
        start=0,
        end=5622,       
        batch_size=40, # mỗi batch 10 title
        save_every=10, # cứ 10 batch thì lưu nối vào file
        delay=10        # delay 5s giữa mỗi batch
    )
    '''

    translate_test_dataset(
        input_path="train/test_dataset.xlsx",
        output_path="train/tranlated_test_dataset.xlsx",
        #driver=driver,
        start=0,
        end=973,       
        batch_size=30, # mỗi batch 10 title
        save_every=10, # cứ 10 batch thì lưu nối vào file
        delay=10        # delay 5s giữa mỗi batch
    )

    #driver.quit()
    
    #input_text = '''Cách viết đúng giấy ủy quyền lấy sổ bảo hiểm xã hội # Food stylist là gì? Khám phá nghề làm đẹp cho ẩm thực # SHL test là gì? Mẹo vượt qua SHL test hiệu quả nhất # So sánh trợ cấp thôi việc và trợ cấp thất nghiệp # Bí quyết tìm việc hiệu quả cho người tìm việc làm tuổi 50 # Nên nghỉ việc trước Tết hay sau Tết? Tìm lựa chọn tốt nhất # Cập nhật thông tin chi tiết về mức lương ngành dược # Email blast là gì? Cách triển khai email blast hiệu quả # Tổng hợp các cách chuyển CAD sang Word nhanh, hiệu quả # Tìm hiểu event concept là gì? Cách tổ chức concept sự kiện # Lead Scoring là gì? Cách triển khai lead scoring hiệu quả # Câu hỏi phỏng vấn nhân viên nhà hàng dễ dược hỏi # Trả lời câu hỏi phỏng vấn quản lý dự án tạo ấn tượng đột phá # Chi tiết về chương trình du học nghề điều dưỡng tại Đức # Kinh Nghiệm Phỏng Vấn Vị Trí IT Cho Sinh Viên Mới Ra Trường # Top những công việc part time buổi sáng phù hợp nên làm # Bí Quyết Tìm Việc Làm Thêm Ở Giảng Võ Hà Nội Dễ Dàng Chỉ Với Một Click # Bí kíp sở hữu việc làm tại Đà Nẵng facebook uy tín nhất # Tìm Việc Làm Nấu Ăn Tại Đà Nẵng Dễ Dàng - Bí Quyết Tìm Việc Tốt Nhất # Mở rộng cơ hội việc làm bán hàng Biên Hòa cùng Timviec365
    #            '''
    #translated_text = translate_with_googletrans(input_text)
    #print("Dịch sang tiếng Anh:", translated_text)
    

from source.crawl_title import crawl_title_from_link, filter_title, selenium_driver
import pandas as pd

def save_keys_to_excel(keys, output_path="filtered_keys.xlsx"):
    """
    Lưu danh sách kết quả (list of dict) vào file Excel.

    Mỗi item trong results phải có các key: 'link', 'title', 'keyword'
    """
    if not keys:
        print("⚠️ Không có kết quả nào để lưu.")
        return

    df = pd.DataFrame(keys)
    df.to_excel(output_path, index=False)
    print(f"✅ Đã lưu {len(keys)} kết quả vào: {output_path}")

def save_titles_to_excel(data, filename="output.xlsx"):
    df = pd.DataFrame(data)  # Chuyển list thành DataFrame
    df.to_excel(filename, index=False)  # Lưu file Excel (không thêm số thứ tự)

def load_urls_from_txt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls


def remove_duplicate_titles(file_path):
    # Đọc file Excel
    try:
        df = pd.read_excel(file_path)

        # Kiểm tra xem có cột 'title' không
        if 'title' not in df.columns:
            print("❌ Cột 'title' không tồn tại trong file.")
            return

        # Xóa các dòng có title trùng nhau, giữ lại dòng đầu tiên
        df_unique = df.drop_duplicates(subset='title', keep='first')

        # Ghi đè lên file Excel cũ
        df_unique.to_excel(file_path, index=False)
        print(f"✅ Đã loại bỏ {len(df) - len(df_unique)} dòng trùng 'title'. File đã được cập nhật.")

    except Exception as e:
        print(f"❌ Lỗi khi xử lý file: {e}")


def main():
    # Mã chạy chính nằm ở đây
    urls = load_urls_from_txt("input.txt")
    all_raw_titles = []
    

    for url in urls:
        driver = selenium_driver.get_chrome_driver()
        print("Lấy title từ URL: " + url)
        raw_titles = crawl_title_from_link.extract_link_info_form_url(url, driver)
        if raw_titles == []:
            print("không lấy được blog từ URL này: " + str(url))
            driver.quit()
            continue
        

        
        all_raw_titles += raw_titles

        driver.quit()
        """
        print("Đang lấy keys ...")
        keys = extract_key_word.extract_keywords_from_list(filted_titles)
        if keys == None:
            print("Danh sách key rỗng")
            return
        
        print("Đang lưu keys ...")
        save_keys_to_excel(keys)
        print("Lấy keys thành công.")
        """
    save_titles_to_excel(all_raw_titles, "raw.xlsx")
    
    print("Đang lọc title ...")
    filted_titles = filter_title.filter_similar_title(all_raw_titles)
    if filted_titles == []:
        print("Danh sách title sau khi lọc rỗng")
    
    save_titles_to_excel(filted_titles)

    remove_duplicate_titles("output.xlsx")

    
if __name__ == "__main__":
    main()
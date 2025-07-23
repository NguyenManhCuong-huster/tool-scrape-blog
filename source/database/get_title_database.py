import os
import pandas as pd
import requests
from dotenv import load_dotenv

# === Thiết lập đường dẫn tương đối theo vị trí file này ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def rel_path(*parts):
    return os.path.join(BASE_DIR, *parts)

# === Hàm 1: Gọi API lấy dữ liệu ===
def fetch_blog_data(from_date, to_date):
    load_dotenv(dotenv_path=rel_path("../../.env"))

    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    payload = {
        "fromdate": from_date,
        "todate": to_date,
        "key": api_key
    }

    res = requests.post(api_url, json=payload)

    if res.status_code == 200:
        json_data = res.json()
        blog_items = json_data.get("data", {}).get("data", [])
        results = []

        for item in blog_items:
            _id = item.get("_id")
            title = item.get("new_title")
            link = item.get("link")
            if _id and title and link:
                results.append({
                    "_id": _id,
                    "title": title,
                    "link": link
                })

        return results
    else:
        raise Exception(f"API lỗi: {res.status_code}")

# === Hàm 2: Lưu kết quả ra Excel tạm ===
def save_blog_data(data, filename="blog_list_new.xlsx"):
    df = pd.DataFrame(data)
    df.to_excel(rel_path("../../database", filename), index=False, engine='openpyxl')

# === Hàm 3: Nối file mới + cũ, rồi ghi đè lại file chính ===
def merge_and_save(old_file="blog_list.xlsx", new_file="blog_list_new.xlsx"):
    path_old = rel_path("../../database", old_file)
    path_new = rel_path("../../database", new_file)

    df_old = pd.read_excel(path_old)
    df_new = pd.read_excel(path_new)

    df_combined = pd.concat([df_old, df_new], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset='link', keep='first')

    df_combined.to_excel(path_old, index=False)
    print("✅ Đã nối và cập nhật dữ liệu vào", old_file)

# === Hàm tổng: chạy toàn bộ quy trình ===
def run_full_pipeline():
    try:
        #to_date là lần cuối cập nhật database, chỉ cần đổi from_date = to_date, to_date = timestamp hiện tại
        data = fetch_blog_data(from_date=1752461999, to_date=1752639951)
        print(f"🔹 Lấy được {len(data)} bài viết từ API.")
        save_blog_data(data)
        merge_and_save()
    except Exception as e:
        print("❌ Lỗi:", e)

# === Nếu muốn chạy trực tiếp file này ===
if __name__ == "__main__":
    run_full_pipeline()

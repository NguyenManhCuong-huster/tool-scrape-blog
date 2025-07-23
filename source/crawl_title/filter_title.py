import pandas as pd
from sentence_transformers import SentenceTransformer, util
# Load model
model = SentenceTransformer('model/paraphrase-multilingual-MiniLM-L12-v2')

# Đọc tiêu đề blog từ file
import os
import pandas as pd

#Đọc title trong DB
def load_title_embeddings(excel_path="..//..//database//blog_list.xlsx"):
    # Tính đường dẫn tuyệt đối dựa trên vị trí file hiện tại
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, excel_path)

    df = pd.read_excel(full_path)
    titles = df["title"].dropna().tolist()
    embeddings = model.encode(titles, convert_to_tensor=True)
    return embeddings


#Hàm lọc title
def filter_similar_title(items, threshold=0.6):
    title_embeddings = load_title_embeddings()
    filtered = []

    for item in items:
        text = item.get("title", "").strip()
        if not text:
            continue

        text_embedding = model.encode(text, convert_to_tensor=True)

        # So sánh từng dòng embedding title, dừng khi gặp điểm cosine > threshold
        found_similar = False
        for title_embedding in title_embeddings:
            score = util.cos_sim(text_embedding, title_embedding).item()
            if score >= threshold:
                found_similar = True
                break

        if not found_similar:
            filtered.append(item)
        # else: print(f"Loại: {text[:60]} (score={score:.2f})")

    return filtered


# Phần này chỉ để điều chỉnh tham số, ko liên quan luồng
def filter_similar_title_with_removed(items, threshold=0.5):
    title_embeddings = load_title_embeddings()
    filtered = []
    removed = []

    for item in items:
        text = item.get("title", "").strip()
        if not text:
            continue

        text_embedding = model.encode(text, convert_to_tensor=True)

        found_similar = False
        for title_embedding in title_embeddings:
            score = util.cos_sim(text_embedding, title_embedding).item()
            if score >= threshold:
                found_similar = True
                break

        if not found_similar:
            filtered.append(item)
        else:
            removed.append(item)

    return filtered, removed

def process_excel_and_filter(
    input_path,
    output_path_kept='filtered_kept60.xlsx',
    output_path_removed='filtered_removed60.xlsx',
    threshold=0.5
):
    df = pd.read_excel(input_path)
    items = df.to_dict(orient='records')

    # Lọc
    filtered_items, removed_items = filter_similar_title_with_removed(items, threshold=threshold)

    # Ghi 2 file Excel
    pd.DataFrame(filtered_items).to_excel(output_path_kept, index=False)
    pd.DataFrame(removed_items).to_excel(output_path_removed, index=False)

    # In thống kê
    total = len(items)
    kept = len(filtered_items)
    removed = len(removed_items)
    print(f"✅ Tổng: {total} | Giữ lại: {kept} | Bị loại: {removed} ")
    print(f"📁 Đã lưu: '{output_path_kept}' và '{output_path_removed}'")

if __name__ == "__main__":
    process_excel_and_filter('output.xlsx', threshold=0.60)
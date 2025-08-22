import pandas as pd
from sentence_transformers import SentenceTransformer, util
import os

# Load model
base_path = os.path.dirname(os.path.abspath(__file__))  # đang ở source/crawl_title/
model_path = os.path.join(base_path, '..', '..', 'model', 'all-mpnet-base-v2')  # Tính đường dẫn tuyệt đối đến thư mục lưu model
model = SentenceTransformer(model_path)

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


def load_eng_title_embeddings(excel_path="..//..//train//eng_blog_list.xlsx"):
    # Tính đường dẫn tuyệt đối dựa trên vị trí file hiện tại
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, excel_path)

    df = pd.read_excel(full_path)
    titles = df["title_eng"].dropna().tolist()
    embeddings = model.encode(titles, convert_to_tensor=True)
    return embeddings

#Hàm lọc title
def filter_similar_eng_title(items, threshold=0.6):
    title_embeddings = load_eng_title_embeddings()
    filtered = []

    for item in items:
        text = item.get("title_eng", "").strip()
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

def excel_to_list(filename="..//..//train//test_dataset.xlsx"):
    df = pd.read_excel(filename)
    items = df.to_dict(orient='records')
    return items

def save_titles_to_excel(data, filename="output.xlsx"):
    df = pd.DataFrame(data)  # Chuyển list thành DataFrame
    df.to_excel(filename, index=False)  # Lưu file Excel (không thêm số thứ tự)

def test_accuracy():
    import pandas as pd
    from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

    # ===== 1. Đọc dữ liệu =====
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, "..//..//train//eng_test_dataset.xlsx")
    df = pd.read_excel(full_path)  # cột: title, value ('t','f')

    # Ground truth
    y_true = df['value'].map({'f': 1, 't': 0})  # f=1, t=0

    # ===== 2. Gọi hàm lọc =====
    items = df.to_dict(orient='records')
    filtered = filter_similar_eng_title(items, threshold=0.45)  # hàm của bạn
    filtered_titles = set(item["title_eng"] for item in filtered)

    save_titles_to_excel(filtered_titles, "eng_filtered_title.xlsx")

    # ===== 3. Tạo vector dự đoán =====
    y_pred = df['title_eng'].apply(lambda x: 1 if x in filtered_titles else 0)

    # ===== 4. Metrics =====
    acc  = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec  = recall_score(y_true, y_pred)
    f1   = f1_score(y_true, y_pred)
    cm   = confusion_matrix(y_true, y_pred)

    print("Confusion Matrix:\n", cm)
    print(f"Accuracy : {acc:.3f}")
    print(f"Precision: {prec:.3f}")
    print(f"Recall   : {rec:.3f}")
    print(f"F1-score : {f1:.3f}")

    # ===== 5. Log chi tiết =====
    df['y_true'] = y_true
    df['y_pred'] = y_pred

    # False Positives: dự đoán f (1) nhưng thực tế là t (0)
    fp = df[(df['y_true'] == 0) & (df['y_pred'] == 1)]
    print("\n--- False Positives (FP): Hàm giữ lại nhưng thực ra đã có trong DB ---")
    print(fp[['title_eng', 'value']])

    # False Negatives: dự đoán t (0) nhưng thực tế là f (1)
    fn = df[(df['y_true'] == 1) & (df['y_pred'] == 0)]
    print("\n--- False Negatives (FN): Hàm loại bỏ nhưng thực ra chưa có trong DB ---")
    print(fn[['title_eng', 'value']])


if __name__ == "__main__":
    test_accuracy()
import os
from sentence_transformers import SentenceTransformer

def download_and_save_model():
    # Tính đường dẫn tuyệt đối đến thư mục lưu model
    base_path = os.path.dirname(os.path.abspath(__file__))  # đang ở source/download_model/
    model_path = os.path.join(base_path, '..', '..', 'model', 'gte-large')  # đi lên 2 cấp

    # Nếu model đã tồn tại thì không tải lại
    if os.path.exists(model_path) and os.path.isfile(os.path.join(model_path, 'config.json')):
        print(f"✅ Model đã tồn tại ở: {model_path}")
        return

    print("⬇️ Đang tải model từ Hugging Face...")
    model = SentenceTransformer('thenlper/gte-large')
    model.save(model_path)
    print(f"✅ Đã lưu model vào: {model_path}")

# Gọi hàm nếu chạy trực tiếp
if __name__ == "__main__":
    download_and_save_model()


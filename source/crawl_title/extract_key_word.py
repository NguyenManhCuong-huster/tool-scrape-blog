from keybert import KeyBERT
import tranlater
import os
from sentence_transformers import SentenceTransformer
from selenium_driver import get_chrome_driver


# ✅ Load model 1 lần
#kw_model = KeyBERT("paraphrase-multilingual-MiniLM-L12-v2")
#kw_model = KeyBERT("all-MiniLM-L6-v2")


# Đang ở source/crawl_title/
base_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_path, '..', '..', 'model', 'all-mpnet-base-v2')

# Load SentenceTransformer từ local
st_model = SentenceTransformer(model_path)

# Truyền model này vào KeyBERT
kw_model = KeyBERT(model=st_model)

def clean_sentence(sentence: str) -> str:
    # Bỏ phần [abc] ở đầu title nếu có
    sentence = re.sub(r"\[.*?\]\s*", "", sentence)
    # thêm khoảng trắng sau mọi ký tự đặc biệt (bất kỳ ký tự nào KHÔNG phải chữ/số/khoảng trắng)
    return re.sub(r"([,.;:/?!\\()\"'-])([^\s])", r"\1 \2", sentence)

def extract_best_keyword(text: str, threshold, max_range=4):
    """
    Trích cụm từ khóa ngắn nhất có cosine ≥ threshold
    """
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, max_range),
        stop_words=None,
        top_n=20,
        use_mmr=True,
        diversity=0.7
    )
    
    candidates = [kw for kw in keywords if kw[1] >= threshold]
    if not candidates:
        return ""
    
    candidates.sort(key=lambda x: len(x[0].split()))
    return candidates[0][0]

def extract_keywords_from_list(items):
    """
    Trích keyword từ từng text
    Trả về list gồm {link, keyword}
    """
    results = []

    for item in items:
        text = item.get('text', '')
        link = item.get('link', '')
        print("Lấy key của :"+text)
        #text_eng = tranlater.translate_with_googletrans(text)
        #print("text_eng: " + text_eng)
        
        text = clean_sentence(text)
        len_text=len(text.strip().split())
        print(text)
        if text and link:
            raw_text = text
            #Bỏ phần [abc] ở đầu
            text = re.sub(r"\[.*?\]\s*", "", raw_text)
            keyword = "" 
            for th in [0.95, 0.85, 0.75, 0.55]:
                for mr in [2, 4, 8]:
                    mr = min(mr, len_text)
                    keyword = extract_best_keyword(text, th, mr)
                    if keyword:  # nếu tìm được thì dừng
                        break
                if keyword:  # nếu tìm được thì dừng
                    break

        results.append({
            "text": text,
            "keyword": keyword
        })

    return results

import pandas as pd
import re

def extract_keywords_of_dataset(input_file: str, output_file: str):
    """
    Đọc file Excel (input_file: absolute path), trích keyword cho title_eng,
    và lưu kết quả ra output_file (absolute path).
    """
    # Đọc file excel
    df = pd.read_excel(input_file)

    results = []
    for _, row in df.iterrows():
        raw_text = str(row['title_eng'])
        text =clean_sentence(raw_text)
        len_text=len(text.strip().split())
        keyword = ""

        # Thử lần lượt threshold 0.9, 0.8, 0.7
        for th in [0.95, 0.85, 0.75]:
            for mr in [2, 4, 8]:
                mr = min(mr, len_text)
                keyword = extract_best_keyword(text, th, mr)
                if keyword:  # nếu tìm được thì dừng
                    break
            if keyword:  # nếu tìm được thì dừng
                    break
        
        print(text)
        print(keyword)

        results.append({
            "value": row['value'],
            "link": row['link'],
            "title_vie": row['title_vie'],
            "title_eng": row['title_eng'],
            "keyword": keyword
        })

    # Xuất ra Excel
    result_df = pd.DataFrame(results)
    result_df.to_excel(output_file, index=False)
    print(f"✅ Đã lưu kết quả vào {output_file}")



if __name__ == "__main__":
    result = [
        {
            "link": "https://example.com/blog-1",
            "text": "What is F&B?Discover 9 parts in F&B industry"
        },
        {
            "link": "https://example.com/blog-4",
            "text": "What is Cash in Advance?Discover the 4 -step operation mechanism of the CIA"
        }
    ]

    keys = extract_keywords_from_list(result)
    print(keys)

    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_path, '..', '..'))

    input_file = os.path.join(project_root, 'train', 'eng_test_dataset.xlsx')
    output_file = os.path.join(project_root, 'train', 'eng_test_dataset_with_keywords3.xlsx')

    extract_keywords_of_dataset(input_file, output_file)
    """
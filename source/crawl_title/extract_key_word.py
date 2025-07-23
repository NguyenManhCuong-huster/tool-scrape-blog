from keybert import KeyBERT
from tranlater import translate_once
from selenium_driver import get_chrome_driver
# ✅ Load model 1 lần
#kw_model = KeyBERT("paraphrase-multilingual-MiniLM-L12-v2")
kw_model = KeyBERT("all-MiniLM-L6-v2")


def extract_best_keyword(text: str, threshold):
    """
    Trích cụm từ khóa ngắn nhất có cosine ≥ threshold
    """
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(2, min(9, len(text.split()) // 2)),
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

    driver = get_chrome_driver()

    for item in items:
        text = item.get('text', '')
        link = item.get('link', '')
        print("Lấy key của :"+text)
        text_eng = translate_once(driver, text = text, src_lang="vi", dest_lang="en")
        print("text_eng: " + text_eng)

        if text and link:
            for t in [0.9, 0.8, 0.7]:
                keyword = extract_best_keyword(text_eng, t)
                if keyword:
                    print("key: " + keyword)
                    key_vie = translate_once(driver, text = keyword, src_lang="en", dest_lang="vi")
                    print("key_vie: " + key_vie)
                    results.append({
                        'link': link,
                        'title':text,
                        'key_vi': key_vie,
                        'key_en':keyword
                    })
                    break  # ✅ Dừng lại nếu đã có keyword

    driver.quit()  # Sau khi dịch xong

    return results

if __name__ == "__main__":
    result = [
        {
            "link": "https://example.com/blog-1",
            "text": "Ngành IT là gì? Mô tả chi tiết công việc của ngành IT"
        },
        {
            "link": "https://example.com/blog-4",
            "text": "Top 18 câu hỏi phỏng vấn tiếng Trung thường gặp hiện nay"
        }
    ]

    keys = extract_keywords_from_list(result)
    print(keys)
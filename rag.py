from pathlib import Path
import re

# 1. تحميل المستندات وتقسيمها لفقرات كاملة
def load_docs(folder="documents"):
    docs = {}
    for f in Path(folder).glob("*.txt"):
        docs[f.name] = f.read_text(encoding="utf-8")
    return docs

docs_data = load_docs()

def get_collection():
    return None

def normalize_arabic(text):
    # تنظيف النص العربي وتوحيد الأحرف (الألف، التاء المربوطة)
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    return text.lower()

# 2. البحث الذكي المحسّن للغة العربية
def ask(question):
    q_clean = question.strip().lower()

    # قائمة الرفض المباشر للأسئلة الشخصية والخارجية
    unrelated_patterns = ["اسمي", "اسمى", "عمري", "عمرى", "مين انا", "من انا", "بتول", "الطقس", "كأس العالم"]
    if any(pattern in q_clean for pattern in unrelated_patterns):
        return "I don't know.", []

    # استخراج الكلمات الأساسية وتبسيطها
    words = [normalize_arabic(w) for w in re.findall(r'\w+', q_clean) if len(w) > 2]
    
    if not words:
        return "I don't know.", []

    best_chunk = None
    best_source = None
    max_score = 0

    # البحث في كل فقرة عن أفضل نسبة تطابق
    for doc_name, text in docs_data.items():
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 10]
        
        for p in paragraphs:
            p_norm = normalize_arabic(p)
            score = 0
            
            for word in words:
                # إذا كانت الكلمة أو جذرها موجود في الفقرة نزيد النقاط
                if word in p_norm:
                    score += 2
                elif len(word) > 3 and word[:4] in p_norm:  # مطابقة البدايات للجذور
                    score += 1
            
            if score > max_score:
                max_score = score
                best_chunk = p
                best_source = doc_name.replace(".txt", "")

    # يشترط وجود حد أدنى من التطابق لضمان صحة الإجابة
    if max_score >= 2 and best_chunk:
        return best_chunk, [best_source]

    return "I don't know.", []
import os
import re
import math
import pymorphy3
from collections import Counter

TFIDF_DIR = "tf-idf-lemmas"
INDEX_FILE = "index.txt"

def load_index():
    """Загружает ссылки на документы по их id"""
    doc_urls = {}
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                doc_urls[int(parts[0])] = parts[1]
    return doc_urls

def load_doc_vectors():
    """Считывает tf-idf векторы документов, предвычисляет их нормы и словарь idf"""
    doc_vectors = {}
    doc_norms = {}
    idf_dict = {}
    
    for filename in os.listdir(TFIDF_DIR):
        if not filename.endswith('.txt'):
            continue
        doc_id = int(filename.split('.')[0])
        vector = {}
        norm_sq = 0.0
        
        with open(os.path.join(TFIDF_DIR, filename), 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    lemma = parts[0]
                    idf = float(parts[1])
                    tfidf = float(parts[2])
                    
                    vector[lemma] = tfidf
                    norm_sq += tfidf ** 2
                    
                    if lemma not in idf_dict:
                        idf_dict[lemma] = idf
        
        doc_vectors[doc_id] = vector
        doc_norms[doc_id] = math.sqrt(norm_sq)
    
    return doc_vectors, doc_norms, idf_dict

def process_query(query, idf_dict, morph):
    """Строит вектор запроса по леммам и считает его норму"""
    excluded_pos = {'PREP', 'CONJ', 'PRCL', 'INTJ', 'NUMR'}
    word_pattern = re.compile(r'\b\w+\b')
    cyrillic_pattern = re.compile(r'^[а-яё]+$')
    
    raw_tokens = word_pattern.findall(query)
    lemmas = []
    
    for token in raw_tokens:
        token = token.lower()
        if not cyrillic_pattern.match(token):
            continue
        parsed = morph.parse(token)[0]
        if parsed.tag.POS in excluded_pos:
            continue
        lemmas.append(parsed.normal_form)
    
    if not lemmas:
        return {}, 0.0
    
    counts = Counter(lemmas)
    total = len(lemmas)
    
    query_vector = {}
    norm_sq = 0.0
    for lemma, count in counts.items():
        tf = count / total
        idf = idf_dict.get(lemma, 0.0)
        tfidf = tf * idf
        query_vector[lemma] = tfidf
        norm_sq += tfidf ** 2
    
    return query_vector, math.sqrt(norm_sq)

def vector_search(query_vector, query_norm, doc_vectors, doc_norms):
    """Вычисляет косинусное сходство между запросом и всеми документами"""
    scores = {}
    if query_norm == 0:
        return scores
        
    for doc_id, doc_vector in doc_vectors.items():
        dot_product = sum(query_vector[lemma] * doc_vector[lemma] 
                          for lemma in query_vector if lemma in doc_vector)
        if dot_product > 0:
            scores[doc_id] = dot_product / (query_norm * doc_norms[doc_id])
    
    return scores

def main():
    doc_urls = load_index()
    doc_vectors, doc_norms, idf_dict = load_doc_vectors()
    morph = pymorphy3.MorphAnalyzer()
    
    while True:
        try:
            query = input("\nВведите запрос (или 'exit' для выхода): ")
        except EOFError:
            break
        
        if query.strip().lower() == 'exit':
            break
        
        q_vec, q_norm = process_query(query, idf_dict, morph)
        if q_norm == 0:
            print("Нет значимых слов в запросе.")
            continue
        
        scores = vector_search(q_vec, q_norm, doc_vectors, doc_norms)
        if not scores:
            print("Ничего не найдено.")
            continue
        
        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\nТоп {len(top)} результатов:")
        for rank, (doc_id, score) in enumerate(top, 1):
            url = doc_urls.get(doc_id, "Unknown URL")
            print(f"{rank}. score: {score:.4f} | {url} [{doc_id}]")

if __name__ == '__main__':
    main()
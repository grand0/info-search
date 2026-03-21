import os
import math
import re
from collections import defaultdict, Counter

tfidf_token_path = "tf-idf-tokens"
tfidf_lemma_path = "tf-idf-lemmas"
lemmas_path = "lemmas"
tokens_path = "tokens"


def parse_tokens(file):
    """Retrieve list of tokens from file"""
    with open(file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def parse_lemma_file(file):
    """Retrieve dictionary of lemmas and corresponding words from file"""
    lemma_dict = {}
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                lemma = parts[0]
                words = parts[1:] if len(parts) > 1 else []
                lemma_dict[lemma] = words
    return lemma_dict


def get_token_to_lemma():
    """Build a dictionary of tokens and corresponding lemmas"""
    token_to_lemma = {}
    
    lemma_files = [f for f in os.listdir(lemmas_path) if f.endswith('.txt')]
    lemma_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    for lf in lemma_files:
        filepath = os.path.join(lemmas_path, lf)
        lemma_dict = parse_lemma_file(filepath)
        
        for lemma, tokens in lemma_dict.items():
            for token in tokens:
                token_to_lemma[token] = lemma
    
    return token_to_lemma


def calculate_idf(total_docs, doc_freq):
    """Calculates idf for token"""
    if doc_freq == 0:
        return 0.0
    return math.log(total_docs / doc_freq)


def calculate_token_tfidf():
    """Calculates tf-idf for tokens and saves into files"""
    token_files = [f for f in os.listdir(tokens_path) if f.endswith('.txt')]
    token_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    total_docs = len(token_files)
    
    token_doc_freq = defaultdict(int)
    doc_token_tf = defaultdict(dict)
    
    for doc, token_file in enumerate(token_files, 1):
        file = os.path.join(tokens_path, token_file)
        tokens = parse_tokens(file)
        
        if not tokens:
            continue
            
        token_counter = Counter(tokens)
        total_tokens = len(tokens)
        
        for token, count in token_counter.items():
            doc_token_tf[doc][token] = count / total_tokens
            token_doc_freq[token] += 1
    
    for doc in range(1, total_docs + 1):
        file = os.path.join(tfidf_token_path, f"{doc}.txt")
        
        with open(file, 'w', encoding='utf-8') as f:
            if doc in doc_token_tf:
                for token, tf in doc_token_tf[doc].items():
                    df = token_doc_freq[token]
                    idf = calculate_idf(total_docs, df)
                    tfidf = tf * idf
                    
                    f.write(f"{token} {idf:.6f} {tfidf:.6f}\n")


def calculate_lemma_tfidf():
    """Calculates tf-idf for lemmas and saves into files"""
    token_files = [f for f in os.listdir(tokens_path) if f.endswith('.txt')]
    token_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    total_docs = len(token_files)
    
    token_to_lemma = get_token_to_lemma()
    lemma_doc_freq = defaultdict(int)
    doc_lemma_tf = defaultdict(dict)
    
    for doc, token_file in enumerate(token_files, 1):
        file = os.path.join(tokens_path, token_file)
        tokens = parse_tokens(file)
        
        if not tokens:
            continue
            
        total_tokens = len(tokens)
        lemma_counter = Counter()
        
        for token in tokens:
            lemma = token_to_lemma.get(token, token)
            lemma_counter[lemma] += 1
            
        for lemma, count in lemma_counter.items():
            doc_lemma_tf[doc][lemma] = count / total_tokens
            lemma_doc_freq[lemma] += 1
    
    for doc in range(1, total_docs + 1):
        file = os.path.join(tfidf_lemma_path, f"{doc}.txt")
        
        with open(file, 'w', encoding='utf-8') as f:
            if doc in doc_lemma_tf:
                for lemma, tf in doc_lemma_tf[doc].items():
                    df = lemma_doc_freq[lemma]
                    idf = calculate_idf(total_docs, df)
                    tfidf = tf * idf
                    
                    f.write(f"{lemma} {idf:.6f} {tfidf:.6f}\n")


if __name__ == "__main__":
    os.makedirs(tfidf_token_path, exist_ok=True)
    os.makedirs(tfidf_lemma_path, exist_ok=True)
    calculate_token_tfidf()
    calculate_lemma_tfidf()

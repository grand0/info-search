import os
import math
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

tfidf_token_path = "tf-idf-tokens"
tfidf_lemma_path = "tf-idf-lemmas"
lemmas_path = "lemmas"
tokens_path = "tokens"


def parse_tokens(file):
    """
    Retrieve list of tokens from file
    """
    with open(file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def parse_lemma_file(file):
    """
    Retrieve dictionary of lemmas and corresponding words from file
    """
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
    """
    Build a dictionary of tokens and corresponding lemmas
    """
    token_to_lemma = {}
    lemma_files = sorted([f for f in os.listdir(lemmas_path) if f.endswith('.txt')], key=lambda x: int(x.split('.')[0]))
    
    for lf in lemma_files:
        filepath = os.path.join(lemmas_path, lf)
        lemma_dict = parse_lemma_file(filepath)
        
        for lemma, tokens in lemma_dict.items():
            for token in tokens:
                token_to_lemma[token] = lemma
    
    return token_to_lemma


def calculate_idf(total_docs, doc_freq):
    """
    Calculates idf for token
    """
    if doc_freq == 0:
        return 0.0
    return math.log(total_docs / doc_freq)


def calculate_token_tfidf():
    """
    Calculates tf-idf for tokens and saves into files
    """
    token_files = sorted([f for f in os.listdir(tokens_path) if f.endswith('.txt')])
    total_docs = len(token_files)
    
    token_doc_freq = defaultdict(int)
    token_tf = defaultdict(dict)
    
    # get token tf
    for doc, token_file in enumerate(token_files, 1):
        file = os.path.join(tokens_path, token_file)
        tokens = parse_tokens(file)
            
        token_counter = Counter(tokens)
        for token, count in token_counter.items():
            tf = count / len(tokens)
            token_tf[token][doc] = tf
    
    # get token document frequency
    for doc, token_file in enumerate(token_files, 1):
        file = os.path.join(tokens_path, token_file)
        tokens = parse_tokens(file)
        
        for token in tokens:
            token_doc_freq[token] += 1
    
    # save results
    for doc in range(1, total_docs + 1):
        file = os.path.join(tfidf_token_path, f"{doc}.txt")
        
        with open(file, 'w', encoding='utf-8') as f:
            for token, doc_tfs in token_tf.items():
                if doc in doc_tfs:
                    tf = doc_tfs[doc]
                    df = token_doc_freq[token]
                    idf = calculate_idf(total_docs, df)
                    tfidf = tf * idf
                    
                    f.write(f"{token} {idf:.6f} {tfidf:.6f}\n")

def calculate_lemma_tfidf():
    """
    Calculates tf-idf for lemmas and saves into files
    """
    token_files = sorted([f for f in os.listdir(tokens_path) if f.endswith('.txt')])
    total_docs = len(token_files)
    
    token_to_lemma = get_token_to_lemma()
    lemma_doc_freq = defaultdict(int)
    lemma_tf = defaultdict(dict)
    
    # gather lemma occurrences in documents
    lemma_occurrences = defaultdict(lambda: defaultdict(int))
    doc_token_counts = {}
    
    for doc, token_file in enumerate(token_files, 1):
        file = os.path.join(tokens_path, token_file)
        tokens = parse_tokens(file)
        doc_token_counts[doc] = len(tokens)
        
        # group tokens by lemmas
        for token in tokens:
            if token in token_to_lemma:
                lemma = token_to_lemma[token]
                lemma_occurrences[lemma][doc] += 1
            else:
                lemma_occurrences[token][doc] += 1
    
    # calculate tf for lemmas
    for lemma, doc_counts in lemma_occurrences.items():
        for doc, count in doc_counts.items():
            tf = count / doc_token_counts[doc]
            lemma_tf[lemma][doc] = tf
    
    # calculate df for lemmas
    for lemma, doc_counts in lemma_occurrences.items():
        lemma_doc_freq[lemma] = len(doc_counts)
    
    # save results
    for doc in range(1, total_docs + 1):
        file = os.path.join(tfidf_lemma_path, f"{doc}.txt")
        
        with open(file, 'w', encoding='utf-8') as f:
            for lemma, doc_tfs in lemma_tf.items():
                if doc in doc_tfs:
                    tf = doc_tfs[doc]
                    df = lemma_doc_freq[lemma]
                    idf = calculate_idf(total_docs, df)
                    tfidf = tf * idf
                    
                    f.write(f"{lemma} {idf:.6f} {tfidf:.6f}\n")

if __name__ == "__main__":
	os.makedirs(tfidf_token_path, exist_ok=True)
	os.makedirs(tfidf_lemma_path, exist_ok=True)
	calculate_token_tfidf()
	calculate_lemma_tfidf()

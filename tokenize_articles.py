import os
import re
from lxml import html
import pymorphy3

def process_texts():
    INPUT_DIR = 'articles'
    TOKENS_DIR = 'tokens'
    LEMMAS_DIR = 'lemmas'

    os.makedirs(TOKENS_DIR, exist_ok=True)
    os.makedirs(LEMMAS_DIR, exist_ok=True)

    morph = pymorphy3.MorphAnalyzer()

    # PREP - предлоги, CONJ - союзы, PRCL - частицы, INTJ - междометия, NUMR - числительные
    EXCLUDED_POS = {'PREP', 'CONJ', 'PRCL', 'INTJ', 'NUMR'}

    word_pattern = re.compile(r'\b\w+\b')
    cyrillic_pattern = re.compile(r'^[а-яё]+$')

    for filename in os.listdir(INPUT_DIR):
        if not filename.endswith('.txt'):
            continue
            
        filepath = os.path.join(INPUT_DIR, filename)
            
        # clean html
        raw_content = ""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            tree = html.fromstring(raw_content)
            clean_text = tree.text_content()
        except Exception:
            clean_text = re.sub(r'<[^>]+>', ' ', raw_content)
        
        raw_tokens = word_pattern.findall(clean_text)
        
        unique_tokens = set()
        lemma_to_tokens = {}
        
        for raw_token in raw_tokens:
            token = raw_token.lower()
            
            if not cyrillic_pattern.match(token):
                continue
            
            parsed = morph.parse(token)[0]
            if parsed.tag.POS in EXCLUDED_POS:
                continue
                
            lemma = parsed.normal_form
            
            unique_tokens.add(token)
            
            if lemma not in lemma_to_tokens:
                lemma_to_tokens[lemma] = set()
            lemma_to_tokens[lemma].add(token)
        
        tokens_filepath = os.path.join(TOKENS_DIR, filename)
        with open(tokens_filepath, 'w', encoding='utf-8') as f:
            for t in sorted(unique_tokens):
                f.write(f"{t}\n")
        
        lemmas_filepath = os.path.join(LEMMAS_DIR, filename)
        with open(lemmas_filepath, 'w', encoding='utf-8') as f:
            for lemma, tokens_set in sorted(lemma_to_tokens.items()):
                tokens_str = " ".join(sorted(tokens_set))
                f.write(f"{lemma} {tokens_str}\n")

if __name__ == '__main__':
    process_texts()
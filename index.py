import os

lemmas_path = "lemmas"
tokens_path = "tokens"
articles_path = "articles"
termin_file = "termin_index.txt"

def get_lemmas(lemmas_file):
	"""
	Retrieves lemmas from files and returns dictionary of lemmas and words
	"""
	lemmas = {}
	with open(lemmas_file, 'r', encoding='utf-8') as f:
		for l in f:
			parts = l.strip().split()
			lemma = parts[0]
			words = parts[1:]
			lemmas[lemma] = words
	return lemmas

def build_index():
	"""
	Builds index of lemmas and documents
	"""

	# get list of lemma files
	docs = sorted([f for f in os.listdir(articles_path) if f.endswith('.txt')],
		key=lambda x: int(x.split('.')[0]))
	lemma_files = [os.path.join(lemmas_path, doc) for doc in docs]
	
	lemma_index = {}
	for doc, lf in enumerate(lemma_files, start=1):
		lemmas = get_lemmas(lf)
		for lemma, words in lemmas.items():
			if (lemma_index.get(lemma) == None):
				lemma_index[lemma] = set()
			lemma_index[lemma].add(doc)

	return lemma_index

def build_and_write_index():
	"""
	Builds index of lemmas and documents and writes it into file termin_index.txt
	"""
	index = build_index()
	with open(termin_file, 'w') as f:
		for lemma, docs in index.items():
			str_docs = [str(doc) for doc in docs]
			f.write(f'{lemma} {' '.join(str_docs)}\n')


if __name__ == "__main__":
	build_and_write_index()
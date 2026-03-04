import sys

termin_file = "termin_index.txt"
and_symbol = ' & '
or_symbol = ' | '
not_symbol = ' ~ '
doc_amount = 100

def parse_termin_index():
	"""
	Returns index in dictionary of lemmas and documents that have them
	"""
	index = {}
	with open(termin_file, 'r', encoding='utf-8') as f:
		for l in f:
			parts = l.strip().split()
			lemma = parts[0]
			docs = set([int(doc) for doc in parts[1:]])
			index[lemma] = docs
	return index

def parse_expression_rec(expr, index):
	"""
	Recursively parses parts of expression
	"""
	if (expr.startswith('(') and expr.endswith(')')):
		return parse_expression_rec(expr[1:-1], index)

	#firstly search for first level or operators
	paren_lvl = 0
	op_positions = []
	for i, char in enumerate(expr):
		#increment or decrement parenthesis level
		if char == '(':
			paren_lvl += 1
		elif char == ')':
			paren_lvl -= 1
		#found first level expression
		elif paren_lvl == 0:
			if char == or_symbol.strip():
				op_positions.append(i)
	if len(op_positions) > 0:
		# find last or operator
		pos = op_positions[-1]
		left = expr[:pos].strip()
		right = expr[pos+1:].strip()
		return parse_expression_rec(left, index) | parse_expression_rec(right, index)

	#secondly search for first level and operators
	paren_lvl = 0
	op_positions = []
	for i, char in enumerate(expr):
		#increment or decrement parenthesis level
		if char == '(':
			paren_lvl += 1
		elif char == ')':
			paren_lvl -= 1
		#found first level expression
		elif paren_lvl == 0:
			if char == and_symbol.strip():
				op_positions.append(i)
	if len(op_positions) > 0:
		# find last and operator
		pos = op_positions[-1]
		left = expr[:pos].strip()
		right = expr[pos+1:].strip()
		return parse_expression_rec(left, index) & parse_expression_rec(right, index)

	#lastly search for not operators
	if (expr.startswith(not_symbol.strip())):
		sub_expr = expr[1:].strip()
		all_docs = {i for i in range(1, doc_amount + 1)}
		return all_docs - parse_expression_rec(sub_expr, index)

	#expression is only single word
	return index[expr]


def bool_search(query):
	"""
	Parses query and returns result of boolean search using built index
	"""
	query = query.strip().lower()
	#replace boolean operators with single characters for more convenient parsing
	query = query.replace(' and ', and_symbol).replace(' or ', or_symbol).replace(' not ', not_symbol)
	index = parse_termin_index()
	return parse_expression_rec(query, index)
	
if __name__ == '__main__':
	if len(sys.argv) < 1:
		print('No query was provided')
	else:
		query = sys.argv[1]
		docs = bool_search(query)
		docs_str = [str(doc) for doc in docs]
		if docs_str:
			print(f'Document ids: {' '.join(docs_str)}')
		else:
			print('No documents found')

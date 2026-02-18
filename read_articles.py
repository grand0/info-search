from newspaper import Article
import html
import os

urls_path = "urls.txt"
index_path = "index.txt"

def read_urls():
	"""
	Returns article URLs from urls.txt file
	"""
	with open(urls_path, "r") as file:
		urls = file.read().splitlines()
	return urls

def read_url(url):
	"""
	Reads article content using newspaper3k library from given URL
	"""
	article = Article(url, keep_article_html=True, language="ru")
	article.download()
	article.parse()
	# unescaping cyrillic HTML characters for readability
	return html.unescape(article.article_html)

def write_article(out_path, content):
	"""
	Writes article content into given file path
	"""
	with open(out_path, "w") as file:
		file.write(content)

def read_articles():
	"""
	Reads article URLs from urls.txt file, gets article content from each URL and writes content in separate files
	"""
	index = 1
	urls = read_urls()
	os.makedirs("articles", exist_ok = True)
	with open(index_path, "w") as index_file:
		# iterating over urls, getting its content and writing into corresponding files
		for url in urls:
			html = read_url(url)
			out_path = os.path.join("articles", f"{index}.txt")
			write_article(out_path, html)
			index_file.write(f"{index} {url}\n")
			index += 1


if __name__ == "__main__":
	read_articles()

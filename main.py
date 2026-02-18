from newspaper import Article
import html
import os

urls_path = "urls.txt"
index_path = "index.txt"

def read_urls():
	with open(urls_path, "r") as file:
		urls = file.read().splitlines()
	return urls

def read_url(url):
	article = Article(url, keep_article_html=True, language="ru")
	article.download()
	article.parse()
	return html.unescape(article.article_html)

def write_article(out_path, content):
	with open(out_path, "w") as file:
		file.write(content)

def main():
	index = 1
	urls = read_urls()
	os.makedirs("articles", exist_ok = True)
	with open(index_path, "a") as index_file:
		for url in urls:
			html = read_url(url)
			out_path = os.path.join("articles", f"{index}.txt")
			write_article(out_path, html)
			index_file.write(f"{index} {url}\n")
			index += 1


if __name__ == "__main__":
	main()

import os
import re
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import pymorphy3

from vector_search import load_index, load_doc_vectors, process_query, vector_search

def get_snippet(doc_id):
    filepath = os.path.join("articles", f"{doc_id}.txt")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        clean_text = re.sub(r'<[^>]+>', ' ', raw_content)
        words = re.findall(r'\b\w+\b', clean_text)
        if len(words) > 10:
            return " ".join(words[:10]) + "..."
        return " ".join(words) + ("..." if words else "")
    except Exception:
        return "Описание недоступно..."

DOC_URLS = {}
DOC_VECTORS = {}
DOC_NORMS = {}
IDF_DICT = {}
MORPH = None

class SearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/' or path == '/index.html':
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = re.sub(
                    r'<h3 class="result-title">[\s\S]*?<div class="result-meta">[\s\S]*?</div>',
                    r'<h3 class="result-title">${item.snippet}</h3>\n                        <div class="result-url">${item.doc_id}, <a href="${item.url}" target="_blank">${item.url}</a></div>\n                        <div class="result-meta">Score: ${item.score.toFixed(4)}</div>',
                    content
                )
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "index.html not found")
                
        elif path == '/search':
            query_params = urllib.parse.parse_qs(parsed_path.query)
            query = query_params.get('q', [''])[0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            if not query:
                response = {"error": "Пустой запрос"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            q_vec, q_norm = process_query(query, IDF_DICT, MORPH)
            if q_norm == 0:
                response = {"results": []}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            scores = vector_search(q_vec, q_norm, DOC_VECTORS, DOC_NORMS)
            top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
            
            results = []
            for doc_id, score in top:
                results.append({
                    "doc_id": doc_id,
                    "url": DOC_URLS.get(doc_id, "Unknown URL"),
                    "score": score,
                    "snippet": get_snippet(doc_id)
                })
                
            response = {"results": results}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        else:
            self.send_error(404, "File not found")

def run(port=8000):
    global DOC_URLS, DOC_VECTORS, DOC_NORMS, IDF_DICT, MORPH
    
    print("Инициализация сервера...")
    print("Загрузка индекса и векторов...")
    DOC_URLS = load_index()
    DOC_VECTORS, DOC_NORMS, IDF_DICT = load_doc_vectors()
    MORPH = pymorphy3.MorphAnalyzer()
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, SearchHandler)
    print(f"Сервер запущен! Откройте в браузере: http://localhost:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        
    httpd.server_close()
    print("\nСервер остановлен.")

if __name__ == '__main__':
    run()
from playwright.sync_api import sync_playwright
import time

INITIAL_PAGE = "https://kod.ru/tag/news"
ARTICLES_TARGET_COUNT = 100
ARTICLE_LINK_SELECTOR = 'div[class*="NewsItem_container"] a[class*="NewsItem_imageContainer"]'
MORE_BUTTON_SELECTOR = 'button[class*="News_button"]'


def collect_links():
    """
    Collects links from the INITIAL_PAGE.
    Writes links to the urls.txt file.
    """
    with sync_playwright() as p:
        # open browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(INITIAL_PAGE)
        
        while True:
            # find all links to articles on the page
            links = page.query_selector_all(ARTICLE_LINK_SELECTOR)
            current_count = len(links)
            print(f"Loaded {current_count} URLs")
            
            # if there are enough links on the page, stop
            if current_count >= ARTICLES_TARGET_COUNT:
                break
            
            # otherwise, find and click the button to load more articles
            button = page.query_selector(MORE_BUTTON_SELECTOR)
            if button and button.is_visible():
                button.click()
                time.sleep(1.5)
            else:
                break
        
        # get and write all the links found on the page
        hrefs = [page.evaluate('(el) => el.href', link) for link in links[:ARTICLES_TARGET_COUNT]]
        with open("urls.txt", 'w') as f:
            for url in hrefs:
                f.write(f"{url}\n")
        
        print("Saved to urls.txt")
        browser.close()


if __name__ == "__main__":
    collect_links()
        
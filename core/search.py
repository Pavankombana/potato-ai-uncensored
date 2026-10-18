"""
Zero-dependency DuckDuckGo web search integration.
Performs fast, live web searches via DuckDuckGo HTML endpoints without any API key or subscription.
"""

import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo and return a list of dictionaries with title, url, and snippet.
    """
    if not query or not query.strip():
        return []

    results = []
    clean_query = query.strip()

    # Strategy 1: POST to html.duckduckgo.com/html/
    try:
        url = "https://html.duckduckgo.com/html/"
        response = requests.post(url, data={"q": clean_query}, headers=HEADERS, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all("div", class_="result")
            for el in elements:
                title_elem = el.find("a", class_="result__a")
                snippet_elem = el.find("a", class_="result__snippet")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                raw_href = title_elem.get("href", "")
                
                target_url = raw_href
                if "uddg=" in raw_href:
                    parsed = urllib.parse.urlparse(raw_href)
                    params = urllib.parse.parse_qs(parsed.query)
                    if "uddg" in params:
                        target_url = params["uddg"][0]
                
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                if title and target_url:
                    results.append({
                        "title": title,
                        "url": target_url,
                        "snippet": snippet
                    })
                if len(results) >= max_results:
                    return results
    except Exception:
        pass

    # Strategy 2: GET fallback to lite.duckduckgo.com
    if not results:
        try:
            lite_url = f"https://lite.duckduckgo.com/lite/"
            resp = requests.post(lite_url, data={"q": clean_query}, headers=HEADERS, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                rows = soup.find_all("tr")
                for r in rows:
                    link = r.find("a", class_="result-link")
                    snippet_td = r.find("td", class_="result-snippet")
                    if link:
                        results.append({
                            "title": link.get_text(strip=True),
                            "url": link.get("href", ""),
                            "snippet": snippet_td.get_text(strip=True) if snippet_td else ""
                        })
                    if len(results) >= max_results:
                        return results
        except Exception:
            pass

    return results

if __name__ == "__main__":
    res = search_duckduckgo("Qwen 2.5 Coder 7B", 3)
    print(f"Got {len(res)} results:")
    for r in res:
        print(f"[{r['title']}]\nURL: {r['url']}\nSnippet: {r['snippet']}\n")

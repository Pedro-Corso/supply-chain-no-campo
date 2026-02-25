import feedparser
import json
import os

# Lista de feeds RSS sugeridos
FEEDS = {
    "Economia": [
        "https://www.valor.com.br/brasil/macroeconomia/rss",
        "https://g1.globo.com/dynamo/economia/rss2.xml"
    ],
    "Agro": [
        "https://www.noticiasagricolas.com.br/rss/noticias.xml",
        "https://www.canalrural.com.br/feed/"
    ],
    "Industrial": [
        "https://www.reutersagency.com/feed/?taxonomy=reuters_topics&term=business"
    ],
    "Global": [
        "https://tradingeconomics.com/rss/news.aspx?c=commodities",
        "https://tradingeconomics.com/rss/news.aspx",
        "https://tradingeconomics.com/rss/news.aspx?c=trade"
    ],
    "Clima": [
        "https://metsul.com/feed/",
        "https://www.canalrural.com.br/categoria/agricultura/tempo/feed/",
        "https://www.noticiasagricolas.com.br/rss/clima.xml",
        "https://www.climate.gov/news/feed/rss.xml"
    ]
}

def check_feeds():
    results = {}
    for category, urls in FEEDS.items():
        results[category] = []
        for url in urls:
            print(f"Testando: {url}")
            feed = feedparser.parse(url)
            if feed.entries:
                results[category].append({
                    "url": url,
                    "status": "OK",
                    "entries_count": len(feed.entries),
                    "first_title": feed.entries[0].title
                })
            else:
                results[category].append({
                    "url": url,
                    "status": "EMPTY/ERROR"
                })
    
    # Salva report em .tmp
    with open(".tmp/feed_check_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print("\nRelatório de teste gerado em .tmp/feed_check_report.json")

if __name__ == "__main__":
    check_feeds()

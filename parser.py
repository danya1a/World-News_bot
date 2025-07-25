import requests
from bs4 import BeautifulSoup
import traceback

HEADERS = {"User-Agent": "Mozilla/5.0"}

def default_parser(url, selector, limit=5, base=""):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        items = soup.select(selector)
        if not items:
            return []

        seen = set()
        results = []
        for i in items:
            if not i.get("href"):
                continue
            href = i['href'] if i['href'].startswith('http') else base + i['href']
            title = i.text.strip()
            if (title, href) in seen:
                continue
            seen.add((title, href))
            results.append(f"{title}\n{href}")
            if len(results) >= limit:
                break
        return results
    except Exception as e:
        print(f"[ERROR] Parsing {url} failed: {e}")
        traceback.print_exc()
        return []

# --- Украина ---
parse_unian = lambda: default_parser("https://www.unian.net/", ".news-feed__item__title a", base="https://www.unian.net")
parse_pravda = lambda: default_parser("https://www.pravda.com.ua/", ".article__title a")
parse_korrespondent = lambda: default_parser("https://korrespondent.net/", ".article__title a", base="https://korrespondent.net")
parse_censor = lambda: default_parser("https://censor.net/", ".news_item a", base="https://censor.net")
parse_nv = lambda: default_parser("https://nv.ua/", "article a", base="https://nv.ua")

# --- США ---
parse_nytimes = lambda: default_parser("https://www.nytimes.com/", "section.css-1ez5fsm a", base="https://www.nytimes.com")
parse_wapo = lambda: default_parser("https://www.washingtonpost.com/", "a.card-headline", base="https://www.washingtonpost.com")
parse_cnn = lambda: default_parser("https://edition.cnn.com/world", "h3.cd__headline a", base="https://edition.cnn.com")
parse_foxnews = lambda: default_parser("https://www.foxnews.com/", "main .title a", base="https://www.foxnews.com")
parse_bbc_us = lambda: default_parser("https://www.bbc.com/news/world/us_and_canada", "a.gs-c-promo-heading", base="https://www.bbc.com")

# --- Великобритания ---
parse_bbc = lambda: default_parser("https://www.bbc.com/news", "a.gs-c-promo-heading", base="https://www.bbc.com")
parse_guardian = lambda: default_parser("https://www.theguardian.com/uk", "a.js-headline-text", base="https://www.theguardian.com")
parse_times = lambda: default_parser("https://www.thetimes.co.uk/", "h3 a", base="https://www.thetimes.co.uk")
parse_skynews = lambda: default_parser("https://news.sky.com/uk", ".sdc-site-tile__headline a", base="https://news.sky.com")
parse_dailymail = lambda: default_parser("https://www.dailymail.co.uk/news/index.html", ".linkro-darkred a", base="https://www.dailymail.co.uk")

# --- Германия ---
parse_spiegel = lambda: default_parser("https://www.spiegel.de/", "article a[data-unique-id]", base="https://www.spiegel.de")
parse_sz = lambda: default_parser("https://www.sueddeutsche.de/", "h3.entry-title a", base="https://www.sueddeutsche.de")
parse_faz = lambda: default_parser("https://www.faz.net/", "article a", base="https://www.faz.net")
parse_bild = lambda: default_parser("https://www.bild.de/", "a.tile__link", base="https://www.bild.de")
parse_tagesschau = lambda: default_parser("https://www.tagesschau.de/", "a.ts-teaser__link", base="https://www.tagesschau.de")

# --- Польша ---
parse_onet = lambda: default_parser("https://www.onet.pl/", "article a", base="https://www.onet.pl")
parse_wp = lambda: default_parser("https://www.wp.pl/", "a[data-track-name=title]", base="https://www.wp.pl")
parse_wyborcza = lambda: default_parser("https://wyborcza.pl/", "h2 a", base="https://wyborcza.pl")
parse_tvn24 = lambda: default_parser("https://tvn24.pl/", ".teaser a", base="https://tvn24.pl")
parse_polsat = lambda: default_parser("https://www.polsatnews.pl/", ".news__title a", base="https://www.polsatnews.pl")

# --- Китай ---
parse_xinhua = lambda: default_parser("https://english.news.cn/", ".tit a", base="https://english.news.cn")
parse_chinadaily = lambda: default_parser("https://www.chinadaily.com.cn/", "a[title]", base="https://www.chinadaily.com.cn")
parse_people = lambda: default_parser("https://en.people.cn/", "h3 a", base="https://en.people.cn")
parse_cctv = lambda: default_parser("https://english.cctv.com/", "a[href^='/']", base="https://english.cctv.com")
parse_globaltimes = lambda: default_parser("https://www.globaltimes.cn/", "h3 a", base="https://www.globaltimes.cn")

# --- Источники ---
SOURCES = {
    "Ukraine": [
        {"name": "UNIAN", "url": "https://www.unian.net/", "parser": "parse_unian"},
        {"name": "Ukrainian Pravda", "url": "https://www.pravda.com.ua/", "parser": "parse_pravda"},
        {"name": "Korrespondent", "url": "https://korrespondent.net/", "parser": "parse_korrespondent"},
        {"name": "Censor.NET", "url": "https://censor.net/", "parser": "parse_censor"},
        {"name": "NV", "url": "https://nv.ua/", "parser": "parse_nv"},
    ],
    "USA": [
        {"name": "NY Times", "url": "https://www.nytimes.com/", "parser": "parse_nytimes"},
        {"name": "Washington Post", "url": "https://www.washingtonpost.com/", "parser": "parse_wapo"},
        {"name": "CNN", "url": "https://edition.cnn.com/world", "parser": "parse_cnn"},
        {"name": "Fox News", "url": "https://www.foxnews.com/", "parser": "parse_foxnews"},
        {"name": "BBC US", "url": "https://www.bbc.com/news/world/us_and_canada", "parser": "parse_bbc_us"},
    ],
    "UK": [
        {"name": "BBC News", "url": "https://www.bbc.com/news", "parser": "parse_bbc"},
        {"name": "The Guardian", "url": "https://www.theguardian.com/uk", "parser": "parse_guardian"},
        {"name": "The Times", "url": "https://www.thetimes.co.uk/", "parser": "parse_times"},
        {"name": "Sky News", "url": "https://news.sky.com/uk", "parser": "parse_skynews"},
        {"name": "Daily Mail", "url": "https://www.dailymail.co.uk/news/index.html", "parser": "parse_dailymail"},
    ],
    "Germany": [
        {"name": "Der Spiegel", "url": "https://www.spiegel.de/", "parser": "parse_spiegel"},
        {"name": "Süddeutsche Zeitung", "url": "https://www.sueddeutsche.de/", "parser": "parse_sz"},
        {"name": "FAZ", "url": "https://www.faz.net/", "parser": "parse_faz"},
        {"name": "Bild", "url": "https://www.bild.de/", "parser": "parse_bild"},
        {"name": "Tagesschau", "url": "https://www.tagesschau.de/", "parser": "parse_tagesschau"},
    ],
    "Poland": [
        {"name": "Onet", "url": "https://www.onet.pl/", "parser": "parse_onet"},
        {"name": "WP", "url": "https://www.wp.pl/", "parser": "parse_wp"},
        {"name": "Gazeta Wyborcza", "url": "https://wyborcza.pl/", "parser": "parse_wyborcza"},
        {"name": "TVN24", "url": "https://tvn24.pl/", "parser": "parse_tvn24"},
        {"name": "Polsat News", "url": "https://www.polsatnews.pl/", "parser": "parse_polsat"},
    ],
    "China": [
        {"name": "Xinhua", "url": "https://english.news.cn/", "parser": "parse_xinhua"},
        {"name": "China Daily", "url": "https://www.chinadaily.com.cn/", "parser": "parse_chinadaily"},
        {"name": "People's Daily", "url": "https://en.people.cn/", "parser": "parse_people"},
        {"name": "CCTV", "url": "https://english.cctv.com/", "parser": "parse_cctv"},
        {"name": "Global Times", "url": "https://www.globaltimes.cn/", "parser": "parse_globaltimes"},
    ]
}

# --- Основная функция получения новостей ---
def get_news_by_country(country: str):
    if country not in SOURCES:
        return "Нет новостей для этой страны."

    results = []
    for source in SOURCES[country]:
        try:
            news_items = globals()[source["parser"]]()
            if news_items:
                results.append(f"📰 {source['name']}:\n" + "\n".join(news_items))
        except Exception as e:
            print(f"[ERROR] Failed to get news from {source['name']}: {e}")
            traceback.print_exc()
            continue

    return "\n\n".join(results) if results else "Нет доступных новостей для этой страны."

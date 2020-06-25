import feedparser
import re

RSS_URL = "https://www.cronachemaceratesi.it/feed/"
MAX_ARTICLES_TO_READ = 5


def get_latest_news(current_page, category=None):
    try:
        feed = feedparser.parse(RSS_URL)
        news = feed.entries
        current_page = int(current_page)
        start_item = current_page * MAX_ARTICLES_TO_READ
        end_item = MAX_ARTICLES_TO_READ + current_page * MAX_ARTICLES_TO_READ
        if (news is not None and len(news) >= 0):
            news = [n for n in news if "&#" not in n["summary"]]

            if category is None:
                return get_internal(news, start_item, end_item)
            else:
                filtered_news = []
                for n in news:
                    for tag in n["tags"]:
                        if category.strip().lower() in re.sub(r"[^\w\s]", "", tag["term"].strip().lower()):
                            filtered_news.append(n)
                            break
                return get_internal(filtered_news, start_item, end_item)
        else:
            return []
    except:
        return []


def get_internal(news, start_item, end_item):
    if start_item > len(news):
        return []
    if end_item > len(news):
        end_item = len(news)
    return [get_clean_string_from_news(i) for i in news[start_item:end_item]]


def get_clean_string_from_news(news):
    author = news["author"]
    splitted_summary = news["summary"].replace("–", "-").split(" - ")
    argument = splitted_summary[0] if len(splitted_summary) > 1 else "NEWS"
    real_summary = splitted_summary[0] if len(
        splitted_summary) == 1 else splitted_summary[1]

    utterance = "{0}, di {1}. {2}. {3}. ".format(
        argument, author, news["title"], real_summary
    )

    for char in ["«", "»", "“", "”"]:
        utterance = utterance.replace(char, "\"")
    for char in ["’"]:
        utterance = utterance.replace(char, "'")

    utterance = utterance.replace("(Foto/Video)", "")
    utterance = utterance.replace("A'", "à")
    utterance = utterance.replace("E'", "è")
    utterance = utterance.replace("I'", "ì")
    utterance = utterance.replace("O'", "ò")
    utterance = utterance.replace("U'", "ù")
    utterance = re.sub(r"\s+", " ", utterance)
    utterance = re.sub(r"(\s\d\d)\.(\d\d\s)", r"\1:\2", utterance)

    return utterance.strip()


# for n in get_latest_news(0, "camerino"):
#     print(n)
#     print("===")


# feed = feedparser.parse('https://www.cronachemaceratesi.it/feed/')
# news = feed.entries

# categories = [i["term"] for n in news for i in n["tags"]]
# print(set(categories))

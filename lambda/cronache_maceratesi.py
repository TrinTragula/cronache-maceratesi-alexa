import feedparser
import re

RSS_URL = "https://www.cronachemaceratesi.it/feed/"
MAX_ARTICLES_TO_READ = 5


def get_latest_news(category=None):
    try:
        feed = feedparser.parse(RSS_URL)
        news = feed.entries

        if (news is not None and len(news) >= 0):
            if category is None:
                return [get_clean_string_from_news(i) for i in news[:MAX_ARTICLES_TO_READ]]
            else:
                filtered_news = []
                for n in news:
                    for tag in n["tags"]:
                        if category.strip().lower() in re.sub(r"[^\w\s]", "", tag["term"].strip().lower()):
                            filtered_news.append(n)
                            break
                return [get_clean_string_from_news(i) for i in filtered_news[:MAX_ARTICLES_TO_READ]]
        else:
            return []
    except:
        return []


def get_clean_string_from_news(news):
    author = news["author"]
    splitted_summary = news["summary"].split(" - ")
    argument = splitted_summary[0]
    real_summary = splitted_summary[1]

    utterance = "{0}, di {1}. {2}. {3}. ".format(
        argument, author, news["title"], real_summary
    )

    for char in ["«", "»", "“", "”"]:
        utterance = utterance.replace(char, "\"")
    utterance = utterance.replace("(Foto/Video)", "")
    utterance = re.sub(r"\s+", " ", utterance)
    utterance = re.sub(r"(\s\d\d)\.(\d\d\s)", r"\1:\2", utterance)

    return utterance.strip()


# for n in get_latest_news("civitanova"):
#     print(n)
#     print("===")


# feed = feedparser.parse('https://www.cronachemaceratesi.it/feed/')
# news = feed.entries

# categories = [i["term"] for n in news for i in n["tags"]]
# print(set(categories))

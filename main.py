from news_extractor import TodoNoticias
from constants import MAIN_TOPICS
from model import NLPClassifier

bot = TodoNoticias()

# for topic in MAIN_TOPICS:
#     bot.request_server(type="links",topic = topic)

# for link in bot.all_links:
#     bot.request_server(type='articles', url = link)

# bot.save_csv("todo_noticias_articles")

data = bot.load_files("todo_noticias_full_articles")

algorithm = NLPClassifier(data)

algorithm.preprocessing()

algorithm.modelling()

algorithm.predict("some text...")

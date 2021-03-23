import pandas
from ebpaperboy.utils import clean_text
from tabloid import Tabloid
import json

# instantite tabloid
model = Tabloid()

# download neural network
model.load_network()

df = pandas.read_csv("~/news_zuckerberg.csv")

tags = []

df = df[:4]

for i in range(len(df)):
    print(i)
    story = df.iloc[i]
    
    texts = [story['article_title'] + ".",
             story['article_lead'],
             story['article_body']]

    article = " ".join(texts)

    tag = model.predict_text(article, threshold = 0.1)
    tag = {'content_id': int(story['content_id']), 'tag': tag}

    tags.append(tag)

with open('test.json', 'w') as fp:
    json.dump(tags , fp)
    
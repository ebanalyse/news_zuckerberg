import pandas as pd
from ebpaperboy.utils import clean_text
from tabloid import Tabloid
import json

# Prædiktér tags

# instantite tabloid
model = Tabloid()

# download neural network
model.download_network()
model.load_network()

df = pd.read_csv("~/news_zuckerberg.csv")

tags = []

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

with open('topics.json', 'w') as fp:
    json.dump(tags , fp, ensure_ascii = False)

clean_texts = []
# clean texts
for i in range(len(df)):
    print(i)
    story = df.iloc[i]
    
    texts = [story['article_title'] + ".",
             story['article_lead'],
             story['article_body']]

    article = " ".join(texts)
    article = clean_text(article)

    text = {'content_id': int(story['content_id']), 'clean_text': article}

    clean_texts.append(text)

with open('clean_texts.json', 'w') as fp:
    json.dump(clean_texts , fp, ensure_ascii = False)
    
# antal artikler opdelt på brand og år
from ebawsconnect.athena import get_query_results_from_athena
query = """
SELECT SUBSTRING(first_published, 1, 4) AS yr, cms_publication,
COUNT(DISTINCT content_id) AS ANTAL
FROM dfp_prod_jppol_dsa_shrd.escenic_article
WHERE article_url NOT LIKE '/incoming%'
AND cms_publication IN ('ekstrabladet', 'jyllandsposten', 'politiken')
AND LENGTH(article_body) >= 100
GROUP BY SUBSTRING(first_published, 1, 4), cms_publication
ORDER BY cms_publication, yr
"""
out = get_query_results_from_athena(query, to_df = True, force_query = True, profile_name = "jppol-dfp")
out.to_csv("stories_count_brand_year.csv", index = False)
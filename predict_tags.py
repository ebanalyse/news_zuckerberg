import pandas
from ebpaperboy.utils import clean_text
from tabloid import Tabloid

# instantite tabloid
model = Tabloid()

# download neural network
model.load_network()

df = pandas.read_csv("~/news_zuckerberg.csv")

tags = []

for i in range(5):
    print(i)
    story = df.iloc[i]
    texts = [story['article_title'] + ".",
             story['article_lead'],
             story['article_body']]

    texts = [clean_text(text) for text in texts]

    article = " ".join(texts)

    tag = model.predict_text(article, threshold = 0.1)

    tags.append(tag)

    
# predict from docvec
docvec = np.random.randn(300) # create a random test docvec
prediction = model.predict(docvec=docvec)

# predict from text, with text output
text = 'Folk siger, at Jeppe drikker. Men de siger ikke, hvorfor Jeppe drikker.'
pred = model.predict_text(text, threshold=0.1)

import numpy as np
from tabloid import Tabloid
from 

# instantite tabloid
model = Tabloid()

# download neural network
model.download_network()

# predict from docvec
docvec = np.random.randn(300) # create a random test docvec
prediction = model.predict(docvec=docvec)

# predict from text, with text output
text = 'Folk siger, at Jeppe drikker. Men de siger ikke, hvorfor Jeppe drikker.'
predcition = model.predict(text, threshold=0.1)
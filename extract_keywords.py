import datetime
import logging
import re

import numpy as np
from tqdm import tqdm
import pandas as pd
import awswrangler as wr
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from nltk.tokenize import sent_tokenize
import torch

from ebawsconnect.athena import get_query_results_from_athena

logger = logging.getLogger("Data extraction..")

def lookup_articles(word="Mark Zuckerberg"):
    
    logger.info(f"Looking up articles containing: {word}")
    
    publications = ["'ekstrabladet'", 
                    "'politiken'",
                    "'jyllandsposten'"]
    
    # TODO: remove LIMIT
    # form query
    query = f"""
    SELECT *
    FROM dfp_prod_jppol_dsa_shrd.escenic_article
    WHERE article_url NOT LIKE '/incoming%'
    AND cms_publication IN ({' ,'.join(publications)})
    AND LENGTH(article_body) >= 100
    AND (article_title LIKE '%{word}%'
    OR article_lead LIKE '%{word}%'
    OR article_body LIKE '%{word}%')
    LIMIT 100
    """
    
    # submit query
    out = get_query_results_from_athena(query, 
                                        to_df = True,
                                        force_query = True, 
                                        profile_name = "jppol-dfp")
    
    # compute year from 'first published'
    out["year"] = [x[:4] for x in out.first_published.values.tolist()]
    
    return out

def clean_articles(df):
    
    # drop missings
    na_cols = ['article_lead', 'article_title', 'article_body']
    df = df.dropna(subset=na_cols)  
    
    # remove duplicates
    # select last modified entry per content_id
    df = df.sort_values('last_modified').groupby('content_id').tail(1) 
    
    return df

def clean_text(text: str) -> str:
    """Clean-up text
    Removes nasty stuff from texts in order to prepare them
    for modelling.
    Args:
        text (str): Text to clean.
    Returns:
        str: cleaned text.
    """

    # clean up text
    replace_with_space = [
        # HTML Links
        "<a href.*?<\/a>",
        # various HTML
        # <h5> <i> etc.
        r'\<[^)]*\>',
        # /ritzau/ etc.
        r'/[^)]*/',
        # &mdash; etc.
        "&[^)]*;",
        # links
        # HACK: FIX. Og erstat med punktummer?
        '\\n',
        '\\t',
        '\\xa0',
        # TODO: overvej denne.
        "--------- SPLIT ELEMENT ---------"
        ]

    replace_with_space = "|".join(replace_with_space)
    
    text = re.sub(replace_with_space, " ", text)

    # replace the over spaces.
    text = re.sub('\s{2,}', " ", text)

    return text

def format_articles(df):

    clean_texts = []
    for article in df.itertuples(index=False, name="row"):
        texts = [article.article_title + ".",
                 article.article_lead,
                 article.article_body]
        text = " ".join(texts)
        text = clean_text(text)
        clean_texts.append(text)
            
    df["clean_text"] = clean_texts
    
    # subset only relevant columns
    df = df[["content_id",
           "brand",
           "article_title",
           "article_lead",
           "article_body",
           "clean_text",
           "first_published",
           "article_url"]]
    
    return(df)


def extract_data(keyword,
                 to_s3=True,
                 dir_dest="s3://externalresearch/persons"):
    
    df = lookup_articles(keyword)
    df = clean_articles(df)
    df = format_articles(df)
    
    if to_s3:
        if len(df) > 0:
            wr.s3.to_csv(
                df,
                path=f"{dir_dest}/{keyword}.csv",
                index=True
                )
    
    return df 

keywords = ["Mark Zuckerberg"
, "Sheryl Sandberg" 
, "Jeff Bezos" 
, "Sergei Brin"
, "Larry Page"
, "Sundar Pichai" 
, "Tim Cook" 
, "Bill Gates" 
, "Jack Ma" 
, "Elon Musk" 
, "Ted Sandros" 
, "Jack Dorsey"
, "Margrethe Vestager"
, "Edward Snowden"
, "Christopher Wylie"
, "Peter Thiel" 
, "Steve Jobs" 
, "Tim Cook"
, "Rick Hastings"
, "Travis Kalanick"]

[extract_data(kw) for kw in tqdm(keywords)]




def predict_text(pipeline, text):
    
    labels = {'positiv': 1,
              'negativ': -1,
              'neutral': 0}
    
    sents = sent_tokenize(text)
    preds = pipeline(sents)
    preds_scores = [labels.get(x.get('label')) for x in preds]
    score = np.mean(preds_scores)
    
    return score

tokenizer = AutoTokenizer.from_pretrained("pin/senda")
model = AutoModelForSequenceClassification.from_pretrained("pin/senda")
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# create 'senda' sentiment analysis pipeline 
senda_pipeline = pipeline('sentiment-analysis', model=quantized_model, tokenizer=tokenizer)

sents = [predict_text(senda_pipeline, text) for text in tqdm(df.clean_text.values.tolist())]


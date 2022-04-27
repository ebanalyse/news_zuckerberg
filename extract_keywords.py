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
import boto3

import keywords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lookup_articles(word:str="Mark Zuckerberg",
                    aws_profile:str="jppol-dfp",
                    add_keyword:bool=True) -> pd.DataFrame:
    """Look up articles 
    
    Look up articles containing specific keyword.
    
    Args:
        word (str): Keyword to look for.
        aws_profile(str): Optional. Which aws profile
            to use to connect to jppol dfp. Profile
            must be set.
            Defaults to 'jppol-dfp'.
        add_keyword(bool): Add keyword to data frame
            as a column.
        
    Returns:
        pd.DataFrame: pandas Data Frame with resulting
            articles.
    """
    
    logger.info(f"Looking up articles containing: {word}")
    
    publications = ["'ekstrabladet'", 
                    "'politiken'",
                    "'jyllandsposten'"]
    
    # TODO: remove LIMIT
    # form query
    query = f"""
    SELECT *
    FROM escenic_article
    WHERE article_url NOT LIKE '/incoming%'
    AND cms_publication IN ({' ,'.join(publications)})
    AND LENGTH(article_body) >= 100
    AND (article_title LIKE '%{word}%'
    OR article_lead LIKE '%{word}%'
    OR article_body LIKE '%{word}%')
    LIMIT 100
    """
    
     # NOTE: aws profile 'jppol-dfp' must be set
    session = boto3.Session(profile_name=aws_profile, 
                            region_name="eu-west-1")

    # submit query
    df = wr.athena.read_sql_query(
            sql=query,
            database="dfp_prod_jppol_dsa_shrd", 
            use_threads=True,
            boto3_session=session,
            )
    
    # add keyword if opted for
    if add_keyword:
        df["keyword"]=word
    
    # compute(/overwrite) year from 'first published'
    df["year"] = [x[:4] for x in df.first_published.values]
    
    return df

def clean_articles(df:pd.DataFrame,
                   na_cols:list=['article_lead', 'article_title', 'article_body']):
    """
    Clean articles
    
    Remove irrelevant articles based on relevant criterias.
    
    Args:
        df (pd.DataFrame): data frame with articles.
        na_cols (list): list with names of columns, for which
            articles are removed, if they are missing.
            
    Returns:
        pd.DataFrame: articles after cleaning.
    """
    
    # reject missings (not articles)
    df = df.dropna(subset=na_cols)  
    
    # remove duplicates
    # only keep last modified entry per content_id
    df = df.sort_values('last_modified').groupby('content_id').tail(1) 
    
    return df

# HELPER FUNCTION FOR TEXT CLEANING
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

def extract_data_for_keyword(kw:str,
                             **kwargs) -> pd.DataFrame:
    """Extract Data for Keyword
    
    Extract, clean and format data for keyword.
    
    Args:
        kw (str): keyword to extract data for.
        kwargs: all optional arguments for 
            lookup_articles().

    Returns:
        pd.DataFrame: resulting "clean" articles.
    """
    
    df = lookup_articles(kw, **kwargs)
    df = clean_articles(df)
    df = format_articles(df)

    return df

def extract_data_for_keywords(keywords:list,
                              to_s3:bool=True,
                              s3_path:str="s3://externalresearch/lookupkeywords/persons.csv",
                              **kwargs):
    
    logger.info("Extracting data for keywords...")
    
    # extract data for all keywords    
    dfs = [extract_data_for_keyword(kw, add_keyword=True, **kwargs) for kw in tqdm(keywords)]
    
    # row bind all articles into one single data frame
    dfs = pd.concat(dfs)
    dfs = dfs.reset_index()
    
    if to_s3:
        logger.info(f"Writing data to S3: {s3_path}")
        if len(dfs) > 0:
            wr.s3.to_csv(
                dfs,
                path=s3_path,
                index=True
                )
    
    return dfs 

if __name__ == "__main__":
    s3_path = "s3://externalresearch/lookupkeywords/"
    persons_path = s3_path + "persons.csv"  
    extract_data_for_keywords(keywords.PERSONS_DEMO, s3_path=persons_path)

# def predict_text(pipeline, text):
#     
#     labels = {'positiv': 1,
#               'negativ': -1,
#               'neutral': 0}
#     
#     sents = sent_tokenize(text)
#     preds = pipeline(sents)
#     preds_scores = [labels.get(x.get('label')) for x in preds]
#     score = np.mean(preds_scores)
#     
#     return score
# 
# tokenizer = AutoTokenizer.from_pretrained("pin/senda")
# model = AutoModelForSequenceClassification.from_pretrained("pin/senda")
# quantized_model = torch.quantization.quantize_dynamic(
#     model, {torch.nn.Linear}, dtype=torch.qint8
# )
# 
# # create 'senda' sentiment analysis pipeline 
# senda_pipeline = pipeline('sentiment-analysis', model=quantized_model, tokenizer=tokenizer)
# 
# sents = [predict_text(senda_pipeline, text) for text in tqdm(df.clean_text.values.tolist())]


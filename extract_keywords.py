# MAKE SURE TO SOURCE ENV VARS FROM .ENVRC

import time

import tqdm
import pandas as pd
import awswrangler as wr

from ebawsconnect.athena import get_query_results_from_athena

def scrape(word="Mark Zuckerberg"):
    query = f"""
    SELECT *
    FROM dfp_prod_jppol_dsa_shrd.escenic_article
    WHERE article_url NOT LIKE '/incoming%'
    AND LENGTH(article_body) >= 100
    AND (article_title LIKE '%{word}%'
    OR article_lead LIKE '%{word}%'
    OR article_body LIKE '%{word}%')
    """
    out = get_query_results_from_athena(query, 
                                        results_file = f"{word}.csv", 
                                        to_df = True,
                                        force_query = True, 
                                        profile_name = "jppol-dfp")
    print("Word")
    out["keyword"] = word
    return out

#t1 = time.time()
#out = scrape("Mark Zuckerberg")
#t2 = time.time()

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

output = [scrape(keyword) for keyword in tqdm.tqdm(keywords)]
output = pd.concat(output, ignore_index=True)

wr.s3.to_csv(
   output,
   path="s3://externalresearch/persons.csv",
   index=True
   )

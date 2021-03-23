# from ebawsconnect.athena import get_query_results_from_athena
# query = """
# SELECT *
# FROM dfp_prod_jppol_dsa_shrd.escenic_article
# WHERE article_url NOT LIKE '/incoming%'
# AND LENGTH(article_body) >= 100
# AND (article_title LIKE '%Mark Zuckerberg%'
# OR article_lead LIKE '%Mark Zuckerberg%'
# OR article_body LIKE '%Mark Zuckerberg%')
# """
# out = get_query_results_from_athena(query, results_file = "zuckerberg.csv", to_df = True, force_query = True, profile_name = "jppol-dfp")

library(tidyverse)

df = readr::read_csv("projects/zuckerberg.csv")

# subset relevant publications
df <- df %>% filter(cms_publication %in% c('ekstrabladet','politiken','jyllandsposten'))

# exploratory
df %>%
  mutate(year_lk = substr(first_published, 1, 4)) %>%
  group_by(year_lk) %>%
  summarize(antal = n())

# handle unique content-ids
singles = df %>% 
  group_by(content_id) %>%
  mutate(antal = n()) %>%
  filter(antal == 1) %>%
  select(-antal)

# handle non-unique content-ids
dubs = df %>% 
  group_by(content_id) %>%
  mutate(antal = n()) %>%
  filter(antal > 1) %>%
  select(-antal) %>%
  arrange(last_modified) %>%
  slice(1) %>%
  ungroup()
  
out = bind_rows(singles, dubs)

write_csv(out, "artikeldata_zuckerberg.csv")







  
  
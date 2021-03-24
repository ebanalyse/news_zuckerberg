# Dataudtræk - Artikler om Mark Zuckerberg

Vedhæftet findes resultaterne af et dataudtræk fra JP/POLITIKENS HUS data lake af artikler, hvor 
"Mark Zuckerberg" indgår.

Udtrækket har følgende komponenter:

1. news_zuckerberg.csv: selve udtrækket af rådata for "Mark Zuckerberg"-artikler, i alt >1.500 artikler
2. clean_texts.json: artikler fra 1., hvor selve teksten er forsøgt rengjort
3. stories_count_brand_year.csv: et groft skøn over antallet af udgivne artikler opdelt på brand (jp/pol/eb) og år
4. topics.json: prædikterede topics for artikler i 1 med EB's nuværende topic-model "Tabloid".

Herunder en række mere detaljerede oplysninger om de enkelte komponenter

## news_zuckerberg.csv

Dette er selve dataudtrækket, sådan som det ser ud i Ekstra Bladets kildesystemer, dvs. rådata. Datasættet
er forsøgt renset, sådan at tabellen kun indeholder unikke artikler (dette er dog ikke lykkedes 100 procent).
Hver række svarer til en artikel.

Tabellen indeholder følgende felter med navne, der langt hen ad vejen fremstår selvforklarende:
brand,sub_brand,cms_publication,section_id,content_id,article_url,article_title,article_lead,section_name,first_published,first_published_date,tag_scheme_term_array,tag_scheme_array,last_modified,article_body,cms_database,year,month

Her et par eksempel:
'cms_publication' angiver publikationens navn. 
'content_id' er en unik identifikator for en artikel og svarer til en primærnøgle.
'article_title', 'article_lead' og 'article_body' udgør tilsammen en artikels indhold.
'article_url' indeholder url til artiklen.
'section_name' indeholder navnet på den sektion, artiklen er rubriceret under.

osv.

## clean_texts.json:

Her er artiklerne fra news_zuckerberg.csv forsøgt rengjort ved at fjerne diverse huskumsnusk, specialtegn,
HTML-kode m.v. fra det rå artikelindhold.

Artikelteksterne kan kobles til data i news_zuckerberg.csv vha. 'content_id'.

## stories_count_brand_year.csv

Af denne tabel fremgår et udtræk af antallet unikke artikler (content-id's) opdelt på brand og år.

Dette tal er en proxy - groft estimat - for antallet af udgivne artikler opdelt på de forskellige medier.

## topics.json

Her er tabelleret de prædikterede topics for artiklerne i news_zuckerberg.csv med Ekstra Bladets Data
Science teams seneste Topic-model, der går under navnet "Tabloid".

De prædikterede topics kan kobles til artiklerne i news_zuckerberg.csv gennem 'content_id'.

For en uddybende forklaring til disse prædiktioner henvises til Ekstra Bladets Data Science afdeling.





























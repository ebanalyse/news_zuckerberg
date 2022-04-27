# Extract, Transform and Load Data for Keywords

(Primitiv) funktionalitet til at lave et dataudtræk fra JP/POLITIKENS HUS data lake af artikler, hvor 
bestemte keywords indgår.

Dataudtrækket renses, formateres og eksporteres herefter til S3, hvorfra de potentielt
kan deles internt og med eksterne forskere. 

Seneste udtræk kan genereres ved at afvikle 'main-scriptet':

```bash
python -m etl_keywords
```

**NB**: Sørg for først at installere afhængigheder:

```bash
pip install -r requirements.txt
```

## Indhold af udtræk 

Udtrækket har følgende komponenter:

1. "articles*.csv": En eller flere .csv-filer med artikel-data for de artikler, der er blevet trukket ud.
2. "predictions*.csv": En eller flere .csv-filer med prædiktioner for de pågældende artikler fra relevante modeller (f.eks. Sentiment, Topic, NER).

Herunder følger en række mere detaljerede oplysninger om de enkelte komponenter.

## articles*.csv

Dette er artikel-dataudtrækket fra JP POLs kildesystemer. Datasættet
er forsøgt renset, sådan at tabellen kun indeholder unikke artikler (dette er dog ikke lykkedes 100 procent).
Hver række svarer til en artikel.

Tabellen indeholder følgende felter med navne:

- content_id: en unik identifikator for en artikel og svarer til en **primærnøgle**.
- article_title: artikel titel
- article_lead: artikel rubrik
- article_body: artikel brødtekst
- clean_text: den samlede tekst i artiklen, der er forsøgt renset for diverse snavs (hyperlinks, specialtegn etc.).
- first_published: tidspunkt for første publicering af artiklen.
- article_url: url til originalartiklen.

## predictions*.csv:

Indeholder prædiktioner fra relevante modeller på de samme artikler i articles*.csv.

Tabellerne skal content_id som primærnøgl, hvorved de herigennem kan kobles tilbage til artiklerne i articles*.csv.

Bortset fra det skal predictions*.csv for hver række indeholde relevant metadata for prædiktionerne et meningsfuldt format, der vil være forskelligt fra model til model. Det er op til de modelansvarlige for de enkelte modeller at definere og beskrive formatet.

I et simpelt eksempel som Sentiment Analysis vil formatet være:

| content_id | prediction |
| --- | ------- | 
| 123 | positiv |
| 456 | neutral |
| 789 | negativ |




























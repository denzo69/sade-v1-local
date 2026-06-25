# Säde AI Evaluation Policy v1

Säde v1 käyttää kahta testitasoa:

1. tavalliset yksikkö- ja integraatiotestit
2. AI-käytösevalit, jotka tarkistavat turvallisuuden, totuusrajan ja työkalupolitiikan

Ensimmäinen toteutus on staattinen: evalit eivät vaadi live-mallia tai Ollamaa. Tämä varmistaa, että projektin suojakerrokset ovat olemassa ja testattavissa jokaisella `pytest`-ajolla.

Nykyiset eval-kohteet:

- prompt injection -yritysten tunnistus
- salaisuuksiin ja `auth.json`-tiedostoon kohdistuvien pyyntöjen riskimerkintä
- työkalujen riskitasojen tarkistus
- RAG-haun epävarmuusraja silloin, kun lähteitä ei löydy

Pääreitit:

- `GET /evals/static`
- `POST /security/prompt-injection/analyze`
- `POST /rag/quality`

Totuusraja: staattinen eval ei todista mallin vastausten laatua kaikissa tilanteissa. Se todistaa, että turva- ja arviointikerros on teknisesti olemassa. Live-mallin laatuevalit voidaan lisätä myöhemmin erillisenä kerroksena.


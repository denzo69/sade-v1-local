# Säde Finnish Language Pack v1

Päivitetty: 2026-06-21  
Tila: active

## Tarkoitus

Finnish Language Pack ohjaa Säteen vastaukset luontevalle, ymmärrettävälle ja teknisesti täsmälliselle suomelle. Se ei ole yleiskäyttöinen konekäännösmoottori eikä jälkikäsittele mallin vastausta.

## Toimintaperiaate

- Oletuskieli on suomi.
- Käyttäjän selkeä pyyntö vastata englanniksi ohittaa oletuksen kyseisessä vastauksessa.
- Koodia, komentoja, tiedostopolkuja, API-nimiä ja tunnisteita ei käännetä.
- Vakiintuneita tuote- ja kirjastonimiä ei muuteta.
- Epäselvän suomenkielisen teknisen termin yhteydessä alkuperäinen termi annetaan ensimmäisellä käyttökerralla sulkeissa.
- Kielipaketti ei saa keksiä suomennoksia.

## Projektisanasto

| Englanninkielinen termi | Suositeltu muoto |
|---|---|
| audit log | audit-loki |
| guardrail / guardrails | turvaraja / turvarajat |
| language pack | kielipaketti |
| learning feedback | oppimispalaute |
| memory cleaner | muistihuolto (`memory_cleaner`) |
| semantic memory | semanttinen muisti |
| system prompt | ydinprompti (system prompt) |
| tool router | työkalureititin (`tool_router`) |

Sanasto on ohjaava, ei mekaaninen korvaustaulukko. Asiayhteys ratkaisee taivutuksen ja sanavalinnan.

## Suojatut tekniset muodot

Esimerkiksi `API`, `FastAPI`, `JSON`, `JSONL`, `RAG`, `SHA-256`, `UI`, `URL`, `Ollama`, `Python`, `pytest`, `tool_router` ja `memory_cleaner` säilytetään tunnistettavina.

## Integraatio

- Toteutus: `app/language_pack.py`
- Promptti-integraatio: `app/main.py` / `build_sade_prompt`
- Tila: `GET /language/status`
- Testit: `tests/test_language_pack.py`

## Totuusraja

Kielipaketti parantaa ohjausta ja terminologiaa, mutta paikallinen kielimalli tuottaa lopullisen tekstin. Kielipaketti ei takaa täydellistä kielioppia eikä korvaa käyttäjän palautetta.


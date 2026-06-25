# Säde Model Provider Policy v1

Säde v1 käyttää mallikutsuihin erillistä provider-kerrosta.

Nykyinen provider:

- `ollama`

Tavoite:

- muu sovellus ei ole suoraan sidottu yksittäiseen mallibackendiin
- myöhemmin voidaan lisätä toinen paikallinen malli tai API-pohjainen provider ilman koko sovelluksen uudelleenkirjoitusta

Pääreitti:

- `GET /model/status`

Toteutus:

- `app/model_provider.py`

Totuusraja: v1 ei vielä sisällä useita provider-toteutuksia. Se sisältää vaihtokerroksen ja Ollama-providerin.


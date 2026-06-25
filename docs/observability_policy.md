# Säde Observability Policy v1

Säde v1:n kehittäjän jäljitettävyys tallentaa kevyen trace-lokin siitä, miten chat-pyyntö käsiteltiin.

Trace ei saa sisältää salasanoja, sessiotokeneita, API-avaimia tai muita salaisuuksia. Tiedot redaktoidaan ennen tallennusta.

Trace-lokiin kirjataan esimerkiksi:

- pyynnön aikaleima
- viestin lyhyt esikatselu
- viestin hash
- valittu reitti
- työkalun nimi
- prompt injection -analyysin tulos
- mallireitin vastausmerkkien määrä

Pääreitti:

- `GET /debug/trace`

Toteutus:

- `app/debug_trace.py`

Totuusraja: trace-loki ei ole sama kuin audit-log. Audit-log todistaa turvallisuus- ja kirjoitustoimintoja. Trace auttaa ymmärtämään päätöspolkua kehityksen aikana.


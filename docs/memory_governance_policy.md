# Säde Memory Governance Policy v1

Säde v1 antaa käyttäjälle hallinnan pitkäaikaiseen muistiin.

Nykyiset toiminnot:

- näytä muistimerkinnät
- vie muisti JSON-muotoon
- poista yksittäinen muistimerkintä vahvistuksella

Pääreitit:

- `GET /memory/entries`
- `POST /memory/export`
- `POST /memory/delete-entry`

Poisto vaatii täsmällisen vahvistuslauseen:

```text
HYVÄKSYN MUISTIMERKINNÄN POISTON
```

Ennen poistoa alkuperäisestä `sade_memory.md`-tiedostosta tehdään varmuuskopio.

Toteutus:

- `app/memory_governance.py`

Totuusraja: tämä koskee markdown-pohjaista Säde-muistia. Semanttisen vektorimuistin huolto tehdään erillisellä `memory_cleaner.py`-moduulilla.


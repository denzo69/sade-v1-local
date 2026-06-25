# Säde Tool Risk Policy v1

Säde v1 luokittelee työkalut riskitason mukaan, jotta luku-, haku-, kirjoitus- ja järjestelmätoiminnot eivät sekoitu toisiinsa.

Riskitasot:

- `read`: turvalliset lukutoiminnot
- `search`: haku- ja RAG-toiminnot
- `memory_write`: muistiin kirjoittavat toiminnot
- `file_write`: tiedostoa muuttavat toiminnot
- `high`: korkean vaikutuksen ylläpitotoiminnot
- `critical`: ydinpromptiin, palautukseen tai poistoon liittyvät erityisen riskialttiit toiminnot

Audit-log tukee tasoja `low`, `medium` ja `high`. Siksi tarkempi työkaluriski tallennetaan metadataan ja muunnetaan audit-logiin yhteensopivaksi riskiksi.

Pääreitti:

- `GET /tools/policies`

Toteutus:

- `app/tool_permissions.py`

Periaate: jos toiminto kirjoittaa muistiin, muuttaa tiedostoa, poistaa tietoa tai palauttaa varmuuskopiosta, sen pitää olla auditoitava ja tarpeen mukaan vahvistettava.


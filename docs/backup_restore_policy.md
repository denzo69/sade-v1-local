# Säde Backup and Restore Policy v1

Säde v1 suojaa muistia ja projektin dokumentaatiota zip-varmuuskopioilla.

Varmuuskopio sisältää:

- `memory/`-kansion teksti-, JSON- ja JSONL-tiedostoja
- `docs/`-kansion dokumentteja
- projektin konfiguraatiotiedostoja

Varmuuskopio ei sisällä:

- `auth.json`
- `auth_sessions.json`
- vektorikannan binäärihakemistoja

Pääreitit:

- `GET /backup/list`
- `POST /backup/archive`
- `POST /backup/restore`

Palautus vaatii täsmällisen vahvistuslauseen:

```text
HYVÄKSYN VARMUUSKOPION PALAUTUKSEN
```

Toteutus:

- `app/backup_restore.py`

Periaate: palautus on korkean riskin toiminto ja se kirjataan audit-logiin.


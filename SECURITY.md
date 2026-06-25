# Security Policy — Säde v1

Säde v1 on paikallinen AI-työtila. Se käsittelee muistia, tiedostoja, audit-lokia ja kirjautumissessioita, joten sitä ei pidä altistaa avoimeen internetiin.

## Älä julkaise näitä

- `app/memory/auth.json`
- `app/memory/auth_sessions.json`
- `app/memory/chat_log.md`
- `app/memory/*.jsonl`
- `app/memory/vector_db/`
- `app/memory/backups/`
- `app/memory/exports/`
- henkilökohtaiset uploadit
- `.env`

## Suositeltu käyttö

- paikallinen osoite `127.0.0.1`
- kirjautumissuojaus käytössä
- vahva salasana
- ei porttiohjausta julkiseen internetiin
- VPN/Tailscale vain jos etäkäyttö tarvitaan

## Riskitoiminnot

Korkean riskin toimintoja ovat:

- tiedostojen kirjoitus
- muistiin kirjoittaminen
- muistimerkinnän poisto
- semanttisen indeksin uudelleenrakennus
- system promptin muokkaus
- varmuuskopion palautus

Näiden tulee olla auditoituja ja tarvittaessa käyttäjän erikseen vahvistamia.


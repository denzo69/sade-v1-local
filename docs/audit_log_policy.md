# Säde Audit Log Policy v1

Päivitetty: 2026-06-21  
Tila: active

## Tarkoitus

Audit-loki tekee turvallisuuden kannalta merkittävistä toiminnoista jäljitettäviä. Se ei ole keskustelumuisti, analytiikkaloki eikä lupa toiminnon suorittamiseen.

## Periaatteet

- Loki on append-only: sovellus lisää rivejä mutta ei muokkaa tai tyhjennä niitä.
- Jokainen rivi sisältää edellisen rivin hashin. Ketjun katkeaminen tai rivin muuttuminen näkyy eheystarkistuksessa.
- Auditointi ei korvaa käyttäjän hyväksyntää, guardraileja tai tiedostopolkujen tarkistuksia.
- Audit-loki ei tallenna viestien, tiedostojen tai system promptin raakasisältöä.
- Salaisuuksiin viittaavat avaimet sekä sisältökentät sensuroidaan automaattisesti.
- Eheydeltään rikkoutuneeseen lokiin ei lisätä uusia tapahtumia ennen tilanteen tutkimista.

## Kirjattavat tapahtumat

Vähintään seuraavat kirjataan yrityksenä ja lopputuloksena:

- asetusten tai system promptin muuttaminen,
- tiedoston kirjoittaminen, append ja upload,
- semanttisen indeksin uudelleenrakennus,
- tehtävän suorittaminen tai peruminen,
- työkalureitittimen käsittelemä toiminto,
- vienti ja varmuuskopiointi,
- estetty tai epäonnistunut turvallisuuskriittinen toiminto.

Pelkkää lukemista ja tavallista keskustelua ei tarvitse kirjata, ellei siihen liity työkalutoimintoa tai turvallisuuspoikkeamaa.

## Tietomalli

Jokainen JSONL-rivi sisältää vähintään `sequence`, `time`, `actor`, `category`, `action`, `outcome`, `risk_level`, `reason`, `target`, turvalliseksi rajatut `details`, `previous_hash` ja `event_hash`.

## Rajapinnat

- `GET /audit/status` tarkistaa ketjun eheyden.
- `POST /audit/log` lukee rajatun määrän viimeisimpiä tapahtumia.
- Tyhjennysrajapintaa ei tarjota.

## Säilytys ja huolto

Lokitiedosto sijaitsee polussa `app/memory/audit_log.jsonl`. Arkistointi tehdään myöhemmin erillisellä, käyttäjän hyväksymällä menettelyllä. Arkistointia ei saa toteuttaa hiljaisena poistona.

## Totuusraja

Hash-ketju havaitsee tavalliset jälkikäteiset muutokset, mutta se ei ole ulkoisesti allekirjoitettu tai hyökkääjältä suojattu todistus. Paikallisen järjestelmän täydet kirjoitusoikeudet saanut toimija voi periaatteessa rakentaa ketjun uudelleen.

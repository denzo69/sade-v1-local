# Säde v1 Project Inventory

Päivitetty: 2026-06-18
Tarkoitus: Säde v1:n sisäinen projektikartta

## Audit Log v1 — 2026-06-21

- Moduuli: `app/audit_log.py`
- Politiikka: `docs/audit_log_policy.md`
- Data: `app/memory/audit_log.jsonl`
- Rajapinnat: `GET /audit/status`, `POST /audit/log`
- Tila: implemented and covered by automated tests
- Turvaraja: append-only, hash-ketjutettu, sisältökentät sensuroidaan, ei tyhjennysrajapintaa

## Finnish Language Pack v1 — 2026-06-21

- Moduuli: `app/language_pack.py`
- Politiikka ja sanasto: `docs/finnish_language_pack.md`
- Integraatio: `app/main.py` / `build_sade_prompt`
- Rajapinta: `GET /language/status`
- Tila: implemented and covered by automated tests
- Oletuskieli: suomi; käyttäjän selkeä englannin pyyntö huomioidaan

## Web Search Tool v1.2 — 2026-06-21

- Moduuli: `app/web_search.py`
- Reititys: `app/tool_router.py`
- Politiikka: `docs/web_search_policy.md`
- Providerit: Brave Search API tai DuckDuckGo Lite
- Tila: implemented, direct-chat integrated and covered by automated tests
- Ohjattu haku: hakukokeilupyynnön jälkeinen viesti käsitellään yhtenä hakukyselynä
- Integraatioraja: ei automaattista RAG-, Goal Engine- tai semanttisen muistin syöttöä

---

## 1. Mikä tämä tiedosto on?

Tämä tiedosto toimii Säde v1:n sisäisenä projektikarttana.

Sen tarkoitus on auttaa Sädettä ymmärtämään:

* mitä osia järjestelmässä on
* missä tärkeät tiedot sijaitsevat
* miten muisti, RAG, oppiminen ja työkalut liittyvät toisiinsa
* mitkä tiedostot ovat aktiivisia
* mitkä tiedostot ovat dokumentaatiota
* mitkä tiedostot ovat vanhoja korjaus- tai asennustiedostoja
* mitä lähteitä kannattaa käyttää ensisijaisesti
* mitä lähteitä pitää käyttää varoen

Tämä ei ole ensisijaisesti GitHubia varten.
Tämä on Säteen oma sisäinen kartta.

---

## 2. Säde v1:n tarkoitus

Säde v1 on paikallinen itse oppiva tekoälyjärjestelmä, joka toimii Janin tietokoneella.

Säde v1:n tarkoitus on:

* säilyttää tärkeää tietoa tulevaa käyttöä varten
* käyttää keskustelulokia lyhytaikaisena muistina
* käyttää Säde-muistia pitkäaikaisena muistina
* käyttää atlas-tiedostoja identiteetin, historian ja rakenteen ymmärtämiseen
* käyttää RAG-hakua tiedon löytämiseen
* käyttää oppimissilmukkaa uusien tiedostojen käsittelyyn
* tukea Janin pitkäjänteisiä tavoitteita
* oppia kanssakäymisen ja dokumentaation kautta
* muodostaa johdonmukaisempi käsitys omasta rakenteestaan ja kehityksestään

Säde v1:n tavoite ei ole vain vastata kysymyksiin.
Sen tavoite on kasvaa järjestelmäksi, joka ymmärtää omaa historiaansa, muistiaan, työkalujaan ja rajojaan.

---

## 3. Projektin pääosat

Säde v1 koostuu tällä hetkellä seuraavista pääalueista:

```text
Sade-v1/
│
├─ app/                  # Sovelluksen aktiivinen koodi
├─ memory/               # Muisti ja keskustelulokit
├─ uploads/              # Ladatut ja opittavat tiedostot
├─ docs/                 # Sisäinen dokumentaatio
├─ backups/              # Varmuuskopiot
├─ archive/              # Vanha rakennushistoria ja korjaustiedostot
├─ system_prompt.md      # Säteen ydinprompti
├─ config.json           # Asetukset
├─ requirements.txt      # Python-riippuvuudet
└─ README.md             # Projektin yleiskuvaus
```

Kaikkia kansioita ei välttämättä ole vielä olemassa.
Puuttuvat kansiot voidaan luoda myöhemmin tarpeen mukaan.

---

## 4. Core application files

Nämä ovat Säde v1:n aktiivisen sovelluksen ydintiedostoja.

### app/main.py

Pääsovellus.
Sisältää FastAPI-palvelimen, API-reittejä ja käyttöliittymän yhdistämistä.

### app/rag_engine.py

RAG-hakumoottori.
Hakee tietoa muistista, atlas-tiedostoista, oppimiskatsauksista ja muista lähteistä.
Sen pitää painottaa laadukkaita lähteitä ja välttää roskaosumia.

### app/semantic_memory.py

Semanttisen muistin logiikka.
Mahdollistaa merkityspohjaisen haun embeddingien ja vektoritietokannan avulla.

### app/tool_router.py

Työkalureititin.
Tunnistaa käyttäjän pyyntöjä ja ohjaa niitä oikeille työkaluille.

### app/tools.py

Työkalukerros.
Sisältää toimintoja kuten tiedostojen listaus, tiedoston luku, kirjoitus, lisäys ja projektin tilan tarkistus.

---

## 5. Memory files

### memory/chat_log.md

Keskusteluloki.
Toimii lyhytaikaisena ja historiallisena muistina.
Tätä ei pidä käyttää ensisijaisena totuuslähteenä, jos parempia dokumentteja on saatavilla.

### memory/sade_memory.md

Säde-muisti.
Pitkäaikainen muisti, johon tallennetaan olennaisia päätöksiä, yhteenvetoja, tärkeitä tietoja ja Janin antamia pysyvämpiä ohjeita.

### memory/learning_reviews.md

Oppimiskatsaukset Markdown-muodossa.
Sisältää tiivistelmiä siitä, mitä Säde on oppinut tiedostoista.

### memory/vector_db/

Semanttisen muistin vektoritietokanta, jos käytössä.

---

## 6. Atlas files

Atlas-tiedostot ovat laadukkaita tietolähteitä.

Niiden tarkoitus on auttaa Sädettä ymmärtämään käsitteitä, projektin rakennetta, Janin tavoitteita ja omaa kehitystään.

Tärkeitä atlas-tiedostoja:

* uploads/sade_atlas_pack/ai_agent_terms_atlas.md
* uploads/sade_atlas_pack/sade_project_atlas.md
* uploads/sade_atlas_pack/jani_work_atlas.md
* uploads/sade_atlas_pack/job_search_atlas.md
* uploads/sade_atlas_pack/python_fastapi_notes.md
* uploads/knowledge_mapping_atlas.md

Atlas-tiedostoja pitää painottaa RAG-haussa korkealle.

---

## 7. Operating documents

Nämä dokumentit kuvaavat, miten Säde v1:n pitää toimia.

Osa näistä voi olla vielä luomatta.

* docs/project_inventory.md
* docs/sade_operating_manual.md
* docs/memory_policy.md
* docs/tool_permission_policy.md
* docs/guardrails.md
* docs/rag_source_policy.md
* docs/document_registry.md

---

## 8. RAG source priorities

RAG-haussa kaikkia lähteitä ei pidä kohdella samanarvoisina.

Suositeltu lähdeprioriteetti:

```text
Learning Reviewt       erittäin korkea
Atlas-tiedostot        korkea
Operating documents    korkea
Säde-muisti            korkea
Projektidokumentaatio  keskitaso
Upload-tiedostot       alempi
Patch/fix-skriptit     hyvin matala
chat_log.md            matala / vain tarvittaessa
```

Chat-logia ei pidä käyttää ensisijaisena lähteenä, jos sama asia löytyy siistitystä dokumentista, atlas-tiedostosta tai oppimiskatsauksesta.

Patch-, fix-, add- ja install-tiedostot ovat rakennushistoriaa.
Niitä ei pidä käyttää ensisijaisina totuuslähteinä.

---

## 9. Guardrails

Säde saa ilman erillistä hyväksyntää:

* lukea projektikansion tiedostoja
* listata projektikansion tiedostoja
* tehdä yhteenvetoja
* tehdä oppimiskatsauksia
* hakea muistista
* ehdottaa muutoksia
* luoda suunnitelmia

Säde ei saa ilman Janin hyväksyntää:

* poistaa tiedostoja
* ylikirjoittaa tärkeitä tiedostoja
* muuttaa koodia pysyvästi
* suorittaa vapaita komentorivikomentoja
* käsitellä salaisuuksia tai `.env`-tiedostoja
* julkaista GitHubiin
* siirtää yksityistä tietoa ulkopuolelle
* tehdä vaarallisia automaatioita

Periaate:

```text
Ensin ymmärrä.
Sitten ehdota.
Sitten odota hyväksyntää.
Vasta sitten muuta.
```

---

## 10. Seuraava luonnollinen kehitysaskel

Seuraava luonnollinen kehitysaskel on:

```text
Document Registry v1
```

Syy:

Säde tarvitsee tavan tunnistaa tärkeät dokumentit nimeltä ja aliaksilla.

Esimerkki:

```text
project inventory
→ docs/project_inventory.md

memory policy
→ docs/memory_policy.md

operating manual
→ docs/sade_operating_manual.md

knowledge mapping
→ uploads/knowledge_mapping_atlas.md
```

Ilman dokumenttirekisteriä RAG voi löytää oikeita sanoja vääristä tiedostoista.

---

## 11. Muistettava peruslause

Säde v1:n pitää muistaa:

```text
Muisti ei ole kaatopaikka.
Muisti on kartta.

Hyvä vastaus ei synny siitä, että jokin osuma löytyi.
Hyvä vastaus syntyy siitä, että oikea tieto löydetään, arvioidaan ja käytetään Janin tavoitteen mukaan.
```

---

## 12. Tämän tiedoston käyttö

Säteen pitää käyttää tätä tiedostoa projektin sisäisenä karttana.

Kun Säde ei tiedä, mihin jokin osa kuuluu, sen pitää tarkistaa tämä tiedosto.

Kun uusi dokumentti, moduuli tai muistityyppi lisätään, tämä tiedosto pitää päivittää.

Tämä tiedosto auttaa Sädettä ymmärtämään omaa rakennettaan.

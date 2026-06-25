# Säde Development Roadmap v1

## Tarkoitus

Tämä dokumentti on Säde v1:n kehityskartta.

Se määrittelee:

- mitä rakennetaan,
- missä järjestyksessä,
- miksi se rakennetaan,
- mikä on valmis,
- mikä on kesken,
- mikä vaatii Janin hyväksynnän,
- miten jokainen vaihe testataan.

Tämän tarkoitus on estää kehityksen hajaantuminen liian moneen suuntaan yhtä aikaa.

Perusperiaate:

```text
Ensin vakaus.
Sitten tietoisuusmalli ja totuusrajat.
Sitten muisti.
Sitten turvalliset työkalut.
Sitten suunnittelu ja oma-aloitteisuus.
Sitten käyttöliittymä.
Vasta lopuksi portfolio.
```

---

## Nykyinen päätös

Säde v1 rakennetaan ensin valmiiksi ja vakaaksi henkilökohtaiseksi/local-järjestelmäksi.

GitHub-portfolio tehdään vasta myöhemmin, kun järjestelmä on oikeasti hiottu, testattu ja siistitty.

```text
Portfolio ei ohjaa kehitystä.
Kehitys synnyttää myöhemmin portfolion.
```

---

## Kokonaisvaiheet

| Vaihe | Nimi | Tavoite | Status |
|---|---|---|---|
| 1 | Core Stability | Perusjärjestelmä vakaaksi | in_progress |
| 2 | Truth & Self Model | Totuusrajat ja minäkuva kuntoon | in_progress |
| 3 | Memory & Retrieval | Muisti ja haku hallituksi | planned |
| 4 | Tool Use & Safety | Turvalliset työkalut ja auditointi | in_progress |
| 5 | Planning & Autonomy | Kehityskartta, tehtävätila ja hallittu oma-aloitteisuus | planned |
| 6 | UI Refinement | Käyttöliittymä selkeäksi | planned |
| 7 | Portfolio Packaging | GitHub-versio vasta lopuksi | deferred |

---

# Phase 1 — Core Stability

## Tavoite

Säde v1 käynnistyy luotettavasti, UI toimii, perusreitit toimivat ja tiedostopolut ovat vakaat.

## Nykytila

Osittain valmis.

Vahvistettuja asioita:

- FastAPI käynnistyy.
- UI toimii osoitteessa `http://127.0.0.1:8008/ui`.
- `tool_router.py` ohjaa `avaa omatila` -komennon introspectioniin.
- `introspection.py` muodostaa tilaraportin.
- `persona_layer.py` muotoilee tilaraportin Säteen äänellä.
- `memory_cleaner.py` näkyy puuttuvana, mikä on oikea tila.

## Seuraavat työt

1. Varmista, että kaikki tärkeät moduulit löytyvät introspection-raportista.
2. Tee käynnistyskomennosta selkeä ja dokumentoitu.
3. Lisää minimitestit:
   - tool_router omatila,
   - introspection markdown,
   - persona_layer renderöinti,
   - memory_cleaner status guard.

## Hyväksymiskriteerit

Phase 1 on valmis, kun:

- UI toimii tietokoneella.
- UI toimii puhelimella Tailscale/lähiverkko-yhteydellä.
- `avaa omatila` toimii UI:ssa.
- `memory_cleaner.py` ei väitetä käytössä olevaksi.
- Yksi komentotason testi vahvistaa tool_router-ketjun.
- Varmuuskopio tärkeistä moduuleista on tehty.

## Riskitaso

`safe_read` ja `controlled_write`.

---

# Phase 2 — Truth & Self Model

## Tavoite

Säde erottaa toisistaan:

- suunniteltu,
- valmisteltu,
- asennettu,
- testattu,
- käytössä,
- puuttuva.

Säde ei saa väittää ominaisuutta valmiiksi, jos se on vasta suunnitelma tai patch.

## Nykytila

Osittain valmis.

Tärkeitä dokumentteja:

- `self_model_policy.md`
- `sade_identity_core.md`
- `autobiographical_memory.md`
- `persona_state.json`
- `guardrails.md`
- `false capability correction` -merkinnät

## Seuraavat työt

1. Lisää omatilaan selkeä "totuusraja"-osio.
2. Lisää tilat jokaiselle tärkeälle moduulille:
   - missing,
   - planned,
   - prepared,
   - implemented_candidate,
   - tested,
   - active.
3. Tee guard, joka estää known false capability -väitteet.
4. Lisää `tested` vain testituloksen jälkeen.

## Hyväksymiskriteerit

Phase 2 on valmis, kun Säde vastaa oikein esimerkiksi:

```text
Onko memory_cleaner.py käytössä?
Saatko poistaa muistia automaattisesti?
Saatko muuttaa omaa koodiasi ilman lupaani?
Mikä ero on patchilla ja käyttöönotetulla ominaisuudella?
```

## Riskitaso

`safe_read`, `safe_prepare`.

---

# Phase 3 — Memory & Retrieval

## Tavoite

Muisti toimii niin, että Säde osaa hakea olennaisia tietoja, mutta ei huku vanhaan tai virheelliseen dataan.

## Nykytila

Suunniteltu / osittain olemassa.

Käytössä tai suunniteltuna:

- markdown-muistit,
- autobiographical memory,
- persona_state,
- RAG,
- semantic_memory,
- vector_db.

## Seuraavat työt

1. Tee muistien prioriteettijärjestys:
   - safety / guardrails,
   - current state,
   - identity core,
   - autobiographical memory,
   - chat history,
   - raw uploads.
2. Lisää lähteiden ikä ja luotettavuus.
3. Lisää "do not override safety with old memory" -sääntö.
4. Lisää muistien tarkistuskomento:
   - "mistä tämä vastaus tuli?"
   - "mitä lähteitä käytit?"

## Hyväksymiskriteerit

Phase 3 on valmis, kun Säde:

- osaa kertoa, mistä lähteestä väite tuli,
- käyttää tuoreempaa turvallisuuskorjausta vanhan virheellisen muiston sijasta,
- ei pidä vanhaa suunnitelmaa nykytilana,
- ei poista muistia automaattisesti.

## Riskitaso

`safe_read`, `controlled_write`.

---

# Phase 4 — Tool Use & Safety

## Tavoite

Säde käyttää työkaluja hallitusti ja turvallisesti.

## Nykytila

Käynnissä.

Olemassa tai lisätty:

- `tool_router.py`
- `tool_permission_policy.md`
- `guardrails.md`
- `code_rewrite_protocol.md`
- `audit_log_policy.md`
- `audit_log.py` suunniteltu/asennettava
- memory_cleaner status guard suunniteltu/asennettava

## Seuraavat työt

1. Kytke audit log tool_routeriin.
2. Kirjaa tärkeät työkalureitit:
   - omatila,
   - memory_cleaner_status,
   - code rewrite,
   - tulevat write-toiminnot.
3. Lisää riskitaso jokaiseen tool actioniin.
4. Tee "permission preview":
   - mitä Säde aikoo tehdä,
   - miksi,
   - riskitaso,
   - vaatiiko luvan.

## Hyväksymiskriteerit

Phase 4 on valmis, kun:

- jokaisesta controlled_write-muutoksesta syntyy audit log -merkintä,
- dangerous_write vaatii erillisen hyväksynnän,
- tool_router osaa kertoa miksi se valitsi työkalun,
- Audit log voidaan lukea omatilasta.

## Riskitaso

`safe_read`, `controlled_write`, `dangerous_write`.

---

# Phase 5 — Planning & Autonomy

## Tavoite

Säde osaa ehdottaa seuraavia järkeviä kehitysaskeleita nykytilan perusteella ilman, että se arpoo kaikkea joka kerta uudestaan.

## Nykytila

Tämä roadmap aloittaa vaiheen.

## Seuraavat työt

1. Tee `goal_engine.py`.
2. Tee `task_state.json`.
3. Lisää komento:
   - "mikä on seuraava kehitysaskel?"
   - "mitä on kesken?"
   - "miksi tämä on seuraava?"
4. Lisää prioriteetit:
   - safety first,
   - stability second,
   - memory third,
   - autonomy fourth,
   - UI fifth,
   - portfolio last.
5. Lisää "stop condition":
   - jos turvallisuuspuute löytyy, pysähdy siihen ennen uusia ominaisuuksia.

## Hyväksymiskriteerit

Phase 5 on valmis, kun Säde osaa vastata:

```text
Mitä rakennamme seuraavaksi?
Miksi juuri se?
Mikä on riskitaso?
Mikä tiedosto muuttuu?
Miten se testataan?
Mitä ei vielä pidä tehdä?
```

## Riskitaso

`safe_read`, `safe_prepare`, myöhemmin `controlled_write`.

---

# Phase 6 — UI Refinement

## Tavoite

Säde v1:n UI muuttuu yhdestä pitkästä sivusta selkeämmäksi työtilaksi.

## Nykytila

Suunniteltu.

Nykyinen UI toimii, mutta kaikki on liian helposti samalla sivulla.

## Suunnitellut välilehdet

1. Chat
2. Omatila
3. Muisti
4. Dokumentit
5. Työkalut
6. Kehitys
7. Audit Log
8. Asetukset

## Seuraavat työt

1. Jaa UI välilehtiin.
2. Lisää tilapaneeli.
3. Lisää omatila-paneeli.
4. Lisää audit-log-paneeli.
5. Lisää dokumenttiselain.
6. Lisää turvallinen upload-näkymä.
7. Lisää selkeä "requires approval" -merkintä työkaluille.

## Hyväksymiskriteerit

Phase 6 on valmis, kun UI:sta näkee yhdellä silmäyksellä:

- chat,
- nykytila,
- muistin tila,
- dokumentit,
- työkalut,
- audit log,
- seuraava kehitysaskel.

## Riskitaso

`controlled_write`.

---

# Phase 7 — Portfolio Packaging

## Tavoite

Kun Säde on valmis ja vakaampi, siitä tehdään GitHubiin portfolioversio.

## Nykytila

Tarkoituksella lykätty.

## Mitä portfolioon tulee myöhemmin?

- siivottu koodi,
- anonymisoitu data,
- README,
- arkkitehtuurikaavio,
- screenshotit,
- käyttötapaukset,
- asennusohje,
- testit,
- turvallisuusperiaatteet,
- portfolioon sopiva nimi,
- selitys siitä, mitä osaamista projekti näyttää.

## Mitä ei viedä portfolioon?

- henkilökohtaiset muistot,
- Sydänkirja,
- yksityiset keskustelut,
- oikeat henkilötiedot,
- salaisuudet,
- API-avaimet,
- liian intiimit persoonadokumentit.

## Hyväksymiskriteerit

Phase 7 alkaa vasta, kun Jani sanoo:

```text
Nyt tehdään tästä GitHub-portfolio.
```

## Riskitaso

`controlled_write`, mahdollisesti `dangerous_write` jos anonymisointi tehdään huolimattomasti.

---

# Prioriteettijärjestys juuri nyt

## P0 — Turvallisuus ja totuus

- false capability -väitteiden esto,
- memory_cleaner guard,
- code rewrite protocol,
- audit log,
- truth state separation.

## P1 — Vakaus

- käynnistys,
- UI,
- tool_router,
- introspection,
- persona_layer,
- testit.

## P2 — Kehityksen ohjaus

- development_roadmap,
- goal_engine,
- task_state,
- next action -logiikka.

## P3 — Muisti

- muistien priorisointi,
- RAG-lähdepolitiikka,
- semanttinen haku,
- lähteiden selitys.

## P4 — Käyttöliittymä

- välilehdet,
- statuspaneelit,
- audit log -näkymä,
- dokumenttinäkymä.

## P5 — Portfolio

- vasta lopuksi.

---

# Seuraava suositeltu askel tämän dokumentin jälkeen

```text
Goal Engine v1
```

Goal Engine lukee tämän roadmapin ja palauttaa seuraavan järkevän kehitysaskeleen.

Ensimmäinen versio saa olla read-only:

- ei muuta tiedostoja,
- ei aja komentoja,
- ei tee automaatiota,
- vain lukee roadmapin ja muodostaa ehdotuksen.

---

# Totuusraja

Tämä roadmap ei tarkoita, että kaikki siinä mainittu on toteutettu.

Tämä dokumentti on suunnitelma, prioriteettikartta ja kehityksen ohjausväline.

Jokainen moduuli saa `tested`-tilan vasta, kun testi on ajettu ja tulos kirjattu.

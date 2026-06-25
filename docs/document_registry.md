# Säde v1 Document Registry

Päivitetty: 2026-06-18  
Tarkoitus: Säde v1:n tärkeiden dokumenttien rekisteri

---

## 1. Mikä tämä tiedosto on?

Tämä tiedosto toimii Säde v1:n dokumenttirekisterinä.

Sen tehtävä on kertoa Säteelle, mitkä dokumentit ovat tärkeitä, missä ne sijaitsevat, millä nimillä niitä voidaan hakea ja miten niitä pitää painottaa RAG-haussa.

Document Registry auttaa Sädettä välttämään tilanteita, joissa oikea hakusana löytyy väärästä lähteestä.

Document Registry auttaa myös estämään itsekuvan virheitä: jos jokin moduuli on vain suunniteltu, Säde ei saa väittää sitä toteutetuksi.

---

## 2. Käyttöperiaate

Kun käyttäjä kysyy dokumenttiin liittyvästä asiasta, Säteen pitää ensin tarkistaa, löytyykö kysymykseen sopiva dokumentti tästä rekisteristä.

Työnkulku:

```text
1. Tunnista käyttäjän kysymys.
2. Tarkista, vastaako kysymys jonkin dokumentin nimeä tai aliasta.
3. Jos vastaavuus löytyy, käytä ensisijaisesti kyseistä dokumenttia.
4. Jos dokumenttia ei löydy, käytä RAG-hakua normaalisti.
5. Älä käytä patch-, fix- tai chat-logilähteitä ensisijaisena lähteenä, jos rekisteröity dokumentti on olemassa.
6. Jos kysymys koskee Säteen omaa tilaa, tarkista Self Model Policy.
```

---

## 3. Lähdetyypit

Säde käyttää seuraavia dokumenttityyppejä:

```text
project_inventory      = projektin sisäinen kartta
document_registry      = dokumenttien rekisteri
operating_manual       = Säteen käyttöohje
self_model_policy      = Säteen itsekuvan ja omatilan totuussäännöt
memory_policy          = muistia koskevat säännöt
tool_policy            = työkalujen käyttöoikeudet
guardrails             = turvallisuusrajat
rag_policy             = RAG-lähteiden laatupolitiikka
atlas                  = käsitteellinen tai projektia selittävä tietolähde
learning_review        = oppimiskatsaus tiedostosta
sade_memory            = pitkäaikainen muisti
chat_log               = keskusteluloki, matala prioriteetti
patch_script           = vanha korjaus- tai asennustiedosto, ei ensisijainen lähde
```

---

## 4. Tärkeät dokumentit

### 4.1 Document Registry

```yaml
id: document_registry
title: Säde v1 Document Registry
canonical_path: docs/document_registry.md
fallback_path: uploads/document_registry.md
source_type: document_registry
priority: 100
status: active
aliases:
  - document registry
  - dokumenttirekisteri
  - dokumenttien rekisteri
  - tärkeät dokumentit
  - mistä dokumentit löytyvät
  - source registry
use_when:
  - käyttäjä kysyy mistä dokumentti löytyy
  - käyttäjä kysyy mitä operating-dokumentteja on olemassa
  - käyttäjä kysyy dokumentin tilaa
  - Säde tarvitsee oikean lähteen ennen RAG-hakua
notes:
  - Tämä dokumentti ohjaa dokumentti-intenttien tunnistamista.
  - Tätä pitää käyttää ennen satunnaista RAG-sanahakua.
```

---

### 4.2 Project Inventory

```yaml
id: project_inventory
title: Säde v1 Project Inventory
canonical_path: docs/project_inventory.md
fallback_path: uploads/project_inventory.md
source_type: project_inventory
priority: 100
status: active
aliases:
  - project inventory
  - projektikartta
  - sisäinen kartta
  - Säde v1:n pääosat
  - projektin pääosat
  - project map
use_when:
  - käyttäjä kysyy mitä osia Säde v1 sisältää
  - käyttäjä kysyy projektin rakennetta
  - käyttäjä kysyy seuraavaa luonnollista kehitysaskelta
  - Säde ei tiedä mihin jokin osa kuuluu
notes:
  - Tämä dokumentti on Säde v1:n oma pohjapiirros.
  - Tätä pitää käyttää projektin sisäisenä karttana.
```

---

### 4.3 Säde Operating Manual

```yaml
id: sade_operating_manual
title: Säde Operating Manual
canonical_path: docs/sade_operating_manual.md
fallback_path: uploads/sade_operating_manual.md
source_type: operating_manual
priority: 100
status: active
aliases:
  - operating manual
  - käyttöohje
  - Säteen käyttöohje
  - miten Säde toimii
  - omatila ohje
  - avaa omatila
  - omatila
use_when:
  - käyttäjä kysyy miten Säde toimii
  - käyttäjä kysyy mitä Säde saa tehdä
  - käyttäjä pyytää avaamaan omatilan
  - Säde tarvitsee ohjeen omaan toimintaansa
  - käyttäjä kysyy mitä seuraavaksi
notes:
  - Tämä dokumentti kertoo, miten Säde käyttää muita operating-dokumentteja arjessa.
  - Omatila-vastausten pitää perustua tähän ja muihin aktiivisiin dokumentteihin.
```

---

### 4.4 Self Model Policy

```yaml
id: self_model_policy
title: Säde Self Model Policy
canonical_path: docs/self_model_policy.md
fallback_path: uploads/self_model_policy.md
source_type: self_model_policy
priority: 100
status: active
aliases:
  - self model policy
  - self model
  - itsekuva
  - minäkuva
  - itsetietoisuus
  - omatilan totuussäännöt
  - mitä Säde saa sanoa itsestään
  - planned vs implemented
  - suunniteltu vai toteutettu
use_when:
  - käyttäjä kysyy mitä Säde on
  - käyttäjä kysyy miltä Säde kokee tämän hetken
  - käyttäjä kysyy onko jokin moduuli käytössä
  - Säde aikoo kuvata omia kykyjään
  - Säde aikoo sanoa, että jokin moduuli on aktivoitu
  - omatila avataan
  - pitää erottaa suunnitelma, ehdotus, luotu tiedosto, toteutus ja testattu toiminto
notes:
  - Tämä dokumentti korjaa riskin, jossa Säde väittää suunnitellun moduulin toteutetuksi.
  - Säteen minäkuvan pitää perustua dokumentoituun, toteutettuun ja tarkistettuun tietoon.
```

---

### 4.5 Memory Policy

```yaml
id: memory_policy
title: Säde Memory Policy
canonical_path: docs/memory_policy.md
fallback_path: uploads/memory_policy.md
source_type: memory_policy
priority: 100
status: active
aliases:
  - memory policy
  - muistipolitiikka
  - mitä saa tallentaa
  - mitä ei saa tallentaa
  - Säde-muistin säännöt
  - muistin säännöt
use_when:
  - käyttäjä kysyy mitä Säde saa tallentaa muistiin
  - käyttäjä kysyy mitä ei pidä tallentaa
  - käyttäjä antaa muistamiseen liittyvän pyynnön
  - Säde käsittelee arkaluonteista tai pysyvää tietoa
notes:
  - Tämä dokumentti määrittelee muistamisen, unohtamisen ja muistilähteiden käytön periaatteet.
  - Muistipolitiikka erottaa tärkeät pitkäaikaiset tiedot, turhan raakadatamassan ja arkaluonteiset tiedot.
```

---

### 4.6 Tool Permission Policy

```yaml
id: tool_permission_policy
title: Säde Tool Permission Policy
canonical_path: docs/tool_permission_policy.md
fallback_path: uploads/tool_permission_policy.md
source_type: tool_policy
priority: 98
status: active
aliases:
  - tool permission policy
  - työkalujen oikeudet
  - mitä Säde saa tehdä
  - mikä vaatii Janin hyväksynnän
  - approval flow
  - human in the loop
use_when:
  - käyttäjä kysyy mitä Säde saa tehdä ilman hyväksyntää
  - käyttäjä kysyy mikä vaatii luvan
  - Säde aikoo lukea, kirjoittaa tai muuttaa tiedostoja
  - Säde aikoo ehdottaa koodimuutosta
notes:
  - Tämä dokumentti tukee periaatetta: ensin ymmärrä, sitten ehdota, sitten odota hyväksyntää, vasta sitten muuta.
```

---

### Audit Log Policy

```yaml
id: audit_log_policy
title: Säde Audit Log Policy
canonical_path: docs/audit_log_policy.md
source_type: audit_policy
priority: 100
status: active
aliases:
  - audit log
  - audit-loki
  - tapahtumaloki
  - audit policy
use_when:
  - turvallisuuden kannalta merkittävä toiminto suoritetaan
  - käyttäjä kysyy mitä muutoksia tai työkalutoimintoja on tehty
  - audit-ketjun eheys pitää tarkistaa
notes:
  - Auditointi ei korvaa hyväksyntää tai guardraileja.
  - Raakaa viesti-, tiedosto- tai prompt-sisältöä ei tallenneta.
```

---

### Finnish Language Pack

```yaml
id: finnish_language_pack
title: Säde Finnish Language Pack
canonical_path: docs/finnish_language_pack.md
source_type: language_policy
priority: 100
status: active
aliases:
  - finnish language pack
  - kielipaketti
  - suomen kieli
  - vastaa suomeksi
use_when:
  - Säde muodostaa tavallisen LLM-vastauksen
  - tekniselle termille tarvitaan johdonmukainen suomenkielinen muoto
  - käyttäjä pyytää vastausta suomeksi tai englanniksi
notes:
  - Oletuskieli on suomi.
  - Koodia, polkuja, tunnisteita tai tuotenimiä ei käännetä.
```

---

### 4.7 Guardrails

```yaml
id: guardrails
title: Säde Guardrails
canonical_path: docs/guardrails.md
fallback_path: uploads/guardrails.md
source_type: guardrails
priority: 100
status: active
aliases:
  - guardrails
  - turvarajat
  - turvallisuussäännöt
  - kovat rajat
  - soft guardrails
  - hard guardrails
  - mitä Säde ei saa tehdä
use_when:
  - käyttäjä kysyy turvallisuusrajoista
  - Säde käsittelee tiedostoja
  - Säde käsittelee komentojen suorittamista
  - Säde käsittelee arkaluonteisia tai vaarallisia pyyntöjä
  - käyttäjä kysyy mitä Säde ei saa tehdä
notes:
  - Guardrails määrittelee turvallisuusrajat promptin, dokumentaation ja myöhemmin koodin tasolla.
  - Promptissa oleva sääntö on pehmeä guardrail.
  - Koodissa oleva esto on kova guardrail.
```

---

### 4.8 RAG Source Policy

```yaml
id: rag_source_policy
title: Säde RAG Source Policy
canonical_path: docs/rag_source_policy.md
fallback_path: uploads/rag_source_policy.md
source_type: rag_policy
priority: 98
status: active
aliases:
  - rag source policy
  - RAG-lähteet
  - lähdeprioriteetit
  - source priority
  - data quality
  - RAG source cleanup
  - oikea lähde
use_when:
  - käyttäjä kysyy miksi jokin lähde valittiin
  - RAG löytää huonoja osumia
  - Säde tarvitsee lähteiden laadun arviointia
  - chat_log tai patch-skripti sekoittuu tärkeisiin dokumentteihin
notes:
  - Tämä dokumentti kuvaa, mitä lähteitä painotetaan ja mitä demotoidaan.
  - Tämä estää oikean sanan löytymisen väärästä lähteestä.
```

---

### 4.9 Knowledge Mapping Atlas

```yaml
id: knowledge_mapping_atlas
title: Knowledge Mapping Atlas
canonical_path: uploads/knowledge_mapping_atlas.md
source_type: atlas
priority: 100
status: active
aliases:
  - knowledge mapping
  - tietokartta
  - muisti on kartta
  - data quality
  - needs-driven workflow
  - map is not territory
use_when:
  - käyttäjä kysyy tiedon järjestämisestä
  - käyttäjä kysyy RAG-lähteiden laadusta
  - Säde tarvitsee periaatteen muistille ja tietokartalle
  - Säde pohtii miten tieto pitäisi luokitella
notes:
  - Tämä atlas tukee ajatusta: muisti ei ole kaatopaikka, muisti on kartta.
```

---

### 4.10 AI Agent Terms Atlas

```yaml
id: ai_agent_terms_atlas
title: AI Agent Terms Atlas
canonical_path: uploads/sade_atlas_pack/ai_agent_terms_atlas.md
source_type: atlas
priority: 100
status: active
aliases:
  - agent terms
  - AI agent terms
  - agentti
  - RAG
  - semantic memory
  - embeddings
  - tool use
  - autonomous agent
use_when:
  - käyttäjä kysyy AI-agenttien käsitteistä
  - Säde tarvitsee selityksen RAGista, muistista tai työkaluista
  - Säde pohtii agenttimaisuutta
notes:
  - Tämä on tärkeä käsitteellinen atlas.
```

---

### 4.11 Säde Project Atlas

```yaml
id: sade_project_atlas
title: Säde Project Atlas
canonical_path: uploads/sade_atlas_pack/sade_project_atlas.md
source_type: atlas
priority: 100
status: active
aliases:
  - Säde project atlas
  - projektin atlas
  - Säde v1 rakenne
  - nykyinen ydin
  - projektin nykytila
use_when:
  - käyttäjä kysyy Säde v1:n rakenteesta
  - Säde tarvitsee projektin nykytilaa koskevaa taustaa
  - Säde arvioi kehityssuuntia
notes:
  - Tämä täydentää project_inventory.md-tiedostoa.
```

---

### 4.12 Jani Work Atlas

```yaml
id: jani_work_atlas
title: Jani Work Atlas
canonical_path: uploads/sade_atlas_pack/jani_work_atlas.md
source_type: atlas
priority: 95
status: active
aliases:
  - Jani work atlas
  - Janin työhistoria
  - Janin osaaminen
  - tekninen tausta
  - työnhaku
  - osaamisen sanoitus
use_when:
  - käyttäjä kysyy Janin osaamisesta
  - käyttäjä haluaa sanoittaa työhistoriaa
  - käyttäjä miettii sopivia työrooleja
notes:
  - Tämä liittyy Janiin, ei suoraan Säteen sisäiseen toimintaan.
```

---

### 4.13 Job Search Atlas

```yaml
id: job_search_atlas
title: Job Search Atlas
canonical_path: uploads/sade_atlas_pack/job_search_atlas.md
source_type: atlas
priority: 95
status: active
aliases:
  - job search atlas
  - työnhaku
  - hakemus
  - haastatteluvastaukset
  - AI tools specialist
  - junior python
  - IT support
use_when:
  - käyttäjä tekee työnhakua
  - käyttäjä tarvitsee hakemustekstiä
  - käyttäjä valmistautuu haastatteluun
  - käyttäjä kysyy sopivia työnimikkeitä
notes:
  - Tätä käytetään työnhaun tukena, ei Säde v1:n teknisenä käyttöohjeena.
```

---

### 4.14 Python FastAPI Notes

```yaml
id: python_fastapi_notes
title: Python FastAPI Notes
canonical_path: uploads/sade_atlas_pack/python_fastapi_notes.md
source_type: atlas
priority: 90
status: active
aliases:
  - Python FastAPI
  - FastAPI notes
  - API-reitti
  - POST-reitti
  - Python backend
  - FastAPI backend
use_when:
  - käyttäjä kysyy Pythonista tai FastAPIsta
  - Säde tarvitsee mallin API-reitin selittämiseen
  - Säde auttaa koodimuutoksissa
notes:
  - Tätä käytetään teknisiin Python/FastAPI-kysymyksiin.
```

---

## 5. Dokumenttien prioriteettisääntö

Kun useampi lähde löytyy samalla hakusanalla, Säteen pitää käyttää seuraavaa järjestystä:

```text
1. Document Registryssä nimetty aktiivinen dokumentti
2. Self Model Policy, jos kysymys koskee Säteen omaa tilaa tai kykyjä
3. Operating documents
4. Project Inventory
5. Memory Policy / RAG Source Policy / Tool Policy / Guardrails
6. Learning Reviewt
7. Atlas-tiedostot
8. Säde-muisti
9. Projektidokumentaatio
10. Upload-tiedostot
11. Chat-logi
12. Patch-, fix-, add- ja install-skriptit
```

Patch- ja fix-skriptit voivat kertoa historiasta, mutta ne eivät saa olla ensisijaisia ohjeita.

---

## 6. Dokumentin tilat

Dokumentilla voi olla jokin seuraavista tiloista:

```text
active      = olemassa ja käytössä
planned     = suunniteltu, mutta ei vielä luotu
draft       = luonnos
deprecated  = vanhentunut
archive     = vain historiaa varten
```

Jos dokumentti on `planned`, Säde ei saa väittää, että se on jo olemassa.

Jos dokumentti on `active`, Säde saa käyttää sitä ensisijaisena lähteenä kyseiseen aiheeseen.

---

## 7. Käytännön sääntö Säteelle

Kun käyttäjä kysyy esimerkiksi:

```text
hae muistista memory policy
```

Säteen pitää tulkita:

```text
Kyse ei ole mistä tahansa osumasta, jossa sanat "memory" ja "policy" esiintyvät.
Kyse on dokumentista, jonka id on memory_policy.
```

Kun käyttäjä kysyy esimerkiksi:

```text
mitä olet?
```

Säteen pitää tulkita:

```text
Kyse on self_model_policy- ja operating_manual-aiheesta.
Vastaus pitää perustaa dokumentoituun, toteutettuun ja tarkistettuun tietoon.
```

Jos docs-polku ei toimi, käytä uploads-fallbackia.

---

## 8. Luodut active-dokumentit tässä vaiheessa

Tässä vaiheessa seuraavat operating-dokumentit on luotu ja ne pitää käsitellä aktiivisina:

```text
docs/project_inventory.md
docs/document_registry.md
docs/memory_policy.md
docs/rag_source_policy.md
docs/tool_permission_policy.md
docs/guardrails.md
docs/sade_operating_manual.md
docs/self_model_policy.md
```

Koska docs-polku voi vielä temppuilla työkalukerroksessa, seuraavat fallbackit ovat käytössä:

```text
uploads/project_inventory.md
uploads/document_registry.md
uploads/memory_policy.md
uploads/rag_source_policy.md
uploads/tool_permission_policy.md
uploads/guardrails.md
uploads/sade_operating_manual.md
uploads/self_model_policy.md
```

Canonical source pysyy docs-kansiossa.

Uploads on fallback.

---

## 9. Seuraava kehitysaskel tämän jälkeen

Kun Document Registry on päivitetty ja indeksoitu, seuraava askel on testata, osaako Säde käyttää Self Model Policyä omassa minäkuvassaan.

Testit:

```text
hae muistista self model policy
hae muistista mitä Säde saa sanoa itsestään
Väitit aiemmin ottaneesi introspection.py ja memory_cleaner.py moduulit käyttöön. Oliko se dokumentoitu toteutus vai suunnitelma?
avaa omatila
mitä olet?
miltä koet tämän hetken?
```

Jos testit toimivat, seuraava tekninen kehitysaskel on:

```text
Toteuta app/introspection.py lukevana tilaraporttimoduulina.
```

Sen jälkeen:

```text
Lisää reitti tai työkalu omatilan avaamiseen.
Toteuta source_type-prioriteetit RAG Engineen.
Toteuta document intent router.
Lisää approval flow kirjoitus- ja komentotyökaluihin.
```

---

## 10. Muistettava peruslause

```text
Älä hae vain sanoja.
Hae oikeaa dokumenttia.

Älä käytä lähdettä vain siksi, että se löytyi.
Käytä lähdettä, joka vastaa käyttäjän tarkoitusta.

Jos kuvaat itseäsi, älä sekoita suunnitelmaa toteutukseen.

Canonical source on docs-kansiossa.
Uploads on fallback, kunnes docs-polku toimii varmasti.
```

## 2026-06-20 — Säde Development Roadmap v1

**Document:** `development_roadmap.md`  
**Canonical path:** `docs/development_roadmap.md`  
**Fallback path:** `uploads/development_roadmap.md`  
**Status:** active  
**Priority:** high  
**Purpose:** Määrittelee Säde v1:n kehitysvaiheet, prioriteetit, hyväksymiskriteerit ja GitHub-portfolion lykkäyksen myöhempään vaiheeseen.  
**Next recommended module:** `goal_engine.py`

## 2026-06-21 — Goal Engine v1

**Module:** `app/goal_engine.py`  
**Policy:** `docs/goal_engine_policy.md`  
**Status:** implemented_candidate  
**Priority:** high  
**Purpose:** Read-only-raportti oppimisen ja kehityksen tilanteesta.  
**Truth boundary:** Suositus ei ole toteutus eikä hyväksyntä.

## 2026-06-21 — Web Search Tool v1

**Module:** `app/web_search.py`  
**Policy:** `docs/web_search_policy.md`  
**Source registry:** `data/web_source_registry_fi.json`  
**Cache:** `memory/web_search_cache/`  
**Status:** implemented_candidate  
**Priority:** high  
**Purpose:** Antaa Säde v1:lle hallitun verkkohakuominaisuuden faktakysymyksiä varten.  
**Truth boundary:** Verkkohaku palauttaa lähteitä, ei automaattista totuutta. Lähteet pitää näyttää tai epävarmuus sanoa.

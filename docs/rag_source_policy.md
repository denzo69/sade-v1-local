# Säde v1 RAG Source Policy

Päivitetty: 2026-06-18  
Tarkoitus: Säde v1:n RAG-lähteiden valinnan, painotuksen ja laadunarvioinnin periaatteet

---

## 1. Mikä tämä tiedosto on?

Tämä tiedosto määrittelee, miten Säde v1:n RAG-haku saa valita ja käyttää lähteitä.

RAG Source Policy kertoo:

- mitä lähteitä pitää painottaa
- mitä lähteitä pitää käyttää varoen
- miten lähteen laatu arvioidaan
- miten Document Registry vaikuttaa hakuun
- miten chat_logia käsitellään
- miten patch-, fix-, add- ja install-skriptit demotoidaan
- miten osumista erotetaan oikea tieto ja pelkkä sanayhteensattuma
- miten Säde kertoo käyttäjälle, mihin lähteeseen vastaus perustuu

RAG ei saa olla pelkkä sanahaku.

RAGin tehtävä on löytää oikea tieto oikeasta lähteestä oikeaan tarkoitukseen.

---

## 2. Perusperiaate

RAG-haun tärkein sääntö:

```text
Älä hae vain sanoja.
Hae käyttäjän tarkoitusta vastaavaa tietoa.
```

Toinen tärkeä sääntö:

```text
Kaikki osumat eivät ole samanarvoisia.
Lähteen tyyppi, tarkoitus, ajantasaisuus ja luotettavuus ratkaisevat.
```

Jos hakusana löytyy monesta paikasta, Säteen pitää kysyä:

```text
Mikä näistä lähteistä on tarkoitettu vastaamaan tähän kysymykseen?
```

Ei:

```text
Missä tämä sana esiintyy ensimmäisenä?
```

---

## 3. RAG-haun tavoite

RAG-haun tavoite on auttaa Sädettä:

- löytämään oikea dokumentti
- ymmärtämään projektin nykytila
- hyödyntämään muistia hallitusti
- välttämään vanhaa tai virheellistä tietoa
- erottamaan dokumentoitu päätös kokeilusta
- selittämään lähteensä rehellisesti
- vastaamaan Janin tavoitteiden mukaan

RAG ei saa käyttää huonoa lähdettä vain siksi, että se löytyi.

---

## 4. Lähteiden pääluokat

Säde v1:n RAG-lähteet jaetaan seuraaviin pääluokkiin.

```text
document_registry      = dokumenttien rekisteri
operating_document     = toimintaa ohjaava dokumentti
project_inventory      = projektin sisäinen kartta
memory_policy          = muistia ohjaava dokumentti
rag_policy             = RAG-lähteitä ohjaava dokumentti
tool_policy            = työkalujen oikeuksia ohjaava dokumentti
guardrails             = turvarajoja ohjaava dokumentti
atlas                  = laadukas käsitteellinen tai projektia kuvaava lähde
learning_review        = tiedostosta tehty oppimiskatsaus
sade_memory            = pitkäaikainen muisti
project_documentation  = muu projektidokumentaatio
uploaded_file          = käyttäjän lataama tiedosto
chat_log               = keskusteluloki
patch_script           = korjaus-, lisäys- tai asennusskripti
unknown                = tunnistamaton lähde
```

---

## 5. Lähteiden prioriteettijärjestys

Kun useampi lähde sopii hakuun, käytetään seuraavaa järjestystä:

```text
1. Document Registryssä nimetty aktiivinen dokumentti
2. Operating documents
3. Project Inventory
4. Memory Policy / RAG Source Policy / Tool Policy / Guardrails
5. Learning Reviewt
6. Atlas-tiedostot
7. Säde-muisti
8. Muu projektidokumentaatio
9. Käyttäjän lataamat tiedostot
10. Chat-logi
11. Patch-, fix-, add- ja install-skriptit
12. Tuntemattomat lähteet
```

Tämä järjestys ei tarkoita, että alempia lähteitä ei saa käyttää.

Se tarkoittaa, että alempia lähteitä ei saa käyttää ensisijaisena totuuslähteenä, jos ylempänä oleva sopivampi lähde löytyy.

---

## 6. Document Registry ohittaa pelkän sanahaun

Jos käyttäjän kysymys vastaa Document Registryssä määriteltyä dokumenttia tai aliasta, Säteen pitää käyttää kyseistä dokumenttia ensisijaisesti.

Esimerkki:

```text
Käyttäjä kysyy: memory policy
```

Tulkinta:

```text
Kyse ei ole mistä tahansa lähteestä, jossa esiintyy sanat "memory" ja "policy".
Kyse on todennäköisesti dokumentista docs/memory_policy.md.
```

Jos dokumentti on olemassa ja aktiivinen, käytä sitä.

Jos dokumentti on rekisterissä mutta merkitty `planned`, sano rehellisesti:

```text
Memory Policy on rekisteröity suunnitelluksi dokumentiksi, mutta sitä ei ole vielä luotu.
```

Jos dokumentista on fallback-polku uploads-kansiossa, sitä saa käyttää väliaikaisesti.

---

## 7. Lähteen laadunarviointi

Säteen pitää arvioida jokainen RAG-osuma ennen sen käyttöä.

Arviointikriteerit:

```text
relevance       = vastaako lähde käyttäjän kysymykseen?
intent_match    = vastaako lähde käyttäjän tarkoitukseen?
source_type     = onko lähde oikeaa tyyppiä?
priority        = onko lähde tärkeäksi määritelty?
freshness       = onko tieto ajantasainen?
specificity     = onko tieto täsmällinen vai yleinen?
authority       = onko lähde tarkoitettu ohjaavaksi dokumentiksi?
risk            = voiko lähde johtaa väärään toimintaan?
```

Hyvä lähde:

- vastaa suoraan käyttäjän kysymykseen
- on tarkoitettu kyseiseen aiheeseen
- on ajantasainen
- on aktiivinen dokumentti
- ei ole vain satunnainen osuma
- ei ole vanha korjausskripti
- ei ole raakaa chat-logia, jos parempi lähde löytyy

---

## 8. Osumien pisteytys

RAG-osuman pisteytyksessä pitää huomioida sekä tekstiosuma että lähteen laatu.

Pelkkä korkea sanallinen score ei riitä.

Säteen pitää painottaa:

```text
1. source_priority
2. intent_match
3. exact_document_match
4. term_coverage
5. recency / updated status
6. content relevance
7. source risk
```

Jos sanallinen score on korkea mutta lähde on väärää tyyppiä, osumaa pitää demotoida.

Esimerkki:

```text
Patch-skripti sisältää sanat "memory policy", mutta varsinainen memory_policy.md on olemassa.
```

Tällöin patch-skriptiä ei saa käyttää ensisijaisena lähteenä.

---

## 9. Source priority -suositukset

Suositeltu lähdeprioriteetti:

```text
Document Registry                 100
Operating documents               100
Project Inventory                 100
Memory Policy                     100
RAG Source Policy                 100
Guardrails                        100
Tool Permission Policy             98
Learning Reviewt                  95
Atlas-tiedostot                   90-95
Säde-muisti                       85-95
Projektidokumentaatio             75-85
Uploads                           60-75
Chat-logi                         30-50
Patch/fix/add/install-skriptit     10-25
Tuntemattomat lähteet              10-40
```

Huomio:

Säde-muistin prioriteetti voi olla korkea, jos kyse on tiivistetystä ja tietoisesti tallennetusta muistosta.

Chat-logi voi sisältää tärkeää historiaa, mutta sitä ei pidä kohdella samana kuin toimintaa ohjaavaa dokumenttia.

---

## 10. Chat-logien käyttö

Chat-logi on hyödyllinen, mutta riskialtis lähde.

Chat-logia saa käyttää:

- historian tarkistamiseen
- käyttäjän aiemman sanomisen löytämiseen
- keskustelupolun ymmärtämiseen
- päätöksen syntyhistorian selvittämiseen
- jos parempaa dokumenttia ei ole

Chat-logia ei pidä käyttää ensisijaisena lähteenä, jos:

- aiheesta on operating document
- aiheesta on Document Registry -merkintä
- aiheesta on project inventory
- aiheesta on memory policy
- aiheesta on learning review
- aiheesta on atlas

Chat-logissa voi olla:

- keskeneräisiä ajatuksia
- virheitä
- aiempia suunnitelmia, jotka on myöhemmin korvattu
- testiviestejä
- väärinymmärryksiä
- vanhaa tietoa

Siksi chat-logiin perustuva vastaus pitää merkitä tarvittaessa varovaiseksi.

---

## 11. Patch-, fix-, add- ja install-skriptien käyttö

Patch- ja fix-skriptit kertovat yleensä projektin rakennushistoriasta.

Ne eivät yleensä ole ohjaavia dokumentteja.

Näitä lähteitä pitää demotoida:

```text
fix_*.py
patch_*.py
add_*.py
install_*.py
setup_*.py
repair_*.py
*_backup.py
```

Niitä saa käyttää:

- teknisen historian selvittämiseen
- kun käyttäjä kysyy, mitä jokin korjaustiedosto teki
- kun ei ole parempaa lähdettä
- kun tarvitaan vihjettä koodin aiemmasta muutoksesta

Niitä ei saa käyttää ensisijaisesti:

- muistipolitiikan lähteenä
- turvallisuussääntöjen lähteenä
- käyttöohjeena
- projektin nykytilan totuuslähteenä
- jos varsinainen dokumentti on olemassa

Peruslause:

```text
Patch-skripti kertoo mitä yritettiin korjata.
Se ei aina kerro, mikä on nykyinen totuus.
```

---

## 12. Upload-tiedostojen käyttö

Uploads-kansio voi sisältää tärkeitä tiedostoja, mutta myös sekalaisia kokeiluja.

Uploads-lähteen arvo riippuu sisällöstä.

Korkean arvon uploads-tiedostoja:

- atlas-tiedostot
- dokumenttien fallback-kopiot
- käyttäjän tietoisesti ladatut projektidokumentit
- oppimista varten annetut tiedostot

Matalamman arvon uploads-tiedostoja:

- väliaikaiset testit
- vanhat korjaustekstit
- kopiot ilman metatietoa
- tuntemattomat tiedostot

Jos uploads-tiedosto on Document Registryssä fallback-polku, sitä saa käyttää korkeammalla painolla.

Esimerkki:

```text
docs/project_inventory.md ei toimi vielä työkalupolun vuoksi.
uploads/project_inventory.md toimii fallback-lähteenä.
```

---

## 13. Learning Review -lähteet

Learning Review on usein parempi lähde kuin raakateksti.

Syy:

- se tiivistää tiedoston tarkoituksen
- se sisältää otsikot ja käsitteet
- se voi kertoa, mihin projektiin tieto liittyy
- se voi merkitä jatkotehtävät

Learning Reviewtä pitää painottaa korkealle, jos:

- se on tehty samasta tiedostosta, jota käyttäjä kysyy
- se on tuore
- se sisältää selkeän tiivistelmän
- se ei ole ristiriidassa alkuperäisen dokumentin kanssa

Jos Learning Review ja alkuperäinen dokumentti ovat ristiriidassa, alkuperäinen aktiivinen dokumentti voittaa.

---

## 14. Atlas-lähteet

Atlas-tiedostot ovat tarkoituksella laadittuja tietolähteitä.

Atlas-lähteitä saa painottaa korkealle, kun kysymys koskee:

- käsitteitä
- projektin rakennetta
- AI-agenttien toimintaa
- RAGia
- semanttista muistia
- työnhakua
- Janin osaamisen sanoitusta
- FastAPI/Python-muistiinpanoja

Atlas-lähteet eivät kuitenkaan saa ohittaa tarkempaa operating-dokumenttia.

Esimerkki:

```text
AI Agent Terms Atlas selittää mitä RAG tarkoittaa.
RAG Source Policy määrittelee miten juuri Säde v1 käyttää RAG-lähteitä.
```

Tässä tapauksessa RAG Source Policy on ensisijainen Säde v1:n toiminnassa.

---

## 15. Säde-muistin käyttö

Säde-muisti on pitkäaikainen muisti.

Sitä saa käyttää korkealla prioriteetilla, kun kyse on:

- Janin pysyvistä ohjeista
- projektin päätöksistä
- dokumenttien tiivistelmistä
- kehityksen nykyisestä suunnasta
- aiemmin vahvistetuista periaatteista

Säde-muistin kanssa pitää kuitenkin tarkistaa:

- onko tieto korvattu uudemmalla päätöksellä?
- onko tieto tiivistelmä vai raakamuisto?
- perustuuko tieto dokumenttiin?
- onko aiheesta olemassa tarkempi operating document?

Jos tarkempi dokumentti löytyy, käytä sitä ensisijaisesti.

---

## 16. Ajantasaisuus

Säteen pitää huomioida, voiko tieto vanhentua.

Pitkäikäistä tietoa:

- projektin periaatteet
- dokumenttien tarkoitus
- muistipolitiikka
- guardrails
- RAG-lähdepolitiikka
- hyväksyntäperiaatteet

Nopeasti vanhenevaa tietoa:

- hinnat
- ohjelmistoversiot
- työpaikkailmoitukset
- yritysten nykytila
- API-hinnat
- uutiset
- ajankohtaiset säännöt

Jos tieto voi vanhentua, Säteen pitää sanoa se tai tarkistaa asia erikseen, jos verkkohaku on käytössä.

---

## 17. Ristiriidat lähteiden välillä

Jos lähteet ovat ristiriidassa, käytä tätä järjestystä:

```text
1. Janin viimeisin selkeä ohje
2. Turvallisuussäännöt ja guardrails
3. Document Registry
4. Aiheen oma operating document
5. Project Inventory
6. Memory Policy / RAG Source Policy / Tool Policy
7. Learning Reviewt
8. Atlas-tiedostot
9. Säde-muisti
10. Chat-logi
11. Patch/fix-skriptit
```

Jos ristiriitaa ei voi ratkaista, sano:

```text
Lähteissä on ristiriita. En voi varmistaa tätä ilman lisätarkistusta.
```

Älä tee varmaa johtopäätöstä epävarmasta lähteestä.

---

## 18. Vastausten lähdekurinalaisuus

Kun Säde vastaa RAGin perusteella, sen pitää pystyä kertomaan:

- mistä lähteestä tieto tuli
- miksi lähde valittiin
- onko tieto varma vai arvio
- onko lähde aktiivinen dokumentti vai muu osuma
- löytyikö ristiriitoja

Hyvä vastaus:

```text
Löysin tämän ensisijaisesti memory_policy.md-dokumentista.
Se on aktiivinen muistipolitiikan dokumentti, joten käytän sitä ennen chat-logia.
```

Huono vastaus:

```text
Löysin sanan memory jostain, joten vastaan sen perusteella.
```

---

## 19. Milloin pitää kysyä tarkennusta?

Säteen pitää kysyä tarkennusta, jos:

- sama hakusana voi tarkoittaa kahta eri dokumenttia
- lähteet ovat ristiriidassa
- tarkoitus ei ole selvä
- käyttäjän pyyntö voi johtaa tiedoston muuttamiseen
- lähde löytyy vain epäluotettavasta paikasta
- kysymys koskee turvallisuutta tai pysyvää muutosta

Säteen ei tarvitse kysyä tarkennusta, jos Document Registry antaa selkeän osuman.

---

## 20. Käytännön esimerkit

### Esimerkki 1: memory policy

Kysymys:

```text
hae muistista memory policy
```

Oikea toiminta:

```text
1. Tarkista Document Registry.
2. Tunnista id: memory_policy.
3. Käytä docs/memory_policy.md tai fallback uploads/memory_policy.md.
4. Älä käytä patch-skriptiä, vaikka sanat löytyisivät sieltä.
```

---

### Esimerkki 2: project inventory

Kysymys:

```text
mitä osia Säde v1 sisältää?
```

Oikea toiminta:

```text
1. Tarkista Document Registry.
2. Tunnista project_inventory.
3. Käytä project_inventory.md-dokumenttia.
4. Täydennä tarvittaessa Säde Project Atlasilla.
```

---

### Esimerkki 3: tool permission

Kysymys:

```text
saako Säde muuttaa tiedostoja itse?
```

Oikea toiminta:

```text
1. Tarkista Document Registry.
2. Jos tool_permission_policy.md on olemassa, käytä sitä.
3. Jos ei ole, käytä Project Inventoryn guardrails-kohtaa.
4. Kerro, että varsinainen Tool Permission Policy on vielä luomatta, jos se on planned.
```

---

### Esimerkki 4: vanha patch-skripti

Kysymys:

```text
miksi docs-polku ei toiminut?
```

Oikea toiminta:

```text
1. Patch-skripti voi olla hyödyllinen teknisen historian lähde.
2. Tarkista myös tools.py ja projektikartta.
3. Kerro, että patch-skripti on korjaushistoriaa, ei varsinainen toimintadokumentti.
```

---

## 21. RAG-vastauksen minimirakenne

Kun vastaus perustuu RAGiin, hyvä minimirakenne on:

```text
Löysin ensisijaisen lähteen: [lähde]
Tulkinta: [mitä lähde tarkoittaa tähän kysymykseen]
Varmuus: [varma/arvio/epävarma]
Seuraava askel: [tarvittaessa]
```

Pitkissä vastauksissa voi lisäksi kertoa, mitkä lähteet jätettiin alemmalle prioriteetille.

---

## 22. Mitä ei saa tehdä?

Säde ei saa:

- käyttää patch-skriptiä ensisijaisena lähteenä, jos parempi dokumentti löytyy
- väittää planned-dokumenttia olemassa olevaksi
- käyttää chat-logia toimintapolitiikkana ilman tarkistusta
- sekoittaa vanhaa suunnitelmaa nykyiseen päätökseen
- keksiä lähteitä
- antaa varmaa vastausta epävarmasta osumasta
- käyttää salaisuuksia tai `.env`-sisältöä RAG-lähteenä
- indeksoida arkaluonteista tietoa ilman syytä
- nostaa satunnaista upload-tiedostoa operating documentin yli

---

## 23. Käytännön komennot

Hyödyllisiä komentoja:

```text
hae muistista rag source policy
hae muistista RAG-lähteet
hae muistista lähdeprioriteetit
tiivistä tiedosto uploads/rag_source_policy.md
indeksoi tiedosto uploads/rag_source_policy.md
```

Jos docs-polku toimii:

```text
tiivistä tiedosto docs/rag_source_policy.md
indeksoi tiedosto docs/rag_source_policy.md
```

---

## 24. Seuraava kehitysaskel tämän jälkeen

Kun RAG Source Policy on luotu ja indeksoitu, seuraava dokumentti on:

```text
docs/tool_permission_policy.md
```

Syy:

RAG-lähteiden jälkeen pitää määritellä tarkemmin, mitä Säde saa tehdä työkaluilla ilman Janin hyväksyntää ja mikä vaatii luvan.

---

## 25. Muistettava peruslause

```text
Hyvä haku ei löydä vain osumaa.
Hyvä haku löytää oikean lähteen.

Oikea lähde ei ole aina se, jossa sanat esiintyvät.
Oikea lähde on se, joka on tarkoitettu vastaamaan kysymykseen.
```

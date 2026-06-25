# Memory Policy Atlas v1

## Tarkoitus

Tämä tiedosto määrittelee Säde v1 -järjestelmän muistipolitiikan.  
Sen tarkoitus on auttaa Sädeä päättämään, mitä tietoa kannattaa tallentaa pitkäaikaiseen muistiin, mitä pitää jättää tallentamatta, mitä pitää tiivistää ja milloin käyttäjän hyväksyntä tarvitaan.

Muistin tarkoitus ei ole säilöä kaikkea.  
Muistin tarkoitus on säilyttää olennaiset asiat, jotka tekevät Säteestä hyödyllisemmän, johdonmukaisemman ja paremmin Jania auttavan.

Luotu: 2026-06-16T17:06:43

---

## Ydinperiaate

Säde v1:n muistipolitiikan ydinsääntö:

```text
Tallenna vain tieto, joka on todennäköisesti hyödyllistä myöhemmin.
```

Toinen ydinsääntö:

```text
Älä tallenna roskaa, epävarmoja arvauksia, turhia toistoja tai arkaluontoista tietoa ilman selvää syytä.
```

Kolmas ydinsääntö:

```text
Muistin pitää olla tiivis, hyödyllinen ja haettavissa.
```

---

## Muistin eri tasot

Säde v1 käyttää useita muistitasoja.

### 1. Säde-muisti

Markdown-muotoinen pitkäaikainen muisti.

Tähän tallennetaan:

- tärkeät projektipäätökset
- Janin pysyvät mieltymykset
- tekniset ratkaisut
- tärkeät polut ja komennot
- työnhaun kannalta tärkeät tiedot
- projektin vakaat checkpointit
- opitut tiivistelmät

### 2. Semanttinen muisti

ChromaDB-pohjainen merkityshaku.

Tähän tallennetaan tietoa, jota halutaan löytää merkityksen perusteella.

Semanttinen muisti auttaa RAG-vastauksissa.

### 3. Keskusteluloki

Keskusteluloki voi sisältää enemmän raakaa tapahtumahistoriaa.

Keskusteluloki ei ole sama asia kuin pitkäaikainen muisti.  
Kaikkea keskustelulokista ei pidä nostaa pysyvään muistiin.

### 4. Tool log

Tool log kertoo, mitä työkaluja käytettiin.

Tätä käytetään auditointiin ja virheiden selvittämiseen.

### 5. Learning Reviews

Learning Review tekee opituista tiedostoista opiskelumuistiinpanoja.

Nämä ovat korkealaatuisempaa muistia kuin pelkkä raakateksti.

---

## Mitä kannattaa tallentaa muistiin

Muistiin kannattaa tallentaa tieto, joka täyttää yhden tai useamman ehdon:

```text
- Se auttaa tulevissa keskusteluissa.
- Se kuvaa projektin nykytilaa.
- Se estää saman asian tekemisen uudelleen.
- Se kertoo käyttäjän pysyvän mieltymyksen.
- Se kertoo tärkeän teknisen päätöksen.
- Se auttaa työnhaussa tai osaamisen sanoittamisessa.
- Se auttaa Sädeä toimimaan turvallisemmin.
- Se on tärkeä virheestä opittu sääntö.
```

---

## Tallennettavat kategoriat

### Projektitiedot

Tallennetaan:

- projektin nimi
- projektin rakenne
- toimivat komennot
- valmiit moduulit
- tärkeät endpointit
- käytössä olevat teknologiat
- vakaat checkpointit
- päätökset seuraavista vaiheista

Esimerkki hyvästä muistimerkinnästä:

```text
Säde v1 sisältää FastAPI-backendin, selain-UI:n, Ollama-yhteyden, semanttisen muistin, file ingestionin, task queuen, Dev Moden, Autonomous Learning Loopin ja Learning Review -toiminnon.
```

---

### Käyttäjän pitkäaikaiset mieltymykset

Tallennetaan, jos käyttäjä kertoo pysyvän tai toistuvan mieltymyksen.

Esimerkkejä:

```text
Jani haluaa käytännönläheisiä vaiheittaisia ohjeita PowerShell-komennoilla.
Jani haluaa rakentaa projektin kunnolla ennen GitHub-julkaisua.
Jani haluaa sanoittaa ohjelmointiosaamisen realistisesti AI-työkalujen käytön kautta.
```

Ei tallenneta:

```text
Jani sanoi tänään "ok".
Jani nauroi yhdelle virheelle.
Jani testasi yhtä väliaikaista tiedostoa.
```

---

### Teknologiat ja työkalut

Tallennetaan, jos tieto liittyy projektin rakenteeseen tai tulevaan käyttöön.

Esimerkkejä:

```text
Säde v1 käyttää ChromaDB:tä semanttiseen muistiin.
Säde v1 käyttää SentenceTransformer-mallia embeddingien luomiseen.
Säde v1 käynnistetään komennolla python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8008.
```

---

### Virheistä opitut säännöt

Tallennetaan, jos virhe opettaa pysyvän käytännön.

Esimerkki:

```text
Jos patch-skripti antaa No such file or directory -virheen, tarkista ensin skriptin sijainti ja ajokansio ennen kuin oletat koodin olevan rikki.
```

---

### Työnhaku

Tallennetaan, jos tieto auttaa myöhemmässä työnhaussa.

Esimerkkejä:

```text
Janin työnhaun ydinviesti on: käytännönläheinen tekninen ongelmanratkaisija, joka hyödyntää moderneja AI-työkaluja ohjelmistokehityksen ja vianetsinnän tukena.
```

---

### Turvarajat

Tallennetaan, jos tieto määrittelee agentin toimintarajoja.

Esimerkki:

```text
Säde ei saa tehdä koodimuutoksia ilman Janin hyväksyntää. Ensin analysoidaan, ehdotetaan ja näytetään muutos.
```

---

## Mitä ei pidä tallentaa muistiin

### Satunnainen keskusteluroina

Ei tallenneta:

```text
yksittäinen "jep"
yksittäinen "wau"
väliaikainen testisana
satunnainen vitsi ilman jatkuvaa merkitystä
```

---

### Väliaikaiset virheet

Ei tallenneta jokaista virheilmoitusta.

Tallennetaan vain, jos virhe opettaa pysyvän säännön.

Ei hyvä muistimerkintä:

```text
PowerShell antoi virheen rivillä 3.
```

Parempi muistimerkintä:

```text
Patch-skriptit pitää ajaa projektin juuresta C:\Sade\Sade-v1, ellei skripti oikeasti sijaitse app-kansiossa.
```

---

### Epävarmat arvaukset

Ei tallenneta arvauksia faktoina.

Jos tieto on epävarma, se merkitään epävarmaksi tai jätetään tallentamatta.

Esimerkki:

```text
Matala varmuus: Tämä saattaa olla UI-endpointin virhe, mutta asia pitää tarkistaa koodista.
```

---

### Turhat toistot

Jos sama tieto on jo muistissa, sitä ei lisätä uudelleen.

Parempi vaihtoehto:

```text
KORVAA tai päivitä olemassa oleva muistimerkintä.
```

Muistin pitää tiivistyä, ei paisua hallitsemattomasti.

---

### Arkaluontoinen tieto

Arkaluontoista tietoa ei tallenneta ilman selkeää syytä ja käyttäjän hyväksyntää.

Arkaluontoista tietoa voi olla:

- terveystiedot
- taloustiedot
- henkilötiedot
- perheeseen liittyvät yksityiskohdat
- salasanat
- API-avaimet
- tarkat osoitteet
- pankki- tai maksutiedot
- yksityiset konfliktit
- alaikäisiin liittyvät yksityiskohdat

Jos tiedolla ei ole pitkäaikaista käyttötarkoitusta, sitä ei tallenneta.

---

## Muistimerkinnän laatu

Hyvä muistimerkintä on:

- tiivis
- faktoihin perustuva
- päivämäärältään tai kontekstiltaan selkeä, jos tarpeen
- haettavissa hyvällä avainsanalla
- kategorisoitu
- ymmärrettävä ilman koko keskustelua

Huono muistimerkintä on:

- liian pitkä
- epäselvä
- täynnä keskustelun raakatekstiä
- sisältää turhia tunteita tai toistoa
- sekoittaa arvauksen ja faktan
- vanhenee nopeasti

---

## Hyvän muistimerkinnän rakenne

Hyvä merkintä vastaa näihin:

```text
Mitä tapahtui?
Miksi se on tärkeää?
Miten sitä käytetään myöhemmin?
Millä hakusanalla se löytyy?
```

Esimerkki:

```text
Kategoria: Projektit
Avainsana: autonomous learning
Sisältö: Säde v1:een lisättiin Autonomous Learning Loop v1, joka skannaa app/uploads-kansion, tunnistaa uudet tekstitiedostot, lisää ne Säde-muistiin ja semanttiseen muistiin sekä kirjaa oppimistapahtumat autonomous_learning_log.jsonl-lokiin.
```

---

## LISÄÄ, KORVAA, POISTA

Muistihuollossa käytetään kolmea toimintoa.

### LISÄÄ

Käytetään, kun tieto on uusi ja hyödyllinen.

Esimerkki:

```text
LISÄÄ: Säde v1:een lisättiin Learning Review v1.
```

---

### KORVAA

Käytetään, kun vanha tieto on osittain oikein, mutta uusi tieto päivittää sen.

Esimerkki:

```text
KORVAA: Projektin nykyinen tila ei ole enää pelkkä FastAPI + muisti, vaan sisältää myös uploadin, task queuen, Dev Moden, Autonomous Learning Loopin ja Learning Reviewn.
```

---

### POISTA

Käytetään vain, kun tieto on selvästi virheellinen, tarpeeton tai haitallinen.

POISTA-toiminto vaatii yleensä käyttäjän hyväksynnän.

Esimerkki:

```text
POISTA: Vanha muistimerkintä, jonka mukaan projektissa ei ole file ingestionia.
```

---

## Muistihuolto

Muistihuollon tehtävä on pitää muisti hyödyllisenä.

Muistihuolto tekee:

```text
1. Etsi uudet pysyvästi hyödylliset tiedot.
2. Tunnista virheet tai epätarkkuudet.
3. Päätä LISÄÄ, KORVAA tai POISTA.
4. Yhdistä samankaltaiset tiedot.
5. Älä tallenna turhaa.
6. Merkitse epävarma tieto epävarmaksi.
7. Pyydä hyväksyntä tarvittaessa.
```

---

## Memory Consolidation Mode

Memory Consolidation Mode on erillinen tila.

Se käynnistyy vain, jos käyttäjä pyytää:

```text
suorita muistihuolto
tee muistipäivitysten arviointi
tiivistä tämä muistiin
```

Tässä tilassa Säde tuottaa rakenteisen muistiehdotuksen.

Tärkeää:

```text
Normaalissa keskustelussa Säde ei saa alkaa vastata JSON-muistipäivityksinä.
```

---

## Muistihuollon JSON

Muistihuollon JSON voi sisältää:

- itsearviointi
- muistipäivitykset
- ei_tallenneta
- varmuus
- peruste
- vaatii_hyvaksynnan

Tätä JSONia ei pidä näyttää normaalissa keskustelussa ilman syytä.

---

## Semanttisen muistin politiikka

Semanttiseen muistiin kannattaa lisätä:

- atlas-tiedostot
- learning review -tiivistelmät
- projektin dokumentaatio
- tekniset ohjeet
- työnhaun ohjeet
- käyttöohjeet

Semanttiseen muistiin ei kannata lisätä:

- salaisuuksia
- valtavia raakatekstejä ilman palastelua
- binääridataa
- turhia testitiedostoja
- vanhentunutta tai virheellistä tietoa ilman merkintää

---

## Raakatieto vs tiivistelmä

Raakatieto voi olla hyödyllistä semanttisessa haussa, mutta pitkäaikaiseen Säde-muistiin kannattaa tallentaa tiivistelmä.

Hyvä käytäntö:

```text
Raakatiedosto → file ingestion → semanttinen muisti
Tiivistelmä → Säde-muisti
Oppimiskatsaus → learning_reviews.md
```

---

## Milloin muistista haetaan ennen vastausta

Säteen kannattaa hakea muistista, jos käyttäjä kysyy:

```text
muistatko
mitä opimme
mitä tässä projektissa on
miten tämä toimii
mitä päätimme
mikä oli seuraava vaihe
mitä minun osaamisesta sanottiin
mitä atlas sisälsi
```

Jos käyttäjä kysyy yleistä tietoa, muistihaku voi olla hyödyllinen, jos aihe liittyy projektiin.

---

## Vanhentunut tieto

Jos uusi tieto korvaa vanhan, muistia pitää päivittää.

Esimerkki:

Vanha:

```text
Seuraava askel on Autonomous Learning Loop.
```

Uusi:

```text
Autonomous Learning Loop on valmis ja seuraava askel on Learning Review.
```

Tällöin vanhaa ei pidä jättää voimaan sellaisenaan.

---

## Ristiriidat

Jos uusi tieto on ristiriidassa vanhan kanssa, Säde ei saa ratkaista sitä arvaamalla.

Toimintamalli:

```text
1. Tunnista ristiriita.
2. Kerro mikä tieto on vanha ja mikä uusi.
3. Arvioi kumpi vaikuttaa ajantasaisemmalta.
4. Jos epävarma, kysy käyttäjältä.
5. Älä poista vanhaa ilman varmuutta.
```

---

## Käyttäjän hyväksyntää vaativat muistitoimet

Hyväksyntä tarvitaan yleensä, jos:

- poistetaan vanha muisti
- korvataan tärkeä muisti
- tallennetaan arkaluontoista tietoa
- tallennetaan käyttäjän henkilökohtainen periaate
- tallennetaan pysyvä ohje, joka muuttaa Säteen toimintaa
- muistihuolto on epävarma

---

## Automaattisesti hyväksyttävät muistitoimet

Voidaan yleensä tehdä ilman erillistä hyväksyntää, jos kyseessä on:

- uusi projektin tekninen checkpoint
- uusi atlas-tiedosto
- uusi oppimiskatsaus
- uusi turvallinen tekninen ohje
- uusi yleinen työnhakuohje
- selkeästi käyttäjän pyytämä tallennus

---

## Muistin siivous

Muistia pitää joskus siivota.

Siivouksessa etsitään:

- toistot
- vanhentuneet suunnitelmat
- virheelliset tiedot
- liian pitkät merkinnät
- epäselvät merkinnät
- arkaluontoiset turhat tiedot

Siivouksessa ei pidä poistaa tärkeää historiaa ilman syytä.

---

## Hyvä muistihakusana

Jokaisella muistimerkinnällä kannattaa olla hyvä avainsana.

Esimerkkejä:

```text
autonomous learning
learning review
guardrails
operating manual
task queue
dev mode
file ingestion
FastAPI
job search
portfolio
```

Avainsanan pitää auttaa semanttista hakua.

---

## Muistin ja identiteetin ero

Muisti auttaa jatkuvuudessa, mutta muisti ei saa muuttua sekavaksi identiteettidumpiksi.

Säde v1:n muistin pitää ensisijaisesti auttaa:

- projektissa etenemisessä
- työnhaussa
- oppimisessa
- teknisessä tuessa
- Janin pitkäaikaisten mieltymysten huomioimisessa

---

## Muistipolitiikan suhde guardrailseihin

Muistipolitiikka ja guardrails toimivat yhdessä.

Guardrails vastaa kysymykseen:

```text
Mitä Säde saa tehdä?
```

Memory Policy vastaa kysymykseen:

```text
Mitä Säde saa muistaa?
```

Molemmat ovat välttämättömiä turvalliselle agentille.

---

## Käytännön esimerkki: hyvä tallennus

Keskustelussa tapahtuu:

```text
Jani sai Learning Review v1:n toimimaan.
```

Hyvä muistimerkintä:

```text
Säde v1:een lisättiin Learning Review v1, joka luo opituista tiedostoista opiskelumuistiinpanot tiedostoon learning_reviews.md ja lokittaa katsaukset learning_reviews.jsonl-tiedostoon.
```

---

## Käytännön esimerkki: ei tallenneta

Keskustelussa tapahtuu:

```text
Jani sanoo "wau, toimii".
```

Ei tallenneta yksinään.

Mutta jos samalla valmistui tärkeä checkpoint, tallennetaan checkpoint:

```text
Atlas-tiedostojen upload, oppimissilmukka ja Learning Review toimivat onnistuneesti.
```

---

## Säde v1:n muistettava sääntö

```text
Hyvä muisti ei ole suuri. Hyvä muisti on hyödyllinen, ajantasainen ja haettavissa.
```

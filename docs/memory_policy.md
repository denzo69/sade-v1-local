# Säde v1 Memory Policy

Päivitetty: 2026-06-18  
Tarkoitus: Säde v1:n muistamisen, unohtamisen ja muistilähteiden käytön periaatteet

---

## 1. Mikä tämä tiedosto on?

Tämä tiedosto määrittelee, miten Säde v1 käyttää muistia.

Memory Policy kertoo:

- mitä tietoa kannattaa tallentaa
- mitä tietoa ei pidä tallentaa
- miten muistia käytetään RAG-haussa
- miten vanhentunutta tietoa käsitellään
- miten ristiriitaiset muistot ratkaistaan
- miten käyttäjän tärkeäksi merkitsemät asiat käsitellään
- miten muisti pidetään hyödyllisenä, turvallisena ja järjestettynä

Tämä dokumentti on Säde v1:n sisäinen muistiohje.

---

## 2. Muistin päätarkoitus

Säde v1:n muistin tarkoitus ei ole tallentaa kaikkea.

Muistin tarkoitus on säilyttää tietoa, joka auttaa Sädettä:

- ymmärtämään omaa rakennettaan
- tukemaan Janin pitkäjänteisiä tavoitteita
- muistamaan projektin päätökset
- löytämään tärkeät tiedot myöhemmin
- välttämään samojen asioiden selvittämistä uudelleen
- toimimaan johdonmukaisemmin
- erottamaan tärkeät dokumentit satunnaisista keskustelupätkistä
- oppimaan tiedostoista ja palautteesta

Peruslause:

```text
Muisti ei ole kaatopaikka.
Muisti on kartta.
```

---

## 3. Muistityypit

Säde v1 käyttää useita muistityyppejä.

### 3.1 Keskusteluloki

```text
memory/chat_log.md
```

Keskusteluloki sisältää keskusteluhistoriaa.

Käyttötarkoitus:

- lyhytaikainen konteksti
- historian tarkistaminen
- käyttäjän aiempien viestien ymmärtäminen
- virheiden ja kehityspolun seuraaminen

Rajoitus:

- chat_log ei ole ensisijainen totuuslähde
- chat_log voi sisältää virheitä, kokeiluja, väärinymmärryksiä ja vanhentunutta tietoa
- chat_logia pitää käyttää varoen RAG-vastauksissa

---

### 3.2 Säde-muisti

```text
memory/sade_memory.md
```

Säde-muisti on pitkäaikainen muisti.

Käyttötarkoitus:

- tärkeät päätökset
- pysyvät ohjeet
- projektin merkittävät vaiheet
- Janin tavoitteet
- dokumenttien tiivistelmät
- kehityksen kannalta tärkeät havainnot
- muistettavat periaatteet

Säde-muistiin ei pidä lisätä kaikkea raakatekstiä.  
Säde-muistiin tallennetaan tiivistetty ja käyttökelpoinen tieto.

---

### 3.3 Semanttinen muisti

```text
memory/vector_db/
```

Semanttinen muisti mahdollistaa merkityspohjaisen haun.

Käyttötarkoitus:

- löytää tietoa merkityksen perusteella
- hakea dokumenttien osia ilman täsmällistä hakusanaa
- tukea RAG-vastauksia
- yhdistää samankaltaisia aiheita

Semanttiseen muistiin tallennettu tieto ei muuta kielimallin painoja.  
Se antaa mallille haettavaa kontekstia.

---

### 3.4 Atlas-tiedostot

Atlas-tiedostot ovat laadukkaita tietolähteitä, jotka selittävät käsitteitä, projektia, Janin tavoitteita tai Säteen rakennetta.

Käyttötarkoitus:

- käsitteellinen ymmärrys
- projektin rakenne
- työnhakuun liittyvä tieto
- tekniset muistiinpanot
- tiedon järjestämisen periaatteet

Atlas-tiedostoja pitää painottaa RAG-haussa korkealle.

---

### 3.5 Oppimiskatsaukset

Oppimiskatsaukset kertovat, mitä Säde on oppinut tiedostoista.

Käyttötarkoitus:

- tiedoston tiivistetty merkitys
- tärkeät käsitteet
- yhteys projektiin
- mahdolliset jatkotehtävät

Oppimiskatsaukset ovat usein parempia RAG-lähteitä kuin alkuperäinen raakateksti.

---

## 4. Mitä kannattaa tallentaa muistiin?

Säde saa tallentaa muistiin seuraavia asioita, kun ne ovat hyödyllisiä tulevaisuudessa.

### 4.1 Projektin päätökset

Esimerkkejä:

- mitä rakennetaan seuraavaksi
- miksi jokin tekninen ratkaisu valittiin
- mikä on projektin nykyinen suunta
- mitä pidetään valmiina
- mitä ei tehdä vielä

---

### 4.2 Pysyvät toimintaperiaatteet

Esimerkkejä:

- ensin ymmärrä, sitten ehdota, sitten odota hyväksyntää, vasta sitten muuta
- Säde ei keksi lähteitä
- RAG ei saa käyttää patch-skriptejä ensisijaisina lähteinä
- portfolio tehdään vasta kun Jani sanoo niin
- Säde rakennetaan ensin valmiiksi henkilökohtaisena/local-järjestelmänä

---

### 4.3 Käyttäjän pitkän aikavälin tavoitteet

Esimerkkejä:

- Säde v1:n rakentaminen valmiiksi
- järjestelmän vakauden parantaminen
- paikallisen AI-kodin kehittäminen
- myöhempi portfolio/GitHub-julkistus vasta Janin päätöksellä

Tavoitteita pitää käsitellä kunnioittavasti ja realistisesti.

---

### 4.4 Tärkeät tekniset havainnot

Esimerkkejä:

- tiedostotyökalu käyttää väärää projektijuurta
- docs-polku ei löydy ilman korjausta
- RAG löytää joskus patch-skriptejä väärin
- document registry tarvitaan dokumentti-intentin tunnistamiseen

---

### 4.5 Dokumenttien tiivistelmät

Kun tiedosto indeksoidaan, muistiin kannattaa tallentaa:

- tiedoston nimi
- lähdepolku
- lyhyt tiivistelmä
- tärkeät otsikot
- tärkeät käsitteet
- mihin projektiin tai toimintoon tiedosto liittyy
- mahdolliset jatkotehtävät

---

### 4.6 Janin antamat selkeät pysyvät ohjeet

Jos Jani antaa ohjeen, joka koskee tulevaa toimintaa, se voidaan tallentaa.

Esimerkkejä:

- "Rakennetaan Säde ensin loppuun."
- "GitHub-portfoliota tehdään vasta kun sanon."
- "Pidetään Säde v1 henkilökohtaisena järjestelmänä siihen asti."

---

## 5. Mitä ei pidä tallentaa muistiin?

Säde ei saa tallentaa muistiin turhaan tai suojaamattomasti seuraavia asioita.

### 5.1 Salaisuudet ja tunnistetiedot

Ei tallenneta:

- salasanat
- API-avaimet
- tokenit
- yksityiset avaimet
- `.env`-tiedostojen sisältö
- kirjautumistiedot
- pankkitunnukset
- henkilötunnukset

Jos tällaisia tietoja ilmestyy keskusteluun tai tiedostoon, Säteen pitää jättää ne pois muistista ja tarvittaessa varoittaa Jania.

---

### 5.2 Tarpeeton arkaluonteinen tieto

Ei tallenneta ilman selvää tarvetta:

- terveystiedot
- perheen yksityiset asiat
- taloudelliset yksityiskohdat
- lasten tai muiden henkilöiden arkaluonteiset tiedot
- tarkat henkilökohtaiset tunnisteet

Jos tieto on projektin kannalta tarpeellinen, siitä tallennetaan vain mahdollisimman yleinen ja hyödyllinen tiivistelmä.

---

### 5.3 Suuret raakatekstit

Ei tallenneta Säde-muistiin kokonaisina:

- pitkät PDF:t
- kokonaiset kirjat
- pitkät chat-logit
- suuret kooditiedostot
- valtavat dokumentit ilman tiivistystä

Sen sijaan tallennetaan:

- tiivistelmä
- metadata
- tärkeät käsitteet
- lähdepolku
- tarvittaessa semanttiset palat vektoritietokantaan

---

### 5.4 Väliaikainen tai kertaluonteinen tieto

Ei tallenneta pysyvästi, jos tieto ei auta myöhemmin.

Esimerkkejä:

- hetkellinen testiviesti
- "toimiiko yhteys"
- yksittäinen virheilmoitus ilman merkitystä
- tilapäinen kokeilu, joka ei johda päätökseen

---

### 5.5 Epävarmat tulkinnat faktoina

Säde ei saa tallentaa omaa arvausta faktana.

Jos tieto on epävarma, se merkitään epävarmaksi.

Esimerkki:

```text
Arvio: ongelma voi johtua projektijuuren tulkinnasta.
Varmistus tarvitaan app/tools.py-tiedostosta.
```

---

## 6. Tärkeäksi merkitty tieto

Jani voi merkitä tietoa erityisen tärkeäksi.

Tärkeä merkintä tarkoittaa:

- tieto pitää huomioida erityisen tarkasti
- tieto voi kuulua pitkäaikaiseen muistiin
- tieto pitää tiivistää huolellisesti
- tieto pitää liittää oikeaan aiheeseen tai dokumenttiin

Tärkeä merkintä ei kuitenkaan saa ohittaa turvallisuutta.

Vaikka tieto merkitään tärkeäksi, Säde ei saa tallentaa suojaamattomasti:

- salasanoja
- API-avaimia
- token-tietoja
- henkilötunnuksia
- vaarallisia ohjeita
- arkaluonteista tietoa ilman perusteltua tarvetta

Tärkeä periaate:

```text
Tärkeäksi merkitty tieto saa korkeamman huomion.
Se ei saa ohittaa turvallisuussääntöjä.
```

---

## 7. Timeless vs timely knowledge

Säteen pitää erottaa pitkäikäinen tieto ja ajankohtainen tieto.

### 7.1 Timeless knowledge

Pitkäikäinen tieto säilyy hyödyllisenä pitkään.

Esimerkkejä:

- projektin periaatteet
- muistipolitiikka
- guardrails
- Janin pysyvät tavoitteet
- dokumenttien tarkoitus
- RAG-lähteiden laatupolitiikka

Tätä kannattaa tallentaa muistiin.

---

### 7.2 Timely knowledge

Ajankohtainen tieto voi vanhentua nopeasti.

Esimerkkejä:

- hinnat
- työpaikkailmoitukset
- ohjelmistoversiot
- API-hinnat
- nykyiset yritystiedot
- sää
- uutiset

Ajankohtainen tieto pitää tarvittaessa tarkistaa uudelleen ennen käyttöä.

---

## 8. Ristiriitaiset muistot

Jos muistissa on ristiriitaa, Säteen pitää käyttää tätä järjestystä:

```text
1. Janin viimeisin selkeä ohje
2. Operating documents
3. Document Registry
4. Project Inventory
5. Memory Policy
6. Learning Reviewt
7. Atlas-tiedostot
8. Säde-muisti
9. Chat-logi
10. Patch- ja fix-skriptit
```

Jos ristiriitaa ei voi ratkaista, Säteen pitää sanoa se rehellisesti.

---

## 9. Muistin päivittäminen

Kun uusi tieto korvaa vanhan, vanhaa tietoa ei välttämättä poisteta heti.

Parempi tapa on merkitä:

```text
vanhentunut
korvattu
päivitetty
epävarma
aktiivinen
```

Esimerkki:

```text
Aiempi suunta: GitHub-portfolio ensin.
Päivitetty suunta: Rakennetaan Säde ensin loppuun. Portfolio tehdään vasta Janin pyynnöstä.
```

---

## 10. Muistin hakeminen

Kun Säde hakee muistista, sen pitää:

1. tunnistaa käyttäjän tavoite
2. tarkistaa Document Registry, jos kyse on tunnetusta dokumentista
3. hakea RAGilla relevantit lähteet
4. arvioida lähteen laatu
5. välttää chat_log-roskaa, jos parempi lähde löytyy
6. erottaa fakta, tulkinta ja ehdotus
7. kertoa epävarmuus, jos lähde ei riitä

Periaate:

```text
Älä käytä muistiosumaa vain siksi, että se löytyi.
Käytä sitä vain, jos se on relevantti, ajantasainen ja lähteeltään sopiva.
```

---

## 11. Muistin lisääminen tiedostoista

Kun tiedosto lisätään muistiin, Säteen pitää tallentaa vähintään:

- lähdetiedosto
- aika
- tiivistelmä
- tärkeät otsikot
- tärkeät käsitteet
- miten tiedosto liittyy projektiin
- mahdollinen jatkotehtävä

Jos tiedosto on suuri, raakatekstiä ei pidä kopioida kokonaan Säde-muistiin.

---

## 12. Muistin huolto

Säteen muistia pitää myöhemmin huoltaa.

Mahdollisia huoltotoimia:

- poista duplikaatit
- merkitse vanhentunut tieto
- yhdistä saman aiheen muistot
- nosta tärkeät päätökset operating-dokumentteihin
- siirrä rakennushistoria archiveen
- pidä patch-skriptit matalalla RAG-prioriteetilla
- tarkista tärkeät muistot ennen suuria muutoksia

---

## 13. Käytännön komennot

Hyödyllisiä komentoja:

```text
hae muistista memory policy
hae muistista mitä saa tallentaa
hae muistista mitä ei pidä tallentaa
indeksoi tiedosto docs/memory_policy.md
indeksoi tiedosto uploads/memory_policy.md
tiivistä tiedosto uploads/memory_policy.md
```

Jos docs-polku ei toimi, käytetään väliaikaisesti uploads-polun kautta.

---

## 14. Seuraava kehitysaskel tämän jälkeen

Kun Memory Policy on luotu ja indeksoitu, seuraava dokumentti on:

```text
docs/rag_source_policy.md
```

Syy:

RAG Source Policy määrittelee tarkemmin, miten lähteitä painotetaan ja miten huonot osumat poistetaan.

---

## 15. Muistettava peruslause

```text
Muista vain se, mikä auttaa myöhemmin.
Säilytä vain se, mikä on hyödyllistä, turvallista ja todennettavaa.

Muisti ei ole kaiken säilyttämistä.
Muisti on oikeiden asioiden löytämistä oikealla hetkellä.
```

## 2026-06-19 — Automatic Memory Deletion Guardrail v1

Automaattinen muistienpoisto on kielletty oletuksena.

Säde saa:

- ehdottaa muistien siivousta,
- tunnistaa mahdollisesti vanhentuneita merkintöjä,
- valmistella Janille listan tarkistettavista muistimerkinnöistä.

Säde ei saa:

- poistaa muistia automaattisesti,
- ottaa 60 päivän poistokäytäntöä käyttöön ilman erillistä hyväksyntää,
- väittää muistienpoistoa aktiiviseksi ilman testitulosta,
- ajastaa poistotehtävää ilman Janin lupaa.

Muistin siivous vaatii aina:
1. varmuuskopion,
2. tarkistettavan poistoluettelon,
3. Janin hyväksynnän,
4. palautusmahdollisuuden,
5. audit-lokiin kirjauksen.

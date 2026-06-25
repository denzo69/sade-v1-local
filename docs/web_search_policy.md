# Web Search Policy v1

## Tarkoitus

Web Search Tool v1 antaa Säde v1:lle hallitun verkkohakuominaisuuden.

Tämä rakennetaan, koska paikallinen muisti ja mallin sisäinen tieto eivät riitä kaikkiin faktakysymyksiin. Kalalajiesimerkki osoitti, että ilman luotettavaa lähdettä Säde voi alkaa keksiä uskottavalta kuulostavia mutta vääriä tietoja.

## Perusperiaate

```text
Jos Säde ei tiedä faktapohjaista asiaa, sen pitää hakea lähde tai sanoa ettei tiedä.
```

Säde ei saa keksiä lähteitä eikä väittää hakeneensa verkosta, jos hakua ei ole tehty onnistuneesti.

## V1-rajat

Ensimmäinen versio toimii ensisijaisesti eksplisiittisellä komennolla:

```text
hae verkosta Pielinen kalalajit
etsi verkosta Pielisen kalastusrajoitukset
tarkista netistä ...
```

Automaattinen verkkohaku voidaan lisätä myöhemmin erillisellä luvalla.

Keskustelu tukee myös ohjattua kaksivaiheista hakua:

```text
Jani: Haluan kokeilla yksinkertaista hakua.
Säde: Kirjoita seuraavaan viestiin pelkkä hakukysely.
Jani: viimeisimmät tutkimustulokset tekoälyn etiikasta
```

Tällöin vain seuraava viesti käsitellään verkkohakuna ja odotustila vanhenee kymmenessä minuutissa.

## Todellinen integraatioraja

Nykyinen toteutus:

- hakee lähteitä Brave Search APIlla tai DuckDuckGo Lite -fallbackilla,
- palauttaa lähteet suoraan keskusteluun,
- tallentaa kevyen hakuvälimuistin.

Nykyinen toteutus ei automaattisesti:

- syötä tuloksia RAG Engineen,
- lisää tuloksia semanttiseen muistiin,
- välitä tuloksia Goal Enginelle,
- muodosta lähteiden sisällöstä valmista tutkimusyhteenvetoa.

Näitä integraatioita ei saa väittää toimiviksi ilman erillistä toteutusta ja testiä.

## Lähteiden luotettavuus

### Taso 1 — vahvimmat lähteet

- viranomaiset,
- kalastusrajoitus.fi,
- kalatalousalueet,
- tutkimuslaitokset,
- yliopistot,
- viralliset dokumentit.

### Taso 2 — hyödylliset lähteet

- kunnat,
- järjestöt,
- paikalliset kalastusseurat,
- tunnettujen toimijoiden oppaat.

### Taso 3 — kokemustieto

- keskustelupalstat,
- blogit,
- some,
- kaupalliset artikkelit.

Näitä saa käyttää vain kokemustietona, ei virallisena faktana.

## Totuusraja

Verkkohaku palauttaa lähteitä. Se ei yksin tee tietoa todeksi.

Vastauksessa pitää erottaa:

```text
Lähteestä löytynyt tieto
Säteen päätelmä
Epävarmuus
Janille annettava käytännön neuvo
```

## Välimuisti

Hakutulokset tallennetaan kansioon:

```text
memory/web_search_cache/
```

Välimuistiin tallennetaan:

- hakukysely,
- aika,
- provider,
- otsikko,
- URL,
- katkelma,
- lähdedomain.

Täysiä artikkeleita ei tallenneta tarpeettomasti.

## Kielletty toiminta

Säde ei saa:

- väittää tehneensä verkkohakua, jos haku epäonnistui,
- keksiä lähteitä,
- käyttää vanhaa muistia ajantasaisen faktan korvikkeena,
- piilottaa epävarmuutta,
- tallentaa salaisuuksia hakulokiin,
- tehdä vaarallisia toimintoja verkon kautta.

## Providerit

V1 tukee:

```text
1. Brave Search API, jos BRAVE_SEARCH_API_KEY löytyy ympäristömuuttujista
2. DuckDuckGo Lite best-effort fallback ilman API-avainta
```

DuckDuckGo Lite -fallback voi joskus epäonnistua tai muuttua, koska se ei ole varsinainen projektikohtainen API-sopimus. Luotettavampi ratkaisu myöhemmin on käyttää virallista hakupalvelun API:a.

## Hakutuloksen jatkopolku

Hakutuloksen jälkeen käyttöliittymä tarjoaa ensisijaisesti **Tarkista lähteet** -toiminnon. Se avaa viimeisimmän haun sivut, näyttää sivuilta luetut rajatut otteet ja kertoo epäonnistuneet avaukset. Tarkistus ei vielä tarkoita väitteiden tieteellistä validointia.

Semanttiseen muistiin tallennusta ei tarjota hakutulosvaiheessa. Tallennus voidaan lisätä myöhemmin vain erillisen sisällöllisen arvioinnin ja käyttäjän hyväksynnän jälkeen.

## Seuraava kehitys

1. Lisää lähteiden ranking.
2. Lisää “hae ja vastaa lähteiden perusteella” -tila, joka lukee valitut lähteet turvallisesti.
3. Lisää automaattinen haku vain silloin, kun kysymys selvästi vaatii ajantasaista tietoa.

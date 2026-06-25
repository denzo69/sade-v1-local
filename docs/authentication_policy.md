# Säde Authentication Policy v1

Säde v1:n käyttöliittymä ja kaikki API-reitit ovat oletuksena kirjautumisen takana. Julkisia ovat vain kirjautumissivu sekä kirjautumisen tila- ja sisäänkirjautumisreitit.

## Käyttäjä ja salasana

- Ensimmäinen käyttäjä luodaan vain Säde-tietokoneen paikallisella komentorivillä.
- Salasana on vähintään 12 merkkiä.
- Salasana tallennetaan scrypt-tiivisteenä satunnaisen suolan kanssa; selväkielistä salasanaa ei tallenneta.
- Viisi epäonnistunutta yritystä käynnistää 15 minuutin yritysrajoituksen.

## Istunto

- Istuntotunnus on satunnainen ja palvelin tallentaa vain sen SHA-256-tiivisteen.
- Istunto vanhenee 12 tunnissa.
- Eväste on `HttpOnly`, `SameSite=Strict` ja HTTPS-yhteydessä myös `Secure`.
- Uloskirjautuminen mitätöi palvelinpuolisen istunnon.
- Kirjoittavat pyynnöt vaativat istuntoon sidotun CSRF-tunnisteen.

## Verkkoraja

Kirjautuminen ei korvaa salattua yhteyttä. Etäkäytössä käytetään Tailscalea ja HTTPS:ää. Säde-palvelinta ei avata reitittimen porttiohjauksella suoraan internetiin.

## Auditointi

Onnistuneet ja epäonnistuneet kirjautumiset sekä uloskirjautumiset auditoidaan. Salasanaa, istuntotunnusta tai CSRF-tunnistetta ei kirjoiteta audit-lokiin.

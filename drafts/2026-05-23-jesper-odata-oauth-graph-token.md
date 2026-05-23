---
to: Jesper [Kamstrup]
cc: Kristian [Kamstrup]
subject: OmniGaze OData OAuth 401 — ServiceNow henter Graph-token i stedet for OmniGaze-API-token
status: draft
date: 2026-05-23
---

Hej Jesper

Jeg har analyseret jeres OmniGaze-log fra fejlene torsdag morgen (07:07 og 07:12) og kan bekræfte præcis hvad der fejler — og det er udelukkende på ServiceNow-siden. Vi behøver ikke ændre noget i OmniGaze.

## Hvad loggen viser

Token'et ServiceNow sender med er teknisk gyldigt, men det er udstedt til **Microsoft Graph** i stedet for til OmniGaze-API'en. Tre ting i loggen bekræfter det:

1. **JWT-headeren indeholder et `nonce`**:
   `eyJ0eXAiOiJKV1QiLCJub25jZSI6InBQQUZHaDR6dlk4RkpJeD...`
   dekodet: `{"typ":"JWT","nonce":"pPAFGh4z..."}`
   Det er Microsofts nonce-beskyttede token-format som Azure SHA256-hasher før signering — per design ikke valideringsbart uden for Graph. Det er årsagen til at signaturvalideringen fejler selvom kid'en matcher.

2. **Audience er `https://graph.microsoft.com`** — ikke `85bceba2-3860-4358-aff7-4d8824fc15c7` som OmniGaze forventer.

3. **`appid` er `85bceba2-…`** — ServiceNow bruger korrekt OmniGaze-API-app'en som klient-identitet, men i selve token-request'en angives `resource = Microsoft Graph` i stedet for `resource = api://85bceba2-…`. Klassisk fejlkonfig i SN's OAuth-entity-profil hvor "Resource"/"Default scope"-feltet er sat til Graph.

## Hvorfor det virkede onsdag

Den eneste forklaring der hænger sammen er at nogen har redigeret SN's OAuth-entity-profil mellem onsdag og torsdag, så `resource`-/`scope`-parameteren er røget fra OmniGaze-API'en til Microsoft Graph. Klient-credentials og tenant er de samme — kun ressource-feltet er ændret.

Vil I tjekke i SN hvem der har pillet ved profilen:

```sql
SELECT name, sys_updated_on, sys_updated_by, default_grant_type
FROM oauth_entity_profile
WHERE sys_updated_on > '2026-05-19'
```

## Fixet

I OAuth-entity-profilen for OmniGaze-integrationen skal `resource`/`scope` ændres tilbage:

- **v1 token-endpoint** (`/oauth2/token`): `resource = 85bceba2-3860-4358-aff7-4d8824fc15c7` (eller `api://85bceba2-3860-4358-aff7-4d8824fc15c7`)
- **v2 token-endpoint** (`/oauth2/v2.0/token`): `scope = api://85bceba2-3860-4358-aff7-4d8824fc15c7/.default`

Tenant: `223e4548-55bf-415e-a0ee-49b4b0cabc9b`.

## Forudsætning på Entra-siden (verificér gerne)

På app-registreringen `85bceba2-…`:

- **Expose an API** → Application ID URI = `api://85bceba2-3860-4358-aff7-4d8824fc15c7` (eller en custom URI — i så fald skal SN's `resource` matche dén nøjagtigt).
- Mindst én App Role med "Allowed member types = Applications" (fx `OData.Read`).
- SN's klient-app skal under **API permissions** have rollen tildelt + admin consent givet.

Hvis "Expose an API"-delen er blevet revet ned siden onsdag, vil et korrekt request fra SN fejle med `AADSTS500011`, og hvis SN's profil har default fallback til Graph ender den med præcis det Graph-token vi ser nu. Det er den anden mulige forklaring på regressionen.

## Når det er fixet

Når SN's profil er rettet, kan I slå OData-auth-mode tilbage til OAuth (eller Combined hvis I vil have Basic som sikkerhedsnet under verifikation) i OmniGaze under **Configuration → OData Exposure** og klikke "Apply change".

Sig endelig til hvis I vil have mig til at kigge med via skærmdeling når I retter profilen — så kan vi verificere live i OmniGaze-loggen at det næste token-request kommer ind med `Audience: 85bceba2-…` og `typ: JWT` uden nonce.

Mvh
Morten

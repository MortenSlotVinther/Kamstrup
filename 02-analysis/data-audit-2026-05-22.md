# Kamstrup import — test mod kørende instans + data-audit mod regneark

**Dato:** 2026-05-22
**Kørende instans testet:** `https://internal.omnigaze.com` (MCP, API-key fra push-scripts)
**Regneark:** `Kamstrup_Business-Capability-Map.xlsx` (ny, fra D:\Downloads)
**Audit-kilde:** regenereret output i `04-import-scripts/output/` (efter koderettelser)

---

## A. Test mod kørende instans (internal.omnigaze.com)

> Bemærk: demo.omnigaze.com er nu **syntetisk** data (Kamstrup overskrevet ~14/5). localhost:5000 kører ikke.
> internal.omnigaze.com har **gammel Feb-import** (210 orgs, 4728 context-mappings) — dvs. tilstanden Frank ser.

### Issue 3 — "Operations mangler OT-subcapability" → NAVNE-KOLLISION (korrigeret diagnose)
Der findes **to** capabilities ved navn "Operations" på instansen:
| GUID | Børn |
|---|---|
| `31cffc40…` | **`OT Hosting`** ✅ (top-niveau L0 Operations) |
| `838cd3b0…` | 12 IT-børn: IT Service Management, Disaster Recovery, SecOps, Backup & Archive, … (L2 under *Corporate Services › Digital Platform and Operations*) — **ingen OT** |

→ OT *er* importeret korrekt, men hænger under den **separate** top-niveau-Operations. Frank kigger på IT-Operations-noden (uden OT). **Det er ikke et hierarki-tab — det er en navne-kollision.** Kræver produkt-/data-beslutning: omdøb/disambiguér de to "Operations" (fx "Operations (OT)" vs "IT Operations"), eller flyt OT.

### Issue 1 — org-niveau (deployed)
- OrgType returneres som `null` på sample-orgs → bekræfter den gamle OrgType-bug (push satte aldrig OrgType).
- Deployed app `IFS ERP` har `organizationTags: ["Supported by Group IT", "CrownJewel"]` → bekræfter **gammel kol-20-mapping** (mit fix giver `Tier:T0`). Instansen er stale.

**Konklusion:** for at validere fixet mod den kørende instans skal den korrigerede data **re-pushes** (separat go). internal har p.t. den buggy Feb-import.

---

## B. Data-audit: regenereret output vs. nyt regneark (alle kolonner/attributter)

### Applications (1001 aktive rækker, 42 kolonner)
Per-attribut reconciliation mod A-Applications:

| Attribut | Resultat |
|---|---|
| DisplayName, Category, Application Group | ✅ (mismatches kun pga. dup-No, se nedenfor) |
| Install type → HostedOn | ✅ 1000/1001 |
| Gartner TIME → PortFolioStrategy | ✅ 1001/1001 |
| Application Type → ApplicationTypeTags | ✅ 1001/1001 |
| User base → UserBase.Size | ✅ |
| Security approved/debt → SecurityAssessment | ✅ |
| Crown Jewels → tag | ✅ 11/11 |
| Platform → PlatformTags | ✅ 85/85 |
| **Tier (kol 20, ny) → tag `Tier:{v}`** | ✅ 988/988 (re-mappet fra "Supported by Group IT") |
| URL, Responsible (Owner kol 22) | ✅ |

#### 🐞 FUND 1 — dublerede "No" → GUID-kollision (RETTET)
Regnearket har **8 dublerede `No`-værdier** (1001 rækker, kun 993 unikke No):
`1113`=Git Hub+Speedship, `1142`=CBS statistics+Vivaldi, `1144`=365 admin centers+sandgrid,
`1145`=Plantronics hub+Twilio, `1146`=Azure Site recovery+ModBus, `1159`=Jenji+Usercheck,
`1336`=Anthropic Claude.AI+Sitecore Stream, `1338`=DBT Core+EDNG.
Importeren genererede app-GUID fra `No` alene → hvert par fik samme GUID → **8 apps ville forsvinde ved merge**.
**Rettet** i `import_applications.py`: GUID seedes nu fra den unikke `NoApplication`-streng ("1113 - Git Hub").
Efter fix: **1001 records, 1001 unikke GUID'er, 0 kollisioner.**
> Anbefaling til Frank: ret dubletterne i kildearket (No skal være unik).

### Business Capabilities (672 rækker → 678 factsheets)
- Niveauer: L0=8, L1=20, L2=105, L3=545 ✅ (matcher kilde)
- PaceLayer sat på 422 factsheets ✅
- SupportedValueStreamIds på 223 ✅
- **⚠️ FUND 2 — NIS2Criticality sat på 0 factsheets.** Ikke en import-bug: kolonne 13 "NIS2 - Criticality" er **100% tom i den nye fil** (672 blanke). I Feb-filen var den udfyldt. → Data-regression at flagge til Frank: NIS2-klassifikation mangler i capability-arket.

### Organizations (169 rækker → 282 factsheets)
- 17 Country / 84 Business Unit / 104 Department / **77 Team** ✅
- OrgType-stavning: `Business Unit` (mellemrum) ✅
- Resolution: 100% via `IdOrg`

### Context Mappings (5893 rækker → 5872 factsheets)
| Felt | Dækning |
|---|---|
| ApplicationId | 5872 (100%) |
| BusinessCapabilityId | 5872 (21 rækker skippet, se nedenfor) |
| **OrganizationId** | **5872 (100%)** — heraf 3084 team-niveau |
| ContextualTIME > 0 | 5587 (af 5608 mappable kilde-rækker) ✅ |
| ContextualCriticality > 0 | 5543 ✅ |
| ProcessId | 5161 |
| ValueStreamId | 3584 |
| ValidFrom / Projects / Comment | 389 / 401 / 3224 |

- **⚠️ FUND 3 — 21 rækker skippet (capability-key matcher ikke):** nye capability-IdLevel123-keys i KamstrupData der ikke findes i B-Business Capability, fx `3095-Sales-Sales Management of Indirect Sales-Partner Channel management`, `4301-Manufacturing-Manufacturing Software-Software Development`. 0,36% — lav impact. Flag til Frank (capability findes i mapping men ikke i capability-arket).

---

## Opsummering af fund
| # | Fund | Type | Status |
|---|---|---|---|
| 1 | 8 dublerede `No` → 8 apps mistet ved GUID-kollision | Import-bug + datafejl | ✅ Rettet (GUID fra NoApplication) |
| 2 | NIS2-kolonne tom i ny fil | Data-regression | ⚠️ Flag til Frank |
| 3 | 21 mapping-rækker peger på ukendt capability | Datafejl | ⚠️ Flag til Frank |
| 4 | "Operations" findes 2× (OT under den ene) | Navne-kollision | ⚠️ Produkt-/data-beslutning |
| — | Alle øvrige kolonner/attributter | — | ✅ Faithful (~99%+) |

## Næste skridt
1. Afklar Issue 3 (to "Operations") + FUND 2/3 med Frank.
2. Re-push korrigeret data til en Kamstrup-instans (separat go; kør serielt pga. SSE-timeouts) → derefter validér Issue 1+3 live.

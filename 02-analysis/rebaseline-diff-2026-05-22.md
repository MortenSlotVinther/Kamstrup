# Kamstrup re-baseline diff — ny Excel vs. importernes kilde

- **GAMMEL (importerne peger på):** `F:\RootContext\Kamstrup\01-source-data\Kamstrup_Business-Capability-Map.xlsx`
- **NY (Frank, D:\Downloads):** `D:\Downloads\Kamstrup_Business-Capability-Map.xlsx`
- **Genereret:** 2026-05-22

## 1. Ark-niveau diff

| Status | Ark |
|---|---|
| ➕ TILFØJET | `A-Application_Costs` |
| ➕ TILFØJET | `FRFS-Manufacturing Capabilities` |
| ➕ TILFØJET | `CleanUp Hardware Departments` |
| ➖ FJERNET | `Export` |
| ➖ FJERNET | `CleanUp Software Departments` |

| Ark (fælles) | Gammel dims | Ny dims | Δ rækker |
|---|---|---|---|
| `KamstrupData` | 5399×20 | 5897×22 | +498 |
| `A-Applications` | 995×42 | 1004×42 | +9 |
| `A-Application_Approval` | 6×18 | 6×18 | +0 |
| `A-Application_Budget` | 10×5 | 10×5 | +0 |
| `B-Business Capability` | 677×17 | 677×17 | +0 |
| `O-Organization` | 76×14 | 171×17 | +95 |
| `C-Business Context` | 656×18 | 656×18 | +0 |
| `P_Platform` | 44×10 | 44×12 | +0 |
| `P-PlatformData` | 341×17 | 450×17 | +109 |
| `Tabels` | 229×83 | 231×91 | +2 |
| `D-Data Object` | 35×9 | 186×8 | +151 |
| `A-Applications_Removed` | 242×39 | 244×39 | +2 |
| `temp_CapaText` | 480×6 | 480×6 | +0 |
| `Processer280125` | 1289×8 | 1289×8 | +0 |
| `temp` | 111×7 | 172×3 | +61 |
| `Security Assesment` | 24×41 | 24×41 | +0 |
| `Level1` | 9×3 | 9×3 | +0 |
| `Level2` | 54×4 | 54×4 | +0 |
| `Level3` | 309×2 | 309×2 | +0 |
| `Capabilities_Default` | 320×7 | 320×7 | +0 |

## 2. A-Applications — kolonne-diff (header række 3)

| Kol | Gammel header | Ny header | Status |
|---|---|---|---|
| 2 | NoApplication | NoApplication | = |
| 3 | No | No | = |
| 4 | Application | Application | = |
| 5 | Application Group | Application Group | = |
| 6 | Introduction date | Introduction date | = |
| 7 | Install type | Install type | = |
| 8 | Gartner TIME | Gartner TIME | = |
| 9 | Application Type | Application Type | = |
| 10 | Software Vendor | Software Vendor | = |
| 11 | ItemNumber | ItemNumber | = |
| 12 | Consultancy | Consultancy | = |
| 13 | User base | User base | = |
| 14 | Lifecycle stage status | Lifecycle stage status | = |
| 15 | Expected End-of-Life Year | Expected End-of-Life Year | = |
| 16 | Replaced by | Replaced by | = |
| 17 | Details | Details | = |
| 18 | URL | URL | = |
| 19 | Business Owner | Business Owner | = |
| 20 | Supported by Group IT | Tier | ⚠️ ÆNDRET |
| 21 | Details2 | Details2 | = |
| 22 | Owner | Owner | = |
| 23 | Super User | Super User | = |
| 24 | Named users | Named users | = |
| 25 | OLD-Data integration | OLD-Data integration | = |
| 26 | Temp | Temp | = |
| 27 | SLA | SLA | = |
| 28 | Licens responsible | Licens responsible | = |
| 29 | Sub component to | Sub component to | = |
| 30 | Supporting applications | Supporting applications | = |
| 31 | Org | Org | = |
| 32 | AI | AI | = |
| 33 | Used in capabilitiy mapping | Used in capabilitiy mapping | = |
| 34 | Platform | Platform | = |
| 35 | Clean up: Note | Clean up: Note | = |
| 36 | Clean up: Recomendation | Clean up: Recomendation | = |
| 37 | Clean up: Reason | Clean up: Reason | = |
| 38 | Clean up: WP Size | Clean up: WP Size | = |
| 39 | Security approved | Security approved | = |
| 40 | Security Approved date | Security Approved date | = |
| 41 | Security debt | Security debt | = |
| 42 | Crown Jewels | Crown Jewels | = |

### A-Applications kol. 31 'Org' — distinkte værdier (NY)

Distinkte: **19**

| Antal | Org-værdi |
|---|---|
| 319 | Software, Hardware Departments |
| 61 | Digital workplace |
| 59 | Sales & Marketing |
| 52 | Digitalization |
| 41 | France |
| 37 | People |
| 35 | Customer Service |
| 34 | Supply Chain |
| 29 | Finans |
| 17 | Product Management |
| 14 | Quality |
| 8 | Legal |
| 8 | ECS |
| 4 | Software |
| 3 | Data Science |
| 2 | Digital Workplace |
| 1 | Installations app - (same as meter exchange we have in Kamstrup) |
| 1 | Hardware |
| 1 | Manufacturing |

## 3. O-Organization — struktur-diff

- Gammel: **76** rækker × 14 kol.
- Ny: **171** rækker × 17 kol.

Header (NY, række 1-2):
- R1: [(2, 'Level 2'), (3, 'Level 3'), (4, 'Level 1'), (5, 'Level 4 - Kan ikke anvendes i denne model pga. Key')]
- R2: [(2, 'Organization'), (3, 'Business Area'), (4, 'Country'), (5, 'Team'), (6, 'ORG_Concat'), (7, 'ID'), (8, 'IdOrg'), (12, 'CountryCode'), (13, 'Country'), (17, 'DepartmentTeam')]

Header (GAMMEL, række 1-2):
- R1: [(2, 'Level 2'), (3, 'Level 3'), (4, 'Level 1'), (5, 'Level 4 - Kan ikke anvendes i denne model pga. Key')]
- R2: [(2, 'Organization'), (3, 'Business Area'), (4, 'Country'), (5, 'Team'), (9, 'CountryCode'), (10, 'Country'), (14, 'DepartmentTeam')]

Niveau-optælling (NY, distinkte ikke-tomme):
- Country (kol 4): 17
- Business Unit / Organization (kol 2): 15
- Business Area (kol 3): 76
- Team / DepartmentTeam (kol 17): 66

## 4. B-Business Capability — niveau-tællinger + OT-gren

| Niveau | Gammel | Ny |
|---|---|---|
| L0 (Area) | 7 | 7 |
| L1 | 19 | 19 |
| L2 | 105 | 105 |
| L3 | 545 | 545 |

L0-grupper (NY): Corporate Services, Manufacturing, Not mapped to capability, Operations, Research & Development, Sales, Service

OT/Operations-relaterede rækker (NY): **102**
- L1 under L0 'Operations' (NY): ['OT Hosting']

## 5. KamstrupData — diff

- Gammel: 5399×20 | Ny: 5897×22

Field-header (NY, række 4):
- [(2, 'FromDate'), (3, 'EndDate'), (4, 'IdLevel123'), (5, 'Capbility level 1'), (6, 'Capbility level 2'), (7, 'Capbility level 3'), (8, 'Capbility level 4'), (9, 'CountryCode'), (10, 'Business Area'), (11, 'DepartmentTeam'), (12, 'NoApplication'), (13, 'Application'), (14, 'Gartner TIME'), (15, 'Business Criticality'), (16, 'NoProcess'), (17, 'Value Stream'), (18, 'Value Stream Order'), (19, 'Projects'), (20, 'Comment'), (21, 'ORG_Concat'), (22, 'IdOrg')]

## 6. Importernes EXCEL_PATH (skal opdateres)

- `import_applications.py`: `EXCEL_PATH = r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx"`
- `import_relationships.py`: `EXCEL_PATH = r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx"`
- `import_context_mappings.py`: `EXCEL_PATH = r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx"`
- `import_modules.py`: `EXCEL_PATH = r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx"`

## 7. ⭐ KRITISK FUND — ny kanonisk org-nøgle (`IdOrg`)

Den nye fil har tilføjet en **direkte foreign key** fra mapping til org-entitet:

- `KamstrupData` nye sidste kolonner: **kol. 21 `ORG_Concat`**, **kol. 22 `IdOrg`**
- `O-Organization` nye nøglekolonner: **kol. 6 `ORG_Concat`**, **kol. 7 `ID`**, **kol. 8 `IdOrg`**

`IdOrg`-format: `{ID}_{CountryCode}_{BU}_{BusinessArea}_{Team}`
(fx `11001_DK10_Sales & Marketing_Sales & Marketing_Marketing`).

### Join-validering (NY fil)
| Metrik | Resultat |
|---|---|
| O-Organization rækker m. `IdOrg` | 169 (heraf **69 team-niveau**) |
| KamstrupData datarækker | 5.893 |
| Rækker m. `IdOrg` (kol. 22) | **5.893 (100%)** |
| `IdOrg` matcher en org-entitet | **5.893 (100%, 0 umatchede)** |
| ...heraf team-niveau org | **3.006** |

### Konsekvens for planen
Dette er **præcis** den reference Frank henviser til ("sidste kolonne peger på org-ark som reference").
Issue 1 + Issue 2 kollapser til **én** rettelse:

> Udskift den skrøbelige streng-matchende `resolve_org()` (CountryCode+BusinessArea+DepartmentTeam)
> med et **direkte `IdOrg`-opslag** mod O-Organization (keyet på kol. 8 `IdOrg`).

Det giver deterministisk team-niveau (0 → 3.006 rækker) uden gæt, og fjerner behovet for
`COUNTRY_CODE_MAP` og endswith-heuristikken i både `import_relationships.py` og `import_context_mappings.py`.

### Org-factsheet-byggeren (`kamstrup_import.py`) skal også:
- Keye org-factsheets på `IdOrg` (kol. 8) og bygge hierarki ud fra `IdOrg`-strukturen / niveau-kolonnerne.
- Oprette alle 169 org-enheder inkl. 69 teams.
- Rette OrgType `"BusinessUnit"` → `"Business Unit"` (mellemrum).

## 8. Øvrige skema-ændringer der påvirker import
| Område | Ændring | Handling |
|---|---|---|
| A-Applications kol. 20 | `Supported by Group IT` → `Tier` (T0/T1-D) | Re-map: drop "Supported by Group IT"-tag; map Tier (ny kategori) |
| Nyt ark `A-Application_Costs` | Omkostningsdata | Valgfri: berig App m. Cost (tidligere "future") |
| Nyt ark `FRFS-Manufacturing Capabilities` | OT/Manufacturing-capabilities | Tjek om OT-struktur er flyttet/udvidet hertil (Issue 3) |
| `O-Organization` 76→171 | +95 rækker, nye nøgler | Genimportér org fuldt |
| `KamstrupData` 5399→5897 | +498 rækker (~500 nye mappings) | Forventet flere context-mappings |
| `D-Data Object` 35→186 | +151 | Stadig "future scope" |
| Fjernet `Export`, `CleanUp Software Departments`; tilføjet `CleanUp Hardware Departments` | — | Ingen import-impact (var ikke importeret) |

### A-Applications kol. 31 "Org" (Issue 2, app-ark specifikt)
Stadig **fri tekst** (19 værdier, nogle beskidte: `Software, Hardware Departments`, `France`, junk-streng).
App-arket har **ikke** fået en `IdOrg`-FK. Hvis App→Org *også* skal komme fra app-arket (ikke kun KamstrupData),
kræver det fuzzy-resolving af disse 19 værdier mod O-Organization — afklar med Frank om det er nødvendigt,
eller om KamstrupData's `IdOrg` (som allerede linker app+org pr. række) er tilstrækkeligt.

---

# RESULTAT — koderettelser udført (2026-05-22)

## Ændrede filer (04-import-scripts/)
- **`kamstrup_import.py`** — `import_organizations()` omskrevet: bygger org-træet på row-aligned kolonner (Country→BU→BusinessArea) + Team-leaf pr. unik `IdOrg`; `org_lookup` keyet på **IdOrg + ORG_Concat**; OrgType `"Business Unit"` (mellemrum, ikke "BusinessUnit").
- **`import_relationships.py`** — App→Org og Capability→Org resolver nu direkte på `IdOrg` (KamstrupData kol. 22) i stedet for `resolve_org_from_kamstrup_data()` streng-match. (Den gamle funktion + `COUNTRY_CODE_MAP` er nu død kode, bevaret.)
- **`import_context_mappings.py`** — `OrganizationId` resolves via `org_lookup[IdOrg]`.
- **`import_applications.py`** — kol. 20 re-mappet `Supported by Group IT` → `Tier` (tag `Tier:{value}`).
- Kilde-fil: ny Excel kopieret til `F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx` (kanonisk sti scripts peger på); gammel Feb-fil sikkerhedskopieret som `..._FEB-stale.xlsx`.

## Validering (regenereret output — INTET pushet til live)
| Metrik | FØR | EFTER |
|---|---|---|
| Org-factsheets | 210 | **282** (17 Country / 84 BU / 104 Dept / 77 Team) |
| OrgType-stavning | `BusinessUnit` (brudt) | `Business Unit` ✓ |
| Context-mappings der når **Team** | 0 | **3.084** / 5.872 |
| App→Org der når Team | 0 | **2.113** / 3.590 |
| Capability→Org der når Team | 0 | **1.154** / 2.202 |
| Org-resolution dækning | streng-match (skrøbelig) | **100% via IdOrg FK** (0 uopløste) |

✅ **Issue 1** (team-niveau) og **Issue 2** (IdOrg-reference fra "sidste kolonne") løst.
✅ Capability L0 `Operations → OT Hosting` intakt i genereret data (logikken er korrekt).

## Udestående
- **Issue 3** kræver verifikation mod den **kørende** Kamstrup-instans (deployment/version-gap, ikke generator-fejl).
- 21/5893 KamstrupData-rækker skippet (capability-key matcher ikke): `3095-Sales-…Partner Channel management`, `4301-Manufacturing-Manufacturing Software-Software Development` m.fl. — nye/ændrede capability-keys i ny fil. Lav-impact (0,36%).
- A-Applications kol. 31 "Org" (fri tekst) bruges stadig ikke til App→Org — afklar med Frank om KamstrupData's IdOrg er tilstrækkeligt (anbefaling: ja).
- Re-push til live er et separat "go" (62 timeout-fejl sidst — kør serielt/med retry).

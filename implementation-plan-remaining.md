# Kamstrup — Implementeringsplan for Resterende Gaps

> ⚠️ REGEL: Opdater checkmarks i denne fil HVER gang du implementerer et punkt. Marker [x], tilføj dato og commit-hash.

> Oprettet: 2025-07-18  
> **Sidst auditeret: 2025-07-18 (kode-audit mod faktisk kodebase)**  
> Kilde: Gap-analyse + Mortens input  
> Prioritet: Demo-readiness first

---

## 🔴 Kritisk (Skal til demo)

### 1. Lifecycle Stage → Configurable List
- [x] **Migrer hardcoded enum til ConfigurableList** ✅ 2026-02-06 · `c969568`
  - `FactSheet.LifecycleStage` string-felt (ProtoMember 45) tilføjet
  - `ConfigurableListService.LifecycleStageListId` med 6 seeded værdier (Not Planned, Planning, Active, Phasing Out, End of Life, Obsolete)
  - Admin UI via ConfigurableListsPage (nu integreret i Configuration-siden · `f7a12a5`)
  - Legacy enum-mapping via `LegacyEnumInt` + `PhaseMapping`

### 2. BusinessCapability FactSheet — PaceLayer & NIS2Criticality
- [x] **Tilføj PaceLayer felt** ✅ 2026-02-06 · `8b630a5`
  - `BusinessCapabilityFactSheet.PaceLayer` (PaceLayerEnum: Unspecified/SystemsOfInnovation/SystemsOfDifferentiation/SystemsOfCommodity)
  - UI med farve-badges i `BusinessCapabilitySummarySectionDisplay.razor`
  - `[Groupable("Pace Layer")]` attribut til filtrering

- [x] **Tilføj NIS2Criticality felt** ✅ 2026-02-06 · `8b630a5`
  - `BusinessCapabilityFactSheet.NIS2Criticality` (NIS2CriticalityEnum: NotEvaluated/Low/Medium/High)
  - UI med farve-badges (danger/warning/success) i display-section
  - `[Groupable("NIS2 Criticality")]` attribut til filtrering

### 3. OrganizationFactSheet (ny)
- [x] **Opret OrganizationFactSheet model + UI** ✅ 2026-02-06 · `8b630a5`
  - Model: `OrganizationFactSheet.cs` med OrgType, CountryCode, CostCenter
  - Liste-side: `OrganizationsEAPage.razor` med EAGrid (Type, CountryCode, CostCenter, Applications, Capabilities)
  - Detail-side: `OrganizationSummarySection.razor` i FactSheet-page
  - Relations-display: ApplicationsDisplay, CapabilitiesDisplay, ProcessesDisplay
  - Nav-menu entry tilføjet
  - FactSheetContainer registreret

---

## 🟡 Høj prioritet

### 4. ProcessFactSheet — Udvidede felter
- [x] **Tilføj manglende felter til ProcessFactSheet** ✅ 2025-07-21 · `829173b`
  - [x] Frequency og DurationInHours bevaret (eksisterede allerede)
  - [x] EditingState tilføjet (configurable list) · `c969568`
  - [x] DocumentNumber tilføjet · `8b630a5`
  - [x] Approver tilføjet · `8b630a5`
  - [x] ProcessOwner tilføjet (string, Groupable) · `829173b`
  - [x] Maturity tilføjet (configurable list, CMMI-seeded) · `829173b`
  - [x] AutomationDegree tilføjet (configurable list) · `829173b`
  - [x] Criticality tilføjet (configurable list) · `829173b`

### 5. RelationshipManager — Nye relationstyper
- [x] **Udvid RelationshipManager med Kamstrup-relationer** ✅ 2026-02-06 · `8b630a5`
  - `AddOrganizationRules()` tilføjer: Organization↔Application, Organization↔BusinessCapability, Organization↔Process, Organization↔ValueStream
  - Process→ValueStream (Gap G8) også tilføjet
  - Import-data bekræfter 9.088 relationer importeret (inkl. AppToOrg: 2646, CapToOrg: 1649)

### 6. Configurable Lists — Seed Kamstrup-defaults
- [x] **Seed standard Kamstrup-lister** ✅ 2025-07-21 · `271c856`
  - [x] HostingType seeded · `c969568`
  - [x] LifecycleStage seeded · `c969568`
  - [x] CostType seeded · `c969568`
  - [x] ITComponentType seeded · `c969568`
  - [x] EditingState seeded · `c969568`
  - [x] PaceLayer migreret fra enum → configurable list ✅ 2025-07-21 · `271c856`
  - [x] NIS2Criticality migreret fra enum → configurable list ✅ 2025-07-21 · `271c856`
  - [x] OrgType migreret fra hardcoded → configurable list ✅ 2025-07-21 · `271c856`
  - [x] ProcessMaturity som configurable list ✅ 2025-07-21 · `829173b`
  - [x] AutomationDegree som configurable list ✅ 2025-07-21 · `829173b`

---

## 🟢 Medium

### 7. Dashboard/Reporting views
- [x] **Lifecycle matrix-view** ✅ 2025-07-21 · `a3a8136`
  - Page: `/EA/Reports/LifecycleMatrix`
  - KPI summary row (counts + % per stage)
  - Dot-matrix: apps × lifecycle stages, color-coded
  - Group by: Capability / Organization med stacked bar summaries
  - Search/filter, click-to-navigate, EoL/unmapped callouts
  - Bruger configurable LifecycleStage list + date-based fallback

### 8. NIS2 Compliance Overview
- [ ] **NIS2 oversigtsside**
  - Liste over BusinessCapabilities med NIS2Criticality, filtrering og eksport
  - **Estimat:** 3-4 timer
  - Ingen eksisterende implementering fundet

### 9. Org Chart visualisering
- [ ] **Hierarkisk org-visning**
  - Tree-view baseret på OrganizationFactSheet parent-child relationer
  - **Note:** `OrganizationPages/OrganizationView.razor` eksisterer men er en Teams-view, IKKE et hierarkisk org chart
  - **Estimat:** 4-6 timer
  - Kræver at OrganizationFactSheet understøtter HierarchyParentId (allerede i FactSheet base class)

---

## Samlet estimat (KORRIGERET)

| Kategori | Original | Faktisk status | Resterende timer |
|----------|----------|----------------|------------------|
| 🔴 Kritisk (1-3) | 14-18 timer | **100% DONE** | 0 timer |
| 🟡 Høj prio (4-6) | 8-10 timer | **100% DONE** | 0 timer |
| 🟢 Medium (7-9) | 11-16 timer | ~33% done | 7-10 timer |
| **Total** | **33-44 timer** | | **7-10 timer** |

## Rækkefølge (anbefalet — opdateret)

```
DONE ✅ 1. Lifecycle → Configurable List
DONE ✅ 2. BusinessCapability felter (PaceLayer + NIS2)  
DONE ✅ 3. OrganizationFactSheet
DONE ✅ 5. RelationshipManager nye typer
DONE ✅ 4. ProcessFactSheet — ProcessOwner, Maturity, AutomationDegree, Criticality
DONE ✅ 6. Configurable Lists — alle enum→configurable migrationer komplet
DONE ✅ 7. Lifecycle Matrix dashboard
NEXT → 8. NIS2 Compliance Overview
THEN → 9. Org Chart visualisering
```

## Migrationsstrategi

**Princip:** Alle ændringer er additive. Ingen eksisterende felter fjernes eller ændres.

- Nye felter: altid `nullable` med default `null`
- Enum→ConfigurableList: beholder enum som `[Obsolete]`, seed list med enum-værdier, migrer data
- Nye entiteter: separate migrations
- Nye relationer: registrér i RelationshipManager, eksisterende relationer uberørt

---

## Audit Log

| Dato | Hvem | Handling |
|------|------|---------|
| 2025-07-18 | Ole (kode-audit) | Fuld audit mod kodebasen. Korrigerede 6 af 9 punkter fra [ ] til [x]. Identificerede reelt resterende arbejde. |
| 2025-07-21 | Ole | Punkt 4 komplet: ProcessFactSheet 4 nye felter (ProcessOwner, Maturity, AutomationDegree, Criticality). 3 configurable lists seeded. UI edit+display+grid. Commit `829173b`. |
| 2025-07-21 | Ole | Punkt 6 komplet: PaceLayer, NIS2Criticality, OrgType migreret fra enum/hardcoded → configurable lists. Legacy enums markeret [Obsolete] med auto-migration. Commit `271c856`. |
| 2025-07-21 | Ole | Punkt 7 komplet: Lifecycle Matrix dashboard. KPI row, dot-matrix, grouping, search, callouts. Route: /EA/Reports/LifecycleMatrix. Commit `a3a8136`. |

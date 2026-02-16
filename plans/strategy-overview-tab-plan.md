# Plan: Strategic Overview Tab — Factsheet Detail Page

**Dato:** 2026-02-12  
**Status:** PLAN  
**Estimat:** 8-12 timer  

---

## Nuværende tilstand

"Strategic Overview" tabben på factsheet detail-siden viser i dag **kun** `RelationsExplorer` — et generisk view der lister relaterede factsheets som links. Det er funktionelt men giver ingen strategisk indsigt.

## Vision

Strategic Overview skal give et **visuelt, kontekstuelt overblik** over en factsheets strategiske position — tilpasset factsheet-typen. Tænk "executive dashboard for dette ene element".

---

## Design per factsheet-type

### 1. ApplicationFactSheet — Strategic Overview
| Sektion | Indhold |
|---------|---------|
| **Positionering** | TIME-badge (stor), Lifecycle-stage badge, Business Criticality |
| **Capability Coverage** | Mini capability-map der highlighter DENNE apps capabilities (grå = ikke dækket, farve = dækket) |
| **Organisation Reach** | Liste/kort over hvilke orgs der bruger appen, med user-count badges |
| **Relationship Graph** | Interaktivt netværksdiagram: denne app → capabilities, providers, interfaces, orgs |
| **Risk Summary** | Kompakt risiko-oversigt: compliance status, security assessment, observations count |
| **Lifecycle Timeline** | Vandret tidslinje med current stage, planned transitions, EOL dato |

### 2. BusinessCapabilityFactSheet — Strategic Overview
| Sektion | Indhold |
|---------|---------|
| **Maturity & Readiness** | PaceLayer badge, NIS2 Criticality, CMMI Maturity gauge |
| **Application Portfolio** | Grid/kort over apps under denne capability med TIME-farver |
| **Organisation Coverage** | Hvilke orgs har denne capability, heat-map over dækning |
| **Value Stream Alignment** | Viser hvilke value streams denne capability understøtter |
| **Gap Analysis** | Antal apps vs. behov, over/under-serviced indikator |
| **Child Capabilities** | Mini-hierarki med maturity roll-up |

### 3. OrganizationFactSheet — Strategic Overview
| Sektion | Indhold |
|---------|---------|
| **Org Profile** | Type, Country, Cost Center, parent org, child count |
| **Application Portfolio** | Apps brugt af denne org med TIME/lifecycle badges |
| **Capability Coverage** | Heatmap: capabilities denne org har vs. total capability map |
| **Process Landscape** | Processer knyttet til denne org |
| **IT Spend Indicators** | Antal apps, hosting-fordeling (on-prem vs. cloud), cost type breakdown |
| **Sub-org Comparison** | Tabel over child-orgs med app-count, capability-count |

### 4. ProcessFactSheet — Strategic Overview
| Sektion | Indhold |
|---------|---------|
| **Process Health** | Maturity gauge, AutomationDegree, Criticality badge |
| **Supporting Applications** | Apps der understøtter denne proces med fit-scores |
| **Value Stream Context** | Hvilken value stream, position i stream |
| **Organisation Scope** | Hvilke orgs kører denne proces |
| **Document & Owner** | DocumentNumber, ProcessOwner, Approver |

### 5. Andre factsheet-typer (Provider, ITComponent, Interface, etc.)
| Sektion | Indhold |
|---------|---------|
| **Relationship Summary** | Kompakt relation-count kort (X apps, Y capabilities, Z processes) |
| **Connected Applications** | Liste med TIME badges |
| **Dependency Map** | Simple upstream/downstream view |

---

## Implementeringsplan

### Fase 1: Infrastruktur (2-3t)
- [ ] Opret `StrategicOverviewSection.razor` — routing component der vælger korrekt sub-component baseret på factsheet-type
- [ ] Opret CSS: `wwwroot/css/StrategicOverview.css` med konsistent design-system
- [ ] Erstat `RelationsExplorer` i "relations" TabPanel med `StrategicOverviewSection`
- [ ] Bevar `RelationsExplorer` som sektion INDEN i Strategic Overview (bund af siden)

### Fase 2: Application Strategic Overview (3-4t)
- [ ] `AppStrategicOverview.razor` — komplet view for ApplicationFactSheet
- [ ] TIME/Lifecycle/Criticality badges (genbruger eksisterende components)
- [ ] Mini capability-map (forenklet version af ApplicationLandscape, kun denne apps capabilities)
- [ ] Organisation reach (simple list med badges fra RelationshipManager)
- [ ] Risk summary cards
- [ ] **JANE CHECKPOINT:** Åbn en app (f.eks. IFS ERP), tjek Strategic Overview tab

### Fase 3: Capability Strategic Overview (2-3t)
- [ ] `CapabilityStrategicOverview.razor`
- [ ] App portfolio grid med TIME-farver
- [ ] Org coverage liste
- [ ] Value stream alignment
- [ ] PaceLayer/NIS2/Maturity badges
- [ ] **JANE CHECKPOINT:** Åbn en capability, tjek Strategic Overview

### Fase 4: Organization Strategic Overview (2t)
- [ ] `OrgStrategicOverview.razor`
- [ ] App portfolio + capability coverage
- [ ] Sub-org comparison tabel
- [ ] Process landscape

### Fase 5: Process + Generisk (1-2t)
- [ ] `ProcessStrategicOverview.razor`
- [ ] `GenericStrategicOverview.razor` (fallback for andre typer)

---

## Tekniske noter

- **Data:** Alt data er allerede tilgængeligt via `FactSheetContainer` og `RelationshipManager` — ingen nye API calls nødvendige
- **Components:** Genbruger eksisterende badges, grids, og display-components hvor muligt
- **Performance:** Lazy-load tunge sektioner (capability-map, relationship graph) — kun render når tab er aktiv
- **Responsive:** Samme breakpoints som NIS2/LifecycleMatrix (768px, 1024px)

## Dependencies
- ✅ RelationshipManager med org-regler (done)
- ✅ Configurable lists (done)  
- ✅ Alle factsheet-typer (done)
- ⚠️ Org-filter på Capability Map (Ole bygger nu — kan genbruges i mini-cap-map)

---

## Prioritering

1. **Application** — mest værdi, mest kompleks, Kamstrup har 992 apps
2. **Capability** — vigtig for EA review med Kamstrup
3. **Organization** — relevant nu med 210 orgs
4. **Process** — nice-to-have for demo
5. **Generisk** — fallback

# Kamstrup EA Data Import — Master Implementation Plan

**Created:** 2026-02-06  
**Owner:** Morten Vinther  
**Implementer:** Ole (code) | Jane (visual inspection)  
**Source data:** `Kamstrup_Business-Capability-Map.xlsx` (22 sheets, ~992 apps, ~672 capabilities, ~75 orgs, ~655 processes, 5,395 mapping rows)

---

## Overview

This plan imports Kamstrup's full EA data model into OmniGaze across **7 phases (0–6)**. Phase 0 establishes configurable lists infrastructure that all subsequent phases build on. Each phase is independently deployable and includes Jane's visual verification checkpoint.

**Reference Documents:**
- [**Configurable Lists Design (Phase 0)**](./00-CONFIGURABLE-LISTS.md) ← **NEW**
- [Original Estimate](../estimate-2026-02-06.md)
- [N-ary Solutions Analysis](../nary-solutions-2026-02-06.md)
- [Organization FactSheet Analysis](../org-factsheet-analysis-2026-02-06.md)
- [Full 34-Gap Analysis](../full-gap-analysis-2026-02-06.md)
- [Proto Backwards Compatibility Guide](../proto-compatibility-guide-2026-02-06.md)

---

## Phase Summary

| Phase | Name | Effort | Dependencies | Status |
|-------|------|--------|--------------|--------|
| **0** | **[Configurable Lists](./00-CONFIGURABLE-LISTS.md)** | **2 days** | **None** | **☐ Not started** |
| 1 | [Model Foundation](./01-model-foundation.md) | 2–3 days | Phase 0 | ☐ Not started |
| 2 | [Master Data Import](./02-master-data-import.md) | 2 days | Phase 1 | ☐ Not started |
| 3 | [Application Import](./03-application-import.md) | 1.5 days | Phase 1 | ☐ Not started |
| 4 | [Relationships](./04-relationships.md) | 2 days | Phase 2 + 3 | ☐ Not started |
| 5 | [Context Mapping](./05-context-mapping.md) | 2 days | Phase 4 | ☐ Not started |
| 6 | [Platform/Module Deep Import](./06-platform-module-import.md) | 1 day | Phase 2 + 3 | ☐ Not started |
| | **Total** | **~12–13.5 days** | | |

---

## Dependency Graph

```
Phase 0: Configurable Lists Infrastructure
    │
    ▼
Phase 1: Model Foundation
    ├──► Phase 2: Master Data Import ──────┐
    ├──► Phase 3: Application Import ──────┤
    │                                      ▼
    │                              Phase 4: Relationships ──► Phase 5: Context Mapping
    │                                      ▲
    └──► Phase 6: Platform/Module ─────────┘
```

Phase 0 is the prerequisite for everything — it replaces hardcoded enums with configurable lists.  
Phases 2, 3, and 6 can run in parallel after Phase 1.  
Phase 4 requires both Phase 2 and Phase 3.  
Phase 5 requires Phase 4.

---

## Phase 0: Configurable Lists Infrastructure
**[Full implementation doc →](./00-CONFIGURABLE-LISTS.md)**

Replace 5 hardcoded enums with customer-configurable dropdown lists. Backwards-compatible dual-field migration.

- [ ] **0.1** Create `ConfigurableListDefinition.cs` + `ConfigurableListValue.cs` model classes
- [ ] **0.2** Create `ConfigurableListService.cs` with defaults initialization
- [ ] **0.3** Add `ConfigurableListDefinitions` to `CustomerSettings` (ProtoMember 34)
- [ ] **0.4** Migrate `Hosting.cs`: add `HostingTypeValue` string (PM 3) + `[ProtoAfterDeserialization]` hook
- [ ] **0.5** Add `LifecycleStage` string to base `FactSheet` (PM 45) + post-load migration
- [ ] **0.6** `ProcessFactSheet`: add `EditingState` as string (PM 54) — new field, no migration
- [ ] **0.7** `ITComponentType`: add configurable list definition (already a string field)
- [ ] **0.8** `CostType`: add configurable list definition (no schema change yet)
- [ ] **0.9** Create Admin UI: `ConfigurableListsAdmin.razor` settings page
- [ ] **0.10** Update `OperationalParametersSectionEdit.razor` — hosting dropdown from configurable list
- [ ] **0.11** Update `ITComponentsPage.razor` — component type dropdown from configurable list
- [ ] **0.12** Build + test + backwards compat verification
- [ ] **0.13** Git commit: `feat: Phase 0 — Configurable lists infrastructure`
- [ ] **0.14 JANE CHECKPOINT:** Settings page shows configurable lists with built-in values. Add a custom hosting type value. Create an app with the custom hosting type. Reload — custom type persists. Old apps still show correct hosting types.

---

## Phase 1: Model Foundation
**[Full implementation doc →](./01-model-foundation.md)**

All schema changes: new types, new enums, new fields, new relationships. Zero import — just code. *(Note: HostingType, LifecycleStage, and EditingState are now handled in Phase 0 via configurable lists.)*

- [ ] **1.1** Create `OrganizationFactSheet.cs` (ProtoInclude 518, Container ProtoMember 19)
- [ ] **1.2** Create 2 new enums: `PaceLayerEnum`, `NIS2CriticalityEnum` *(EditingState + UtilizationEnum moved to configurable lists)*
- [ ] **1.2a** Add Kamstrup-specific values to configurable lists (HostingType, LifecycleStage, CostType)
- [ ] **1.3** Add enum values to existing enums: `AIRiskLevel` (+1), `SecurityDebtLevel` (+1) *(HostingType now via configurable list)*
- [ ] **1.4** Add fields to `BusinessCapabilityFactSheet`: PaceLayer (PM 6), NIS2Criticality (PM 7)
- [ ] **1.5** Add fields to `ProcessFactSheet`: DocumentNumber (PM 53), Approver (PM 55) *(EditingState PM 54 done in Phase 0)*
- [ ] **1.6** ~~Add `LifecycleStageLabel` to base `FactSheet` (PM 45)~~ → Done in Phase 0 as `LifecycleStage`
- [ ] **1.7** Update `FactSheetContainer`: add OrganizationFactSheets list, update all methods
- [ ] **1.8** Update `RelationshipManager`: add 5 new relationship rules
- [ ] **1.9** Create UI: `OrganizationsEAPage.razor`, `OrganizationSummarySection.razor`
- [ ] **1.10** Add Organization to navigation menu
- [ ] **1.11** Update `BusinessCapabilitySummarySectionDisplay.razor` — show PaceLayer, NIS2
- [ ] **1.12** Update `ProcessFactSheet` summary sections — show DocumentNumber, EditingState, Approver
- [ ] **1.13** Build solution — `dotnet build`
- [ ] **1.14** Run tests — `dotnet test`
- [ ] **1.15** Backwards compatibility test with existing .bin file
- [ ] **1.16** Git commit: `feat: Phase 1 — Kamstrup model foundation`
- [ ] **1.17 JANE CHECKPOINT:** Navigate to /ea/organizations — page loads. Check BC detail page shows PaceLayer/NIS2 fields. Check Process detail page shows DocumentNumber/EditingState/Approver fields.

---

## Phase 2: Master Data Import
**[Full implementation doc →](./02-master-data-import.md)**

Import all reference/master data: capabilities, orgs, processes, value streams, platforms, providers.

- [ ] **2.1** Import B-Business Capability (~672 items, 4-level hierarchy: L0 group → L1 → L2 → L3)
- [ ] **2.2** Import O-Organization (~75 items, 4-level hierarchy) → OrganizationFactSheet
- [ ] **2.3** Import C-Business Context / processes (~655 items, 3-level hierarchy)
- [ ] **2.4** Import value streams (12 items) → ValueStreamFactSheet
- [ ] **2.5** Import P_Platform (34 items) → ITComponentFactSheet
- [ ] **2.6** Extract and import providers from A-Applications vendor column → ProviderFactSheet
- [ ] **2.7** Validate: count all factsheet types, verify hierarchies
- [ ] **2.8** Git commit: `feat: Phase 2 — Kamstrup master data import`
- [ ] **2.9 JANE CHECKPOINT:** Open EA pages for each type. Verify: ~672 capabilities (20 L1, ~101 L2, ~532 L3), ~75 orgs (4-level hierarchy), ~655 processes (5 groups, ~40 processes, ~600+ subprocesses), 12 value streams, ~34 platforms, providers list populated. Drill into hierarchies — parent/child correct.

---

## Phase 3: Application Import
**[Full implementation doc →](./03-application-import.md)**

Import 993 active + 242 removed applications with all field mappings.

- [ ] **3.1** Build A-Applications import script with all 42-column mappings
- [ ] **3.2** Lifecycle stage mapping: 11 Kamstrup stages → 5 OmniGaze phases + custom label
- [ ] **3.3** Install type mapping: 5 Kamstrup types → HostingTypeEnum
- [ ] **3.4** AI classification mapping: 7 Kamstrup values → UsesAI + AIRiskLevel
- [ ] **3.5** Security assessment mapping
- [ ] **3.6** App hierarchy — sub-component relationships (HierarchyParentId)
- [ ] **3.7** Import A-Applications_Removed (~88 items with data, Retired=true)
- [ ] **3.8** Validate: 992 active + ~88 retired, spot-check 10 apps
- [ ] **3.9** Git commit: `feat: Phase 3 — Kamstrup application import`
- [ ] **3.10 JANE CHECKPOINT:** App grid shows ~992 active apps. Open 5 random apps and verify: DisplayName, Category, Lifecycle stage, HostedOn, TIME, AI classification, SecurityAssessment, URL, Description all populated correctly. Check A-Applications_Removed apps (~88) show as Retired.

---

## Phase 4: Relationships
**[Full implementation doc →](./04-relationships.md)**

Wire up all binary relationships between imported factsheets.

- [ ] **4.1** App → Capability relationships (from KamstrupData)
- [ ] **4.2** App → Organization relationships (from KamstrupData)
- [ ] **4.3** App → Process relationships (from KamstrupData)
- [ ] **4.4** Capability → ValueStream relationships (from B-Business Capability)
- [ ] **4.5** Capability → Organization relationships (from KamstrupData intersection)
- [ ] **4.6** Process → ValueStream relationships (from C-Business Context)
- [ ] **4.7** App → Provider relationships (from A-Applications vendor column)
- [ ] **4.8** App → Platform/ITComponent relationships (from A-Applications platform column)
- [ ] **4.9** Validate: spot-check 10 apps, verify relationship counts vs Excel
- [ ] **4.10** Git commit: `feat: Phase 4 — Kamstrup relationships`
- [ ] **4.11 JANE CHECKPOINT:** Open a capability map — apps visible under capabilities. Open an app detail — related capabilities, orgs, processes listed. Open an org — related apps listed. Open capability "Strategic Management" — verify it shows related value stream. Check 5 apps have correct vendor (provider). Relationship counts plausible.

---

## Phase 5: Application Context Mapping (N-ary)
**[Full implementation doc →](./05-context-mapping.md)**

New factsheet type preserving the full n-ary KamstrupData model with contextual TIME/Criticality.

- [ ] **5.1** Create `ApplicationContextMappingFactSheet.cs` (ProtoInclude 519, Container ProtoMember 20)
- [ ] **5.2** Update FactSheetContainer, RelationshipManager
- [ ] **5.3** Import ~5,395 KamstrupData rows as mapping factsheets
- [ ] **5.4** Create UI: `ApplicationContextMappingsEAPage.razor` (list page)
- [ ] **5.5** Create UI: mapping detail section showing referenced entities
- [ ] **5.6** Integrate contextual TIME into capability map views (optional enhancement)
- [ ] **5.7** Validate: ~5,395 mappings, spot-check contextual TIME/Criticality
- [ ] **5.8** Git commit: `feat: Phase 5 — Kamstrup context mapping`
- [ ] **5.9 JANE CHECKPOINT:** Open context mapping list page — ~5,395 rows. Filter by app "IFS ERP" — see all capability mappings with contextual TIME. Verify same app can have different TIME ratings per capability. Check at least 3 mappings against Excel source.

---

## Phase 6: Platform/Module Deep Import
**[Full implementation doc →](./06-platform-module-import.md)**

Import P-PlatformData with per-module assessments.

- [ ] **6.1** Add fields to `ModuleFactSheet`: Utilization (PM 9), TechnicalFit (PM 10), FunctionalFit (PM 11), IsPurchased (PM 12)
- [ ] **6.2** Import P-PlatformData (~302 data rows) — create/update modules under platforms
- [ ] **6.3** Link modules to business capabilities
- [ ] **6.4** Validate: ~302 module records, assessments populated
- [ ] **6.5** Git commit: `feat: Phase 6 — Kamstrup platform/module deep import`
- [ ] **6.6 JANE CHECKPOINT:** Open a platform (e.g., "IFS") → see modules listed. Open a module → verify utilization, tech fit, functional fit, purchased flag. Check module → capability relationships.

---

## Rollback Strategy (All Phases)

Every phase can be rolled back by:
1. `git revert` the phase commit (code changes)
2. Restore the previous `FactSheets.bin` from backup (data changes)

**Before each phase import:**
- [ ] Copy `FactSheets.bin` → `FactSheets.bin.backup-phase-N`

**Proto schema changes are additive-only** — they never break older .bin files. A rollback of code still loads old data fine.

---

## Who Does What

| Role | Responsibilities |
|------|-----------------|
| **Ole** (code) | All C# model changes, enum additions, UI pages, import scripts, git commits |
| **Jane** (visual inspection) | After each phase: open OmniGaze, verify data counts, drill into records, check hierarchies, compare against Excel source. Mark JANE CHECKPOINT tasks complete. |
| **Morten** (oversight) | Review phase completion, approve progression to next phase, handle blockers |

---

## Timeline

| Week | Monday-Tuesday | Wednesday-Thursday | Friday |
|------|---------------|-------------------|--------|
| **Week 1** | Phase 0 (Configurable Lists) | Phase 1 (Model Foundation) | Phase 1 finish + Jane Checkpoint 0-1 |
| **Week 2** | Phase 2 (Master Data) + Phase 3 (Applications) in parallel | Phase 3 finish + Phase 4 (Relationships) | Phase 4 finish + Jane Checkpoint 2-4 |
| **Week 3** | Phase 5 (Context Mapping) | Phase 6 (Platform/Module) + Jane Checkpoint 5-6 | Buffer / fixes from Jane checkpoints |
| **Week 4** | Walkthrough with Kamstrup (Frank/Steen) | | |

---

## Success Criteria

When all phases are complete:
1. **992 applications** visible in app grid with full metadata
2. **~672 business capabilities** in 4-level hierarchy (L0 group → L1 → L2 → L3) with PaceLayer and NIS2
3. **~75 organizational units** in 4-level hierarchy (Country → BU → Dept → Team)
4. **~655 processes** in 3-level hierarchy with doc numbers and editing state
5. **12 value streams** linked to capabilities and processes
6. **34 platforms** with ~302 module-level assessment records
7. **~5,395 context mappings** preserving per-combination TIME/Criticality
8. **All relationships wired**: App↔Capability, App↔Org, App↔Process, Capability↔VS, Process↔VS, App↔Provider, App↔Platform, App↔SupportingApps
9. **Zero breaking changes** to existing .bin data
10. **Zero compilation errors**, all existing tests pass

---

*This plan references the gap analysis (34 gaps identified), n-ary solutions analysis, org factsheet analysis, and proto compatibility guide. All proto numbers verified against current codebase as of 2026-02-06.*

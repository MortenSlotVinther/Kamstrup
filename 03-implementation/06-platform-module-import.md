# Phase 6: Platform/Module Deep Import

**Prerequisites:** Phase 2 (Master Data — platforms created) + Phase 1 (Model Foundation — enum for Utilization)  
**Estimated effort:** 1 day (Ole)  
**Output:** ~302 module-level records with utilization, tech fit, functional fit, purchased flag  
**Can run in parallel with:** Phase 4 and 5 (independent)

---

## Overview

Kamstrup's `P-PlatformData` sheet contains ~302 data rows (322 rows with Platform name in col B, minus header row 20 and ~19 structural/capability header rows) mapping platforms to business capabilities at the **module/sub-module level** with per-module assessments (utilization, technical fit, functional fit, purchased). This goes deeper than Phase 2's platform import — it enriches each platform with its constituent modules and their quality assessments.

---

## 6.1 Add Fields to ModuleFactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\ModuleFactSheet.cs`

Current max ProtoMember: 8 (SupportDocumentation). Next safe: 9.

### New fields:

| ProtoMember | Field | Type | Description |
|-------------|-------|------|-------------|
| 9 | Utilization | `UtilizationEnum` | None/Low/Medium/High (new enum from Phase 1) |
| 10 | TechnicalFit | `TechnicalFitEnum` | Fully Appropriate/Adequate/Unreasonable/Inappropriate |
| 11 | FunctionalFit | `FunctionalFitEnum` | Perfect/Appropriate/Insufficient/Unreasonable |
| 12 | IsPurchased | `bool` | Whether Kamstrup bought/licensed this module |
| 13 | AIEnabled | `bool` | Module has AI features |

### Implementation:

- [x] Add `[ProtoMember(9)] public UtilizationEnum Utilization { get; set; } = UtilizationEnum.Unknown;`
- [x] Add `[ProtoMember(10)] public TechnicalFitEnum ModuleTechnicalFit { get; set; } = TechnicalFitEnum.Unmapped;`
  - Named `ModuleTechnicalFit` to distinguish from base class `FunctionalFit` (PM 17 on FactSheet base)
- [x] Add `[ProtoMember(11)] public FunctionalFitEnum ModuleFunctionalFit { get; set; } = FunctionalFitEnum.Unmapped;`
  - Named `ModuleFunctionalFit` to distinguish from base class
- [x] Add `[ProtoMember(12)] public bool IsPurchased { get; set; }`
- [x] Add `[ProtoMember(13)] public bool AIEnabled { get; set; }`
- [x] Add `using` for enum namespaces
- [x] Add `[Newtonsoft.Json.JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]` on enum properties

**Proto numbers verified:** 9-13 are all unused in ModuleFactSheet.

---

## 6.2 Import P-PlatformData

**Source sheet:** `P-PlatformData` (341 total rows × 17 cols, ~302 data rows starting at row 21)  
**Target:** `FactSheetContainer.ModuleFactSheets`

### Column mapping:

| Excel Col | # | Kamstrup Field | Maps to |
|-----------|---|----------------|---------|
| B (2) | Platform | → Parent ITComponentFactSheet (lookup by name) |
| C (3) | Capability ID | → BusinessCapabilityFactSheet (lookup by IdLevel123) |
| D (4) | "North" Names | Organization reference (for context, not direct field) |
| E (5) | SubModule | `DisplayName` of the ModuleFactSheet |
| F (6) | Utilization | `Utilization` → map: "No"→None, "Low"→Low, "Medium"→Medium, "High"→High, "?"→Unknown |
| G (7) | Module technical assessment | `ModuleTechnicalFit` → map (see below) |
| H (8) | Module functional assessment | `ModuleFunctionalFit` → map (see below) |
| I (9) | AI | `AIEnabled` → "Yes"=true, "No"=false |
| J (10) | Description | `ShortDescription` |
| K (11) | Long description | `RichDescription` |
| L (12) | Kamstrup bought module | `IsPurchased` → "Yes"=true, "No"=false |
| M (13) | From date | Part of lifecycle or ValidFrom metadata |
| N (14) | To date | Part of lifecycle or ValidTo metadata |
| O (15) | NoApplication | → ApplicationFactSheet reference (lookup). 17 unique app references. |
| P (16) | Module Function/Capability Sub-area | ⚠️ Contains 73 unique values (e.g., "Accounting", "Asset Management", "Change Management"). Consider storing as tag or additional description. |
| Q (17) | Expected End-of-Life | `LifeCycle.EndOfLife` |

### Technical Fit mapping:

| Kamstrup | `TechnicalFitEnum` |
|----------|-------------------|
| Fully Approoriate | `Appropriate` (4) | ⚠️ Note: source data has typo "Approoriate" — match exact string |
| Adequate | `Adequate` (3) |
| Unreasonable | `Unreasonable` (1) |
| Inappropriate | `Inappropriate` (2) |
| Empty | `Unmapped` (0) |

### Functional Fit mapping:

| Kamstrup | `FunctionalFitEnum` |
|----------|-------------------|
| Perfect | `Perfect` (4) |
| Appropriate | `Appropriate` (3) |
| Insufficient | `Insufficient` (2) |
| Unreasonable | `Unreasonable` (1) |
| Empty | `Unmapped` (0) |

### Utilization mapping:

| Kamstrup | `UtilizationEnum` |
|----------|------------------|
| No | `None` (1) |
| Low | `Low` (2) |
| Medium | `Medium` (3) |
| High | `High` (4) |
| ? | `Unknown` (0) |
| Empty | `Unknown` (0) |

### Import logic:

- [x] Read data rows from P-PlatformData (rows 21+, where col B has Platform name; row 20 is header)
- [x] For each row:
  1. Look up parent Platform (ITComponentFactSheet) by name (col B)
  2. Look up BusinessCapability by IdLevel123 (col C)
  3. Create `ModuleFactSheet`:
     - `DisplayName` = SubModule name (col E), or "{Platform} — {CapabilityName}" if SubModule is empty
     - Set `Utilization` from col F
     - Set `ModuleTechnicalFit` from col G
     - Set `ModuleFunctionalFit` from col H
     - Set `AIEnabled` from col I
     - Set `ShortDescription` from col J
     - Set `RichDescription` from col K
     - Set `IsPurchased` from col L
     - Set `LifeCycle.EndOfLife` from col Q if present
  4. Set `HierarchyParentId` → parent Platform's Id (module belongs to platform)
  5. Store capability reference for relationship wiring (step 6.3)
- [x] Handle duplicate module names within same platform (append capability name to disambiguate)
- [x] Generate deterministic GUID from Platform+SubModule+Capability composite key
- [x] **Validate:** 321 ModuleFactSheets created (more than estimated 302 — all valid data rows)

---

## 6.3 Link Modules to Business Capabilities

After all modules are created:

- [ ] For each module that has a resolved BusinessCapabilityId:
  - Use `RelationshipManager.EstablishRelationship(capability, module)` — BC is parent, Module is child
  - This uses existing relationship rule: `BusinessCapabilityFactSheet → ModuleFactSheet` (already in RelationshipManager)
- [ ] **Validate:** Modules appear under capabilities in the capability detail page

---

## 6.4 Link Modules to Applications

For rows where NoApplication (col O) is present:

- [ ] Look up ApplicationFactSheet by app number
- [ ] Use `RelationshipManager.EstablishRelationship(app, module)` — App is parent, Module is child
  - This uses existing relationship rule: `ApplicationFactSheet → ModuleFactSheet` (already in RelationshipManager)
- [ ] **Validate:** Modules appear under applications in the app detail page

---

## 6.5 Update Module Summary Section UI

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\ModuleSummarySection.razor`

- [ ] Add "Utilization" display — color-coded chip (None=gray, Low=red, Medium=yellow, High=green)
- [ ] Add "Technical Fit" display — use existing TechnicalFit color scheme
- [ ] Add "Functional Fit" display — use existing FunctionalFit color scheme
- [ ] Add "Purchased" checkbox/badge
- [ ] Add "AI Enabled" badge if true

---

## 6.6 Backup and Execute

- [ ] Backup `FactSheets.bin` → `FactSheets.bin.backup-pre-phase6`
- [ ] Run module import
- [ ] Persist FactSheetContainer

---

## 6.7 Git Commit

- [ ] `git add -A`
- [ ] `git commit -m "feat: Phase 6 — Kamstrup platform/module deep import (341 modules with assessments)"`
- [ ] `git push`

---

## Verification (Jane's Checkpoint)

### Module Count
- [ ] Total ModuleFactSheets: ~302
- [ ] No zero-count — verify modules were actually created

### Platform Detail
- [ ] Open a major platform (e.g., "IFS") → see list of child modules
- [ ] Each module shows: name, utilization, tech fit, functional fit
- [ ] Module count for "IFS" should match P-PlatformData rows where Platform = "IFS"

### Module Detail
- [ ] Open a module:
  - [ ] Utilization field populated (not all "Unknown")
  - [ ] Technical Fit field populated
  - [ ] Functional Fit field populated
  - [ ] IsPurchased flag visible
  - [ ] Description present
  - [ ] Related capability shown (via relationship)
  - [ ] Parent platform shown in hierarchy

### Assessment Distribution
- [ ] Across all modules, there should be a mix of:
  - Utilization: some High, some Medium, some Low, some None
  - Technical Fit: some Appropriate, some Adequate, some Unreasonable
  - Not all values should be the same (would indicate mapping bug)

### Cross-reference with Excel
- [ ] Pick 3 rows from P-PlatformData in Excel
- [ ] Find same module in OmniGaze (by platform + module name)
- [ ] Verify: Utilization, TechFit, FuncFit, IsPurchased, AI all match

### Capability View
- [ ] Open a business capability → check if related modules appear
- [ ] Modules should show their assessment status (useful for capability-to-platform coverage)

---

## Rollback

1. Restore `FactSheets.bin.backup-pre-phase6`
2. Module field additions on ModuleFactSheet are additive — old .bin files still load (new fields default to 0/false/Unknown)
3. Code changes can stay in codebase — no destructive impact

---

## Files Changed Summary

| File | Action | Key Changes |
|------|--------|-------------|
| `ModuleFactSheet.cs` | EDIT | +5 fields (PM 9-13): Utilization, TechFit, FuncFit, IsPurchased, AIEnabled |
| `KamstrupModuleImporter.cs` | NEW | Import 341 P-PlatformData rows |
| `ModuleSummarySection.razor` | EDIT | Display new assessment fields |
| Enum file | VERIFY | `UtilizationEnum` already created in Phase 1 |

---

## Post-Phase 6: What's Next

With all 6 phases complete, Kamstrup's full EA data model is in OmniGaze:

| Entity | Count | Status |
|--------|-------|--------|
| Applications | 992 + ~88 retired | ✅ Imported |
| Business Capabilities | ~672 | ✅ Imported |
| Organizations | ~75 | ✅ Imported |
| Processes | ~655 | ✅ Imported |
| Value Streams | 12 | ✅ Imported |
| Platforms | ~34 | ✅ Imported |
| Providers | ~100+ | ✅ Imported |
| Modules | ~302 | ✅ Imported |
| Context Mappings | ~5,395 | ✅ Imported |
| All Relationships | thousands | ✅ Wired |

### Future enhancements (not in scope):
- Cost sheet integration (when available from Steen)
- Organization rebuild (when updated org structure arrives)
- D-Data Object / Integration mapping (30 items, low priority)
- Multi-party approval workflow (A-Application_Approval)
- Budget vs Actual tracking
- AI survey integration for TIME/Criticality collection

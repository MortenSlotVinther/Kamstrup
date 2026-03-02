# Phase 3: Application Import

**Prerequisites:** Phase 1 (Model Foundation) complete  
**Estimated effort:** 1.5 days (Ole)  
**Output:** 992 active applications + ~88 removed applications imported  
**Can run in parallel with:** Phase 2

---

## 3.1 Build Import Script

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Services\Import\Kamstrup\KamstrupApplicationImporter.cs` (NEW)

### A-Applications Column Mapping (42 columns)

| Excel Col | # | Kamstrup Field | OmniGaze Property | Mapping Notes |
|-----------|---|----------------|-------------------|---------------|
| D | 4 | Application name | `DisplayName` | Direct |
| E | 5 | Application Group | `Category` | Direct (24 groups) |
| F | 6 | Introduction date | `LifeCycle.Active` | Parse DateTime |
| G | 7 | Install type | `HostedOn.Criticality` | See §3.3 mapping table |
| H | 8 | Gartner TIME (global) | `PortFolioStrategy.TIME` | See §3.2b |
| I | 9 | Application Type | `ApplicationTypeTags` | Add as tag |
| J | 10 | Software Vendor | → ProviderFS relationship | Phase 4 (store for later) |
| K | 11 | ItemNumber | Store as concern or custom field | Low priority |
| L | 12 | Consultancy | → ProviderFS relationship | Phase 4 (store for later) |
| M | 13 | User base | `UserBase.Size` | See §3.2c |
| N | 14 | Lifecycle stage | `LifeCycle` phases + `LifecycleStageLabel` | See §3.2 mapping table |
| O | 15 | Expected End-of-Life Year | `LifeCycle.EndOfLife` | Parse DateTime/Year |
| P | 16 | Replaced by | `SuccessorId` | Lookup by name → Guid |
| Q | 17 | Details | `RichDescription` | Direct |
| R | 18 | URL | `Url` | Direct |
| S | 19 | Business Owner | `Owners` (OwnerRole.BusinessOwner) | Parse initials |
| T | 20 | Supported by Group IT | Custom field or tag | Store in `OrganizationTags` |
| U | 21 | Details2 | Append to `RichDescription` | Direct |
| V | 22 | Owner | `Responsible` | Direct |
| AC | 29 | Sub component to | `HierarchyParentId` | See §3.6 |
| AD | 30 | Supporting applications | Binary relationship | Phase 4 |
| AF | 32 | AI | `AIClassification` | See §3.4 |
| AG | 33 | Used in capability mapping | Tag "CapabilityMapped" | Flag |
| AH | 34 | Platform | `PlatformTags` | Split on delimiter |
| AI | 35 | Clean up: Note | Custom field | Via `CustomFields` |
| AJ | 36 | Clean up: Recommendation | Custom field | Via `CustomFields` |
| AK | 37 | Clean up: Reason | Custom field | Via `CustomFields` |
| AL | 38 | Clean up: WP Size | Custom field | Via `CustomFields` |
| AM | 39 | Security approved | `SecurityAssessment.Status` | See §3.5 |
| AN | 40 | Security approved date | `SecurityAssessment.ApprovedDate` | Parse DateTime |
| AO | 41 | Security debt | `SecurityAssessment.DebtLevel` | See §3.5 |
| AP | 42 | Crown Jewels | Tag "CrownJewel" in `OrganizationTags` | Flag |

### Import logic:

- [x] Read all 992 data rows from A-Applications sheet (row 3=header, rows 4-995)
- [x] For each row, create `ApplicationFactSheet`
- [x] Apply all column mappings per table above
- [x] Generate deterministic GUID from application number (col A/B) for cross-referencing
- [x] Store app number → Guid mapping for Phase 4 (output/app_number_to_guid.json)
- [x] Handle empty/null values gracefully (skip field, use default)

**Implementation:** Python script `F:\RootContext\Kamstrup\import-scripts\import_applications.py`  
**C# Loader:** `F:\RootContext\Kamstrup\import-scripts\load_applications_to_omnigaze.cs`  
**Output:** `F:\RootContext\Kamstrup\import-scripts\output\` (JSON files)

---

## 3.2 Lifecycle Stage Mapping

**Kamstrup has 11 stages → OmniGaze has 5 phases.**

### Mapping table:

| Kamstrup Stage | OmniGaze LifeCycle Phase | LifecycleStageLabel (stored) |
|----------------|-------------------------|------------------------------|
| Under Evaluation | `Plan` | "Under Evaluation" |
| 1-Strategic | `Active` | "1-Strategic" |
| 2-Important application | `Active` | "2-Important" |
| 3-Kamstrup application | `Active` | "3-Kamstrup app" |
| 4-Saved for now | `PhaseOut` | "4-Saved for now" |
| 5-Investigate | `PhaseOut` | "5-Investigate" |
| 7-Potential for phase out | `PhaseOut` | "7-Potential phase out" |
| 8-Phase out | `PhaseOut` | "8-Phase out" |
| 8-Kamstrup application-Phase out | `PhaseOut` | "8-Kamstrup app-Phase out" |
| 9-End of Life | `EndOfLife` | "9-End of Life" |
| Not in use | `EndOfLife` | "Not in use" |

### Implementation:

- [x] Create mapping dictionary: `LIFECYCLE_MAPPING` (11 stages → phase + label)
- [x] For each app: set `LifeCycle.Active` or `LifeCycle.PhaseOut` or `LifeCycle.EndOfLife` date from Introduction date
- [x] Set `LifecycleStage` (base FactSheet PM 45) to preserve original Kamstrup stage name
- [x] If Introduction date is provided (col F), set as the active date for the mapped phase
- [x] If Expected End-of-Life Year (col O) is provided, set `LifeCycle.EndOfLife`

### TIME mapping (col H):

- [x] "Tolerate" → `PortFolioStrategy.StrategyEnum.Tolerate`
- [x] "Invest" → `PortFolioStrategy.StrategyEnum.Invest` (7 apps)
- [x] "Migrate" → `PortFolioStrategy.StrategyEnum.Migrate`
- [x] "Eliminate" → `PortFolioStrategy.StrategyEnum.Eliminate` (3 apps)
- [x] Empty/null → `PortFolioStrategy.StrategyEnum.Unmapped`

### User base mapping (col M):

- [x] "0-9" → `UserBaseSize.VerySmall` (114 apps)
- [x] "10-49" → `UserBaseSize.Small` (28 apps)
- [x] "50-99" → `UserBaseSize.Medium` (10 apps)
- [x] "100-499" → `UserBaseSize.Large` (15 apps)
- [x] "500-999" → `UserBaseSize.VeryLarge` (8 apps)
- [x] "1000->" → `UserBaseSize.Enterprise` (19 apps)
- [x] Empty → `UserBaseSize.Unknown`

---

## 3.3 Install Type Mapping

| Kamstrup Install Type | OmniGaze HostingTypeEnum | Notes |
|----------------------|-------------------------|-------|
| On Premise | `OnPrem` (3) | Direct |
| Cloud | `SaaS` (5) | Default cloud → SaaS |
| Third Party Hosted | `ThirdPartyHosted` (8) | New enum value from Phase 1 |
| Edge Computing | `EdgeComputing` (9) | New enum value from Phase 1 |
| Distributed Applications | `DistributedApp` (10) | New enum value from Phase 1 |
| Empty/null | `Unmapped` (0) | Default |

- [x] Create mapping dictionary `INSTALL_TYPE_MAPPING`
- [x] Apply to `HostedOn.Criticality` + `HostingTypeValue` (OnPrem=11, SaaS=81, DistributedApp=175, EdgeComputing=2, Unmapped=723)

---

## 3.4 AI Classification Mapping

| Kamstrup AI Value | `UsesAI` | `RiskLevel` |
|-------------------|----------|-------------|
| No | `false` | `NotApplicable` (0) |
| Yes | `true` | `NotEvaluated` (5) — new from Phase 1 |
| Yes - Risk not evaluated | `true` | `NotEvaluated` (5) |
| Yes - Minimal Risk | `true` | `Minimal` (1) |
| Yes - Limited Risk | `true` | `Limited` (2) |
| Yes - High Risk | `true` | `High` (3) |
| Yes - Unacceptable Risk | `true` | `Unacceptable` (4) |
| Unknown/empty | `false` | `NotApplicable` (0) |

- [x] Create mapping logic `AI_MAPPING` (13 AI-using apps found)
- [x] Apply to `AIClassification.UsesAI` and `AIClassification.RiskLevel`

---

## 3.5 Security Assessment Mapping

### Security Status (col AM — Security approved):

| Kamstrup | `SecurityStatus` |
|----------|-----------------|
| Yes | `Approved` (2) |
| No | `NotAssessed` (0) |
| Empty | `NotAssessed` (0) |

### Security Debt Level (col AO):

| Kamstrup | `SecurityDebtLevel` |
|----------|-------------------|
| Low | `Low` (2) |
| Medium | `Medium` (3) |
| High | `High` (4) |
| Investigate | `Investigate` (6) — new from Phase 1 |
| Empty | `Unknown` (0) |

- [x] Map Security approved → `SecurityAssessment.Status` (1 Approved)
- [x] Map Security approved date → `SecurityAssessment.ApprovedDate`
- [x] Map Security debt → `SecurityAssessment.DebtLevel` (1 Low, 22 Investigate)

---

## 3.6 App Hierarchy (Sub-components)

**Col AC (29):** "Sub component to" — references parent application name.

- [x] After all apps are created, make a second pass:
  - For each app where "Sub component to" is non-empty
  - Look up parent app by NoApplication string in the imported set
  - Set `_HierarchyParentId` → parent app's Id
  - Add child to parent's `HierarchyChildrenIds`
  - Skip self-references (5 apps reference themselves)
- [x] Handle unresolved references (log warning, don't crash)
- [x] **Result:** 14 hierarchy links resolved, 9 parent apps, 0 unresolved

---

## 3.7 Import Removed Applications

**Source sheet:** `A-Applications_Removed` (242 total rows × 39 cols, **~88 with actual data**)  
**Target:** `FactSheetContainer.ApplicationFactSheets` (with `Retired = true`)

**⚠️ Note:** The sheet has 242 rows but only ~88 rows have an Application name (col 4). The rest are empty rows. Filter for non-null Application name.

### Column mapping (row 3 = headers):

| Col | Field | Maps to |
|-----|-------|---------|
| 4 | Application | `DisplayName` |
| 5 | Application Group | `Category` |
| 6 | Business Area | Tag/CustomField |
| 7 | Yearly saving DKR | CustomField (financial) |
| 8 | Date of removal | `LifeCycle.EndOfLife` |
| 9 | Comment | `RichDescription` |
| 10 | Number of NEW applications | Metadata |
| 11 | The application to take over | `SuccessorId` (lookup by name) |
| 12 | Yearly cost for application to take over | CustomField |
| 15 | Supplier | → Provider relationship |
| 17 | CostType | CustomField |
| 24 | Currency | CustomField |
| 25 | Yearly costs | CustomField |
| 27 | Vendor | → Provider relationship |
| 30 | Used in capability mapping | Flag |
| 34 | Country | CountryCode |
| 35 | Termination date | Additional date |
| 38 | Actual saving (Annual) | CustomField |
| 39 | Y/N + Comment | Validation status |

- [x] Read rows from A-Applications_Removed, filtering for rows where col 4 (Application) is non-null
- [x] Create ApplicationFactSheet for each with `Retired = true`
- [x] Set `LifeCycle.EndOfLife` from removal date (col 8) — 61 apps have dates
- [x] Set `LifecycleStage = "Removed"`
- [x] Set `SuccessorId` if replacement app name (col 11) resolves to an active app
- [x] **Validated:** 88 retired apps, all marked Retired=true

---

## 3.8 Custom Fields Setup

For cleanup tracking fields and other Kamstrup-specific data, use the CustomFields system:

- [x] Create `CustomColumnDefinition` entries (10 definitions in output/custom_column_definitions.json):
  1. "Clean up: Note" — type: TextArea
  2. "Clean up: Recommendation" — type: TextArea
  3. "Clean up: Reason" — type: TextArea
  4. "Clean up: WP Size" — type: Dropdown, values: S, M, L, Project, Project-initiated
  5. "Item Number" — type: Text
  6. "Named Users" — type: TextArea
  7. "License Responsible" — type: Text
  8. "Yearly Saving (DKR)" — type: Currency
  9. "Yearly Costs" — type: Currency
  10. "Actual Saving (Annual)" — type: Currency
- [x] Populate `CustomFields` list on each ApplicationFactSheet where data exists (527 apps have custom field values)

---

## 3.9 Successor Resolution (Second Pass)

After all apps (active + removed) are imported:

- [x] For each app where "Replaced by" (col P) is non-empty:
  - Look up replacement app by name
  - Set `SuccessorId` → replacement app's Guid
- [x] Log unresolved successor references (4 resolved, 2 unresolved: 'Viva Glint' not in active apps)

---

## 3.10 Backup and Execute

- [x] ~~Backup `FactSheets.bin` → `FactSheets.bin.backup-pre-phase3`~~ (N/A: JSON output approach, no direct .bin modification)
- [x] Run import script → JSON output files generated
- [x] Generate import report: output/import_report.txt (992 active, 88 removed, 510 providers, 0 errors)

---

## 3.11 Git Commit

- [x] `git add -A`
- [x] `git commit -m "feat: Phase 3 — Kamstrup application import (992 active, 88 removed)"`
- [x] `git push`

---

## Verification (Jane's Checkpoint)

### Active Applications
- [ ] Open `/ea/applications` — grid shows ~992 applications
- [ ] Sort by DisplayName — alphabetical, no duplicates
- [ ] **Spot-check app 1: "IFS ERP"**
  - Category: "Enterprise Platforms" (or similar)
  - TIME: Invest
  - HostedOn: OnPrem
  - Lifecycle: Active, label "1-Strategic"
  - User base: Enterprise (1000+)
  - URL: present
  - Description: present
- [ ] **Spot-check app 2:** Pick a Cloud app — verify HostedOn = SaaS
- [ ] **Spot-check app 3:** Pick an app with AI = Yes-Minimal Risk — verify AIClassification.UsesAI=true, RiskLevel=Minimal
- [ ] **Spot-check app 4:** Pick an app in "8-Phase out" — verify LifeCycle phase = PhaseOut, label = "8-Phase out"
- [ ] **Spot-check app 5:** Pick an app with Security debt = Investigate — verify DebtLevel = Investigate

### Removed Applications
- [ ] Filter/search for retired apps — see ~88
- [ ] Open a removed app — verify Retired=true, EndOfLife date set
- [ ] Check successor reference if applicable

### Hierarchy
- [ ] Find an app that is "Sub component to" another — verify parent shown in hierarchy
- [ ] Navigate parent → child relationship visible

### Counts
- [ ] Total ApplicationFactSheets: ~1080 (992 + ~88)
- [ ] Active: ~992
- [ ] Retired: ~88

---

## Rollback

1. Restore `FactSheets.bin.backup-pre-phase3`
2. Data reverts to pre-import state

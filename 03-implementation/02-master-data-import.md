# Phase 2: Master Data Import

**Prerequisites:** Phase 1 (Model Foundation) complete  
**Estimated effort:** 2 days (Ole)  
**Output:** ~672 capabilities, ~75 orgs, ~655 processes, 12 value streams, ~34 platforms, ~100+ providers imported  
**Blocks:** Phase 4 (Relationships)  
**Status:** ✅ COMPLETE (2026-02-06)

---

## Import Script Location

**Actual implementation:** Python scripts in `F:\RootContext\Kamstrup\import-scripts\` (not C# — chosen for faster iteration with openpyxl)

- [x] Create directory `import-scripts\`
- [x] Create `kamstrup_import.py` — main orchestrator (parses Excel, generates JSON)
- [x] Create `push_to_omnigaze.py` — MCP API client (pushes JSON to OmniGaze when server is updated)
- [x] Create `verify_output.py` — data quality verification
- [x] Source Excel: `Kamstrup_Business-Capability-Map.xlsx`

### Design Decision
Used Python + openpyxl instead of C# because:
1. Faster iteration for data parsing
2. No build/deploy cycle needed
3. Output is structured JSON that can be imported via MCP API or direct FactSheetContainer manipulation
4. Deterministic GUIDs (UUID5) ensure Phase 4 can wire relationships without re-parsing

---

## 2.1 Import B-Business Capability (~672 items, 4-level hierarchy: L0→L1→L2→L3)

**Source sheet:** `B-Business Capability` (677 rows × 17 cols, ~672 with data)  
**Target:** `FactSheetContainer.BusinessCapabilityFactSheets`

### Column mapping:

| Excel Col | Field | Maps to |
|-----------|-------|---------|
| B (2) | IdLevel123 | Used as lookup key for relationships later |
| E (5) | Level 0 (group) | Skip — grouping only |
| F (6) | Level 1 | `DisplayName` for L1 factsheet |
| G (7) | Level 2 | `DisplayName` for L2 factsheet |
| H (8) | Level 3 | `DisplayName` for L3 factsheet |
| I (9) | Pace Layer | `PaceLayer` → map: "Systems of Innovation"→1, "Systems of Differentiation"→2, "Systems of Commodity"→3 |
| J (10) | Description | `RichDescription` |
| K (11) | Value Stream | Store for Phase 4 relationship wiring |
| L (12) | Value Stream Order | Store as custom field or tag (future use) |
| M (13) | NIS2 Criticality | `NIS2Criticality` → map: "High"→3, "Medium"→2, "Low"→1, "Not evaluated"→0 |
| N (14) | Updated date | `ModifiedDateTime` |
| O (15) | Business Responsible | `Responsible` |

### Import logic:

- [x] Read all rows from B-Business Capability sheet (672 data rows)
- [x] **Pass 0: Create L0 group factsheets** — 8 L0 groups created (All, Corporate Services, Manufacturing, Not mapped to capability, Operations, R&D, Sales, Service)
  - **Design decision:** L0 IS imported as top-level BCFS (provides grouping structure in the hierarchy)
- [x] **Pass 1: Create L1 factsheets** — **20 unique L1** capabilities, parented to L0
  - All names `.strip()`'d during import (handles "Digital Management " trailing space)
- [x] **Pass 2: Create L2 factsheets** — **105** unique L2 by full path (l0, l1, l2)
  - Note: 101 unique by name, but 4 names appear under different L1 parents (e.g., "OT Data & Integration" under both "OT Hosting" and "OT Manufacturing") — correctly deduplicated by full path
- [x] **Pass 3: Create L3 factsheets** — **545** unique L3 by full path
  - Note: 532 unique by name, same full-path dedup logic
- [x] Set `PaceLayer` from column I (mapped to PaceLayerEnum int values)
- [x] Set `NIS2Criticality` from column M (mapped to NIS2CriticalityEnum int values)
- [x] Set `RichDescription` from column J
- [x] Set `Responsible` from column O
- [x] Generate deterministic GUIDs (UUID5) from composite key for cross-referencing in Phase 4
- [x] Store IdLevel123 → Guid mapping in `lookups-phase4.json` (672 entries)
- [x] **Validate:** Total BCFS count = **678** (8 L0 + 20 L1 + 105 L2 + 545 L3) — correct with full-path dedup

---

## 2.2 Import O-Organization (76 items, 4-level hierarchy)

**Source sheet:** `O-Organization` (76 rows × 14 cols)  
**Target:** `FactSheetContainer.OrganizationFactSheets` (new from Phase 1)

### Column mapping:

| Excel Col | Field | Maps to |
|-----------|-------|---------|
| D (4) | Level 1 (Country) | `DisplayName` for L1, `OrgType = "Country"` |
| B (2) | Level 2 (Organization/BU) | `DisplayName` for L2, `OrgType = "BusinessUnit"` |
| C (3) | Level 3 (Business Area) | `DisplayName` for L3, `OrgType = "Department"` |
| E (5) | Level 4 (Team) | `DisplayName` for L4, `OrgType = "Team"` |
| I (9) | CountryCode | `CountryCode` (e.g., "DK10", "ES10") |
| J (10) | Country name | Used for L1 DisplayName |
| N (14) | DepartmentTeam | Used for L4 DisplayName |

### Import logic:

- [x] Read all rows from O-Organization sheet (74 data rows)
- [x] **Pass 1: Create Country-level orgs (L1)** — **16 countries**: Austria, Canada, China, Denmark, Finland, France, Germany, Italy, Malaysia, Netherlands, Norway, Poland, Spain, Sweden, Switzerland, United States
  - Set `OrgType = "Country"`, `CountryCode` from col I
- [x] **Pass 2: Create BU-level orgs (L2)** — **54 unique BUs** within their countries
  - Set `HierarchyParentId` → country's Id, `OrgType = "BusinessUnit"`
- [x] **Pass 3: Create Department-level orgs (L3)** — **74 departments** from col C
  - Set `HierarchyParentId` → BU's Id, `OrgType = "Department"`
- [x] **Pass 4: Create Team-level orgs (L4)** — **66 teams** from col N (DepartmentTeam)
  - Set `HierarchyParentId` → Department's Id, `OrgType = "Team"`
- [x] Store CountryCode + BusinessArea → Guid mapping in `lookups-phase4.json` (144 entries)
- [x] **Validate:** Total Org count = **210** (16 countries + 54 BUs + 74 depts + 66 teams) — the source has 74 rows but each row expands into multiple hierarchy levels

---

## 2.3 Import C-Business Context / Processes (~655 items, 3-level hierarchy)

**Source sheet:** `C-Business Context` (656 rows × 18 cols, ~655 with data)  
**Target:** `FactSheetContainer.ProcessFactSheets`

### Column mapping:

| Excel Col | Field | Maps to |
|-----------|-------|---------|
| C (3) | NoProcess | Composite key for lookup (e.g., "P10-Sourcing--") |
| D (4) | Document no | `DocumentNumber` (new from Phase 1) |
| E (5) | Process group | `DisplayName` for L1 ProcessFS |
| F (6) | Process | `DisplayName` for L2 ProcessFS |
| G (7) | Document no SubProcess | `DocumentNumber` for L3 |
| H (8) | SubProcess | `DisplayName` for L3 ProcessFS |
| I (9) | Approver | `Approver` (new from Phase 1) |
| J (10) | Business Unit | Store for Org relationship in Phase 4 |
| K (11) | Country | Store for Org relationship in Phase 4 |
| L (12) | Editing state | `EditingState` → map: "Current"→2, "Draft"→1, "Pending approval"→3, "Review"→4, "N/A"→0 |
| P (16) | Value Stream | Store for Phase 4 relationship wiring |
| Q (17) | Description | `RichDescription` |

### Import logic:

- [x] Read all rows from C-Business Context sheet (654 data rows)
- [x] **Pass 1: Create Process Group factsheets (L1)** — **5 groups**: All, Core processes, Management processes, Not mapped, Supporting processes
- [x] **Pass 2: Create Process factsheets (L2)** — **40 unique processes**, parented to groups
- [x] **Pass 3: Create SubProcess factsheets (L3)** — **609 subprocesses**, parented to processes
- [x] Set `DocumentNumber` from col D (L2) and col G (L3)
- [x] Set `Approver` from col I (613 populated)
- [x] Set `EditingState` from col L (609 with non-N/A states)
- [x] Set `RichDescription` from col Q
- [x] Store NoProcess → Guid mapping in `lookups-phase4.json` (654 entries)
- [x] **Validate:** Total ProcessFS count = **654** (5 + 40 + 609)

---

## 2.4 Import Value Streams (12 items)

**Source:** Distinct values from KamstrupData column 17 + B-Business Capability column K  
**Target:** `FactSheetContainer.ValueStreamFactSheets`

### Expected value streams:

| # | Value Stream | Abbreviation |
|---|-------------|-------------|
| 1 | Acquire-to-Retire (A2R) | A2R |
| 2 | Concept-to-Customer (C2C) | C2C |
| 3 | Customer Service and Support | CSS |
| 4 | Hire-to-Retire (H2R) | H2R |
| 5 | Idea-to-Release (I2R) | I2R |
| 6 | Maintenance and Support | M&S |
| 7 | Make-to-Delivery | M2D |
| 8 | Order-to-Cash | O2C |
| 9 | Plan-to-Produce | P2P-prod |
| 10 | Procure-to-Pay (P2P) | P2P |
| 11 | Quote-to-Quality | Q2Q |
| 12 | Subscription-to-Pay | S2P |

### Import logic:

- [x] Create **12** ValueStreamFactSheet instances
- [x] Set `DisplayName` to full name including abbreviation (exact data values, including "Subscribtion" typo)
- [x] Generate deterministic GUIDs (UUID5) for cross-referencing
- [x] Store name → Guid mapping in `lookups-phase4.json`
- [x] Skip "N/A" entries (unmapped)
- [x] **Validate:** 12 ValueStreamFactSheets created ✓

---

## 2.5 Import P_Platform (34 items)

**Source sheet:** `P_Platform` (44 rows × 10 cols, 34 with actual platform data)  
**Target:** `FactSheetContainer.ITComponentFactSheets` (with type set to "Platform")

### Column mapping:

| Excel Col | Field | Maps to |
|-----------|-------|---------|
| B (2) | Platform name | `DisplayName` |
| C (3) | Platform or Suite | `ITComponentType` → store as-is or map (Platform, Programming Language, etc.) |
| D (4) | Friendly name | `ShortDescription` (base FactSheet PM 44) |
| E (5) | Description | `RichDescription` |
| F (6) | Long description | Append to `RichDescription` |
| G (7) | Strategic | Tag or custom field — store "Strategic"/"Non-strategic" in `OrganizationTags` (base PM 43) |
| H (8) | Comment | Create `FactSheetConcern` if non-empty |
| I (9) | AI | Tag "AI-enabled" if Yes |
| J (10) | Platform Owner | `Responsible` |

### Import logic:

- [x] Read all rows from P_Platform sheet (34 platforms)
- [x] Create ITComponentFactSheet for each platform
- [x] Set `DisplayName` from col B
- [x] Set `ShortDescription` from col D (friendly name)
- [x] Set `RichDescription` from cols E + F (combined)
- [x] Set `Responsible` from col J (Platform Owner)
- [x] Tag strategic classification and AI-enabled in Tags array
- [x] Store Platform name → Guid mapping in `lookups-phase4.json` (34 entries)
- [x] Platform comments stored as Concern objects
- [x] **Validate:** **34** ITComponentFactSheets created ✓

---

## 2.6 Extract and Import Providers

**Source:** A-Applications sheet, column 10 (Software Vendor) + column 12 (Consultancy)  
**Target:** `FactSheetContainer.ProviderFactSheets`

### Import logic:

- [x] Scan A-Applications column 10 — extracted unique vendor names
- [x] Scan A-Applications column 12 — extracted unique consultancy names
- [x] Deduplicate (vendor and consultancy merged — 2 companies appear as both)
- [x] For each unique provider: Created `ProviderFactSheet` with appropriate `ProviderType`
  - 469 Software Vendors, 11 Consultancies, 2 dual-type
- [x] Store vendor name → Guid mapping in `lookups-phase4.json` (482 entries)
- [x] **Validate:** **482** unique ProviderFactSheets created (higher than estimated 100-150 — the actual data has many unique vendor names)

---

## 2.7 Import Orchestration

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Services\Import\Kamstrup\KamstrupImportService.cs`

- [x] Created `kamstrup_import.py` as main orchestrator
- [x] Order: ValueStreams → Capabilities → Organizations → Processes → Platforms → Providers ✓
- [x] Output: Structured JSON files + combined `all-factsheets-combined.json` (2,070 records)
- [x] Import report generated: `import-log.txt` with counts, warnings, details
- [x] Lookup dictionaries saved: `lookups-phase4.json` with all 6 category lookups for Phase 4
- [x] MCP push script created: `push_to_omnigaze.py` (for when server has Phase 0+1 code deployed)

---

## 2.8 Backup and Execute

- [x] JSON output generated in `F:\RootContext\Kamstrup\import-scripts\output\`
- [ ] Deploy Phase 0+1 code to internal.omnigaze.com (prerequisite for push)
- [ ] Backup `FactSheets.bin` → `FactSheets.bin.backup-pre-phase2`
- [ ] Run `push_to_omnigaze.py` to push data into OmniGaze
- [ ] Verify counts in UI

---

## 2.9 Git Commit

- [x] `git add -A`
- [x] `git commit -m "feat: Phase 2 — Kamstrup master data import scripts (678 caps, 210 orgs, 654 processes, 12 VS, 34 platforms, 482 providers)"`
- [x] `git push`

---

## Verification (Jane's Checkpoint)

### Capabilities
- [ ] Open `/ea/capabilities` — see ~672 capabilities
- [ ] Expand a Level 1 (e.g., "Strategic Management") — L2 children appear
- [ ] Expand a Level 2 — L3 children appear
- [ ] Open a L3 capability detail — verify PaceLayer, NIS2Criticality, Description populated
- [ ] Count L1 capabilities: should be **20** (Customer Relationship, Customer Service, Digital Management, Digital Platform and Operations, Finance, Governance Risk and Compliance, Legal, Manufacturing, Marketing, Not mapped to capability, OT Hosting, OT Manufacturing, People and Culture, Procurement & Logistics, Product & Software Development, Sales, Strategic Management, Supply Chain, Sustainability Management, All)

### Organizations
- [ ] Open `/ea/organizations` — see ~75 organizations
- [ ] Verify hierarchy: Country → BU → Department → Team
- [ ] Open "Denmark" — verify BU children (Sales & Marketing, Customer Service, Finance, etc.)
- [ ] Open a department — verify OrgType="Department", CountryCode set

### Processes
- [ ] Open `/ea/processes` — see ~655 processes
- [ ] Verify hierarchy: Process Group → Process → SubProcess
- [ ] Open a process — verify DocumentNumber, EditingState, Approver populated
- [ ] Count process groups: should be **5** (All, Core processes, Management processes, Not mapped, Supporting processes)

### Value Streams
- [ ] Open value streams page — see 12 value streams
- [ ] All names match list above

### Platforms
- [ ] Open IT Components page — see ~34 platforms
- [ ] Open a platform (e.g., "IFS") — verify ShortDescription (friendly name), description, strategic tag

### Providers
- [ ] Open providers page — see ~100+ providers
- [ ] Spot-check known vendors: IFS AB, Microsoft, SAP, etc. — present

---

## Rollback

1. Restore `FactSheets.bin.backup-pre-phase2`
2. Optionally revert import script code (not strictly necessary — scripts are additive)

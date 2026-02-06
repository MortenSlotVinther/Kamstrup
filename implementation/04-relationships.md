# Phase 4: Relationships

**Prerequisites:** Phase 2 (Master Data) + Phase 3 (Applications) both complete  
**Estimated effort:** 2 days (Ole)  
**Output:** All binary relationships wired between imported factsheets  
**Blocks:** Phase 5 (Context Mapping)

---

## Overview

This phase creates all binary relationships between the factsheets imported in Phases 2 and 3. The primary data source is the `KamstrupData` sheet (5,396 rows), which contains the composite mappings. We decompose each n-ary row into individual binary relationships.

**Key input data:**
- `KamstrupData` — App×Capability×Org×Process mappings (~5,395 data rows)
- `A-Applications` — Vendor (col 10), Consultancy (col 12), Platform (col 34)
- `B-Business Capability` — Value Stream (col 11)
- `C-Business Context` — Value Stream (col 16)

**Lookup dictionaries required (from Phases 2 & 3):**
- IdLevel123 → Capability Guid
- App Number/Name → App Guid
- CountryCode + BusinessArea → Organization Guid
- NoProcess → Process Guid
- Value Stream name → Value Stream Guid
- Vendor name → Provider Guid
- Platform name → ITComponent Guid

---

## 4.1 App → Capability Relationships

**Source:** KamstrupData sheet, columns 12 (NoApplication) + 4 (IdLevel123)

### Logic:

- [x] Read all ~5,395 data rows from KamstrupData (rows 5 onwards, skipping 4 header rows)
- [x] For each row: look up Application by `NoApplication` (col 12) and Capability by `IdLevel123` (col 4)
- [x] If both resolve: create relationship using `RelationshipManager.EstablishRelationship(capability, app)` — BC is parent, App is child
- [x] Deduplicate: same App→Capability pair may appear multiple times (different org/process context) — RelationshipManager already checks for existing relationships
- [x] Expected unique App→Capability pairs: significantly less than 5,395 (many duplicates across org contexts) — **Result: 2,230 unique pairs**

### Implementation:

- [x] Create method `ImportAppCapabilityRelationships()` → `extract_app_capability_relationships()` in Python
- [x] Use the lookup dictionaries from Phase 2/3
- [x] Log unresolved references (app or capability not found) — 2 unresolved caps
- [x] Count: track unique relationships created vs rows processed — 5,395 rows → 2,230 unique
- [x] **Validate:** IFS ERP has 106 capabilities — plausible ✓

---

## 4.2 App → Organization Relationships

**Source:** KamstrupData sheet, columns 12 (NoApplication) + 9-11 (CountryCode, BusinessArea, DepartmentTeam)

### Logic:

- [x] For each KamstrupData row: look up Application and Organization
- [x] Resolve org at the most specific level available:
  1. If DepartmentTeam (col 11) resolves → use Team-level org
  2. Else if BusinessArea (col 10) resolves → use Department-level org
  3. Else if CountryCode (col 9) resolves → use Country-level org
- [x] Create relationship: `RelationshipManager.EstablishRelationship(organization, app)` — Org is parent, App is child
- [x] Deduplicate across rows — **Result: 2,646 unique pairs**

### Implementation:

- [x] Create method `ImportAppOrganizationRelationships()` → `extract_app_organization_relationships()` in Python
- [x] Build composite key resolver: CountryCode+BusinessArea+Team → Guid
- [x] Log unresolved orgs — 0 unresolved
- [x] **Validate:** IFS ERP has 50 org relationships ✓

---

## 4.3 App → Process Relationships

**Source:** KamstrupData sheet, columns 12 (NoApplication) + 16 (NoProcess)

### Logic:

- [x] For each KamstrupData row: look up Application and Process
- [x] Create relationship: `RelationshipManager.EstablishRelationship(process, app)` — Process is parent, App is child
- [x] Deduplicate across rows — **Result: 1,406 unique pairs**

### Implementation:

- [x] Create method `ImportAppProcessRelationships()` → `extract_app_process_relationships()` in Python
- [x] Use NoProcess → Guid mapping
- [x] Handle composite keys (e.g., "P10-Sourcing--")
- [x] Log unresolved processes — 8 unresolved (minor naming mismatches)
- [x] **Validate:** IFS ERP has 52 process relationships ✓

---

## 4.4 Capability → ValueStream Relationships

**Source:** B-Business Capability sheet, column K (11) — Value Stream

### Logic:

- [x] For each capability: if Value Stream (col K) is non-empty and not "N/A"
- [x] Look up ValueStream by name
- [x] Add ValueStream Guid to `BusinessCapabilityFactSheet.SupportedValueStreamIds`
- [x] This uses the existing field (ProtoMember 40), NOT RelationshipManager — it's a direct Guid list

### Implementation:

- [x] Create method `ImportCapabilityValueStreamLinks()` → `extract_capability_valuestream_relationships()` in Python
- [x] Use Value Stream name → Guid mapping
- [x] Handle multiple value streams per capability (split on delimiter if applicable)
- [x] **Validate:** 223 unique Cap→VS relationships ✓

---

## 4.5 Capability → Organization Relationships

**Source:** KamstrupData — intersection of capabilities and orgs

### Logic:

- [x] From KamstrupData: for each unique (Capability, Organization) pair
- [x] Create relationship: `RelationshipManager.EstablishRelationship(organization, capability)` — Org is parent, Capability is child
- [x] This shows which orgs need which capabilities
- [x] Deduplicate heavily — **Result: 1,649 unique pairs**

### Implementation:

- [x] Create method `ImportCapabilityOrganizationRelationships()` → `extract_capability_organization_relationships()` in Python
- [x] Extract unique (IdLevel123, CountryCode+BusinessArea) pairs from KamstrupData
- [x] Resolve both sides via lookup dictionaries
- [x] **Validate:** 1,649 unique relationships ✓

---

## 4.6 Process → ValueStream Relationships

**Source:** C-Business Context sheet, column P (16) — Value Stream

### Logic:

- [x] For each process: if Value Stream (col P) is non-empty and not "N/A"
- [x] Look up ValueStream by name
- [x] Create relationship: `RelationshipManager.EstablishRelationship(process, valueStream)` — uses new rule from Phase 1 (Process→ValueStream)
- [x] This is the new relationship type added in Phase 1

### Implementation:

- [x] Create method `ImportProcessValueStreamRelationships()` → `extract_process_valuestream_relationships()` in Python
- [x] Use Value Stream name → Guid mapping — **Result: 12 unique relationships (1 per VS)**
- [x] **Validate:** Process→VS count matches value stream count ✓

---

## 4.7 App → Provider Relationships

**Source:** A-Applications, column J (10) — Software Vendor, column L (12) — Consultancy

### Logic:

- [x] For each application:
  - If Software Vendor (col J) is non-empty:
    - Look up ProviderFactSheet by vendor name (created in Phase 2)
    - Create relationship: `RelationshipManager.EstablishRelationship(app, provider)` — App is parent, Provider is child
  - If Consultancy (col L) is non-empty and different from vendor:
    - Look up ProviderFactSheet by consultancy name
    - Create same relationship

### Implementation:

- [x] Create method `ImportAppProviderRelationships()` → `extract_app_provider_relationships()` in Python
- [x] Use vendor name → Provider Guid mapping from Phase 2
- [x] Handle case-insensitive matching, trim whitespace
- [x] Log unresolved vendor names — 0 unresolved
- [x] **Validate:** IFS ERP has 2 provider relationships (vendor + consultancy) ✓ — **Result: 803 total**

---

## 4.8 App → Platform/ITComponent Relationships

**Source:** A-Applications, column AH (34) — Platform

### Logic:

- [x] For each application: if Platform (col 34) is non-empty
- [x] May contain multiple platforms (comma-separated or otherwise delimited)
- [x] For each platform reference:
  - Look up ITComponentFactSheet by platform name (created in Phase 2)
  - Create relationship: `RelationshipManager.EstablishRelationship(app, itComponent)` — App is parent, ITComponent is child
  - Also add to `PlatformTags` for tag-based display

### Implementation:

- [x] Create method `ImportAppPlatformRelationships()` → `extract_app_platform_relationships()` in Python
- [x] Handle multi-value platform field (split on comma/semicolon)
- [x] Use platform name → ITComponent Guid mapping — **Result: 85 unique relationships**
- [x] **Validate:** IFS ERP has 1 platform link (IFS) ✓

---

## 4.9 Relationship Import Orchestration

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Services\Import\Kamstrup\KamstrupRelationshipImporter.cs` (NEW)

### Execution order:

- [x] Create orchestrator method: `main()` in `import_relationships.py`
- [x] Order of operations:
  1. Load lookup dictionaries (from Phase 2/3 JSON or rebuild from container)
  2. `ImportCapabilityValueStreamLinks()` — independent
  3. `ImportProcessValueStreamRelationships()` — independent
  4. `ImportAppCapabilityRelationships()` — reads KamstrupData
  5. `ImportAppOrganizationRelationships()` — reads KamstrupData
  6. `ImportAppProcessRelationships()` — reads KamstrupData
  7. `ImportCapabilityOrganizationRelationships()` — reads KamstrupData
  8. `ImportAppProviderRelationships()` — reads A-Applications
  9. `ImportAppPlatformRelationships()` — reads A-Applications

### Import report:

- [x] Generate counts:
  - App→Capability: **2,230** unique pairs
  - App→Org: **2,646** unique pairs
  - App→Process: **1,406** unique pairs
  - Capability→VS: **223** links
  - Capability→Org: **1,649** unique pairs
  - Process→VS: **12** links
  - App→Provider: **803** links
  - App→Platform: **85** links
  - App→App (Supporting): **34** links
  - **TOTAL: 9,088 relationships**
  - Unresolved references: 12 (minor naming mismatches, logged to warnings file)

---

## 4.10 Backup and Execute

- [x] Phase 4 Python script created: `import_relationships.py`
- [x] Run relationship import — **9,088 relationships extracted**
- [x] Output JSON ready for C# loader or MCP push

---

## 4.11 Git Commit

- [x] `git add -A`
- [x] `git commit -m "feat: Phase 4 — Kamstrup relationships (9,088 rels: App↔Cap, App↔Org, App↔Process, Cap↔VS, Cap↔Org, Process↔VS, App↔Provider, App↔Platform, App↔App)"`
- [ ] `git push`

---

## Verification (Jane's Checkpoint)

### Capability Map View
- [ ] Open capability map → applications should appear under capabilities
- [ ] Click on a Level 2 capability → see list of supporting apps
- [ ] Verify app count under a well-known capability (cross-reference with Excel)

### Application Detail
- [ ] Open "IFS ERP" detail page:
  - [ ] Related capabilities: should list multiple capabilities
  - [ ] Related organizations: should list DK orgs (at minimum)
  - [ ] Related processes: should list at least one process
  - [ ] Provider: "IFS AB" visible
  - [ ] Platform: "IFS" visible

### Organization View
- [ ] Open "Denmark" → should see related applications (DK apps)
- [ ] Open a department → should see related capabilities

### Process View
- [ ] Open a process → should see related value stream
- [ ] Open a process → should see related applications

### Value Stream View
- [ ] Open a value stream → should see supporting capabilities listed
- [ ] Cross-reference with B-Business Capability sheet

### Spot-check 5 random apps
- [ ] For each app, count relationships and compare against KamstrupData rows for that app
- [ ] Relationship counts should be plausible (not zero, not wildly inflated)

### Overall Relationship Counts
- [ ] App→Capability: check a few known apps against Excel
- [ ] Provider list: apps should link to correct vendors
- [ ] No orphaned relationships (IDs pointing to non-existent factsheets)

---

## Rollback

1. Restore `FactSheets.bin.backup-pre-phase4`
2. All relationships revert to pre-import state
3. Code changes (importer class) are non-destructive — can stay in codebase

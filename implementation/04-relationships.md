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

- [ ] Read all ~5,395 data rows from KamstrupData (rows 5 onwards, skipping 4 header rows)
- [ ] For each row: look up Application by `NoApplication` (col 12) and Capability by `IdLevel123` (col 4)
- [ ] If both resolve: create relationship using `RelationshipManager.EstablishRelationship(capability, app)` — BC is parent, App is child
- [ ] Deduplicate: same App→Capability pair may appear multiple times (different org/process context) — RelationshipManager already checks for existing relationships
- [ ] Expected unique App→Capability pairs: significantly less than 5,395 (many duplicates across org contexts)

### Implementation:

- [ ] Create method `ImportAppCapabilityRelationships()`
- [ ] Use the lookup dictionaries from Phase 2/3
- [ ] Log unresolved references (app or capability not found)
- [ ] Count: track unique relationships created vs rows processed
- [ ] **Validate:** Spot-check 10 apps — each has at least one related capability

---

## 4.2 App → Organization Relationships

**Source:** KamstrupData sheet, columns 12 (NoApplication) + 9-11 (CountryCode, BusinessArea, DepartmentTeam)

### Logic:

- [ ] For each KamstrupData row: look up Application and Organization
- [ ] Resolve org at the most specific level available:
  1. If DepartmentTeam (col 11) resolves → use Team-level org
  2. Else if BusinessArea (col 10) resolves → use Department-level org
  3. Else if CountryCode (col 9) resolves → use Country-level org
- [ ] Create relationship: `RelationshipManager.EstablishRelationship(organization, app)` — Org is parent, App is child
- [ ] Deduplicate across rows

### Implementation:

- [ ] Create method `ImportAppOrganizationRelationships()`
- [ ] Build composite key resolver: CountryCode+BusinessArea+Team → Guid
- [ ] Log unresolved orgs
- [ ] **Validate:** Spot-check 5 apps — each shows org relationships

---

## 4.3 App → Process Relationships

**Source:** KamstrupData sheet, columns 12 (NoApplication) + 16 (NoProcess)

### Logic:

- [ ] For each KamstrupData row: look up Application and Process
- [ ] Create relationship: `RelationshipManager.EstablishRelationship(process, app)` — Process is parent, App is child
- [ ] Deduplicate across rows

### Implementation:

- [ ] Create method `ImportAppProcessRelationships()`
- [ ] Use NoProcess → Guid mapping
- [ ] Handle composite keys (e.g., "P10-Sourcing--")
- [ ] Log unresolved processes
- [ ] **Validate:** Spot-check 5 apps — each shows process relationships

---

## 4.4 Capability → ValueStream Relationships

**Source:** B-Business Capability sheet, column K (11) — Value Stream

### Logic:

- [ ] For each capability: if Value Stream (col K) is non-empty and not "N/A"
- [ ] Look up ValueStream by name
- [ ] Add ValueStream Guid to `BusinessCapabilityFactSheet.SupportedValueStreamIds`
- [ ] This uses the existing field (ProtoMember 40), NOT RelationshipManager — it's a direct Guid list

### Implementation:

- [ ] Create method `ImportCapabilityValueStreamLinks()`
- [ ] Use Value Stream name → Guid mapping
- [ ] Handle multiple value streams per capability (split on delimiter if applicable)
- [ ] **Validate:** Open a capability → see linked value stream. Check "Strategic Management" → should link to a value stream.

---

## 4.5 Capability → Organization Relationships

**Source:** KamstrupData — intersection of capabilities and orgs

### Logic:

- [ ] From KamstrupData: for each unique (Capability, Organization) pair
- [ ] Create relationship: `RelationshipManager.EstablishRelationship(organization, capability)` — Org is parent, Capability is child
- [ ] This shows which orgs need which capabilities
- [ ] Deduplicate heavily

### Implementation:

- [ ] Create method `ImportCapabilityOrganizationRelationships()`
- [ ] Extract unique (IdLevel123, CountryCode+BusinessArea) pairs from KamstrupData
- [ ] Resolve both sides via lookup dictionaries
- [ ] **Validate:** Open an org → see related capabilities listed

---

## 4.6 Process → ValueStream Relationships

**Source:** C-Business Context sheet, column P (16) — Value Stream

### Logic:

- [ ] For each process: if Value Stream (col P) is non-empty and not "N/A"
- [ ] Look up ValueStream by name
- [ ] Create relationship: `RelationshipManager.EstablishRelationship(process, valueStream)` — uses new rule from Phase 1 (Process→ValueStream)
- [ ] This is the new relationship type added in Phase 1

### Implementation:

- [ ] Create method `ImportProcessValueStreamRelationships()`
- [ ] Use Value Stream name → Guid mapping
- [ ] **Validate:** Open a process → see linked value stream

---

## 4.7 App → Provider Relationships

**Source:** A-Applications, column J (10) — Software Vendor, column L (12) — Consultancy

### Logic:

- [ ] For each application:
  - If Software Vendor (col J) is non-empty:
    - Look up ProviderFactSheet by vendor name (created in Phase 2)
    - Create relationship: `RelationshipManager.EstablishRelationship(app, provider)` — App is parent, Provider is child
  - If Consultancy (col L) is non-empty and different from vendor:
    - Look up ProviderFactSheet by consultancy name
    - Create same relationship

### Implementation:

- [ ] Create method `ImportAppProviderRelationships()`
- [ ] Use vendor name → Provider Guid mapping from Phase 2
- [ ] Handle case-insensitive matching, trim whitespace
- [ ] Log unresolved vendor names
- [ ] **Validate:** Open "IFS ERP" → see "IFS AB" as related provider

---

## 4.8 App → Platform/ITComponent Relationships

**Source:** A-Applications, column AH (34) — Platform

### Logic:

- [ ] For each application: if Platform (col 34) is non-empty
- [ ] May contain multiple platforms (comma-separated or otherwise delimited)
- [ ] For each platform reference:
  - Look up ITComponentFactSheet by platform name (created in Phase 2)
  - Create relationship: `RelationshipManager.EstablishRelationship(app, itComponent)` — App is parent, ITComponent is child
  - Also add to `PlatformTags` for tag-based display

### Implementation:

- [ ] Create method `ImportAppPlatformRelationships()`
- [ ] Handle multi-value platform field (split on comma/semicolon)
- [ ] Use platform name → ITComponent Guid mapping
- [ ] **Validate:** Open an IFS app → see IFS platform linked

---

## 4.9 Relationship Import Orchestration

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Services\Import\Kamstrup\KamstrupRelationshipImporter.cs` (NEW)

### Execution order:

- [ ] Create orchestrator method: `async Task ImportAllRelationshipsAsync()`
- [ ] Order of operations:
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

- [ ] Generate counts:
  - App→Capability: N unique pairs
  - App→Org: N unique pairs
  - App→Process: N unique pairs
  - Capability→VS: N links
  - Capability→Org: N unique pairs
  - Process→VS: N links
  - App→Provider: N links
  - App→Platform: N links
  - Unresolved references: N (with details)

---

## 4.10 Backup and Execute

- [ ] Backup `FactSheets.bin` → `FactSheets.bin.backup-pre-phase4`
- [ ] Run relationship import
- [ ] Persist FactSheetContainer

---

## 4.11 Git Commit

- [ ] `git add -A`
- [ ] `git commit -m "feat: Phase 4 — Kamstrup relationships (App↔Cap, App↔Org, App↔Process, Cap↔VS, Process↔VS, App↔Provider, App↔Platform)"`
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

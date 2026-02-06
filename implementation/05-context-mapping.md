# Phase 5: Application Context Mapping (N-ary Model)

**Prerequisites:** Phase 4 (Relationships) complete  
**Estimated effort:** 2 days (Ole)  
**Output:** ~5,395 context mapping factsheets preserving per-combination TIME/Criticality  
**This is the solution to the #1 architectural gap (G1)**

---

## Why This Phase Exists

The binary relationships from Phase 4 tell you "App X supports Capability Y" and "App X is used by Org Z" — but they can't express *"App X's TIME rating for Capability Y in the context of Org Z is Invest, while for Capability W it's Migrate."*

This phase creates `ApplicationContextMappingFactSheet` — one factsheet per row of KamstrupData — preserving the full n-ary context with contextual TIME and Criticality.

**Reference:** [N-ary Solutions Analysis](../nary-solutions-2026-02-06.md) — Solution 2 (Recommended)

---

## 5.1 Create ApplicationContextMappingFactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\ApplicationContextMappingFactSheet.cs` (NEW)

- [ ] Create new file
- [ ] Class inherits `FactSheet`
- [ ] Add `[ProtoContract]` attribute

### Fields:

| ProtoMember | Field | Type | Description |
|-------------|-------|------|-------------|
| 1 | ApplicationId | `Guid` | Ref to ApplicationFactSheet |
| 2 | BusinessCapabilityId | `Guid` | Ref to BusinessCapabilityFactSheet |
| 3 | OrganizationId | `Guid?` | Ref to OrganizationFactSheet (nullable) |
| 4 | ProcessId | `Guid?` | Ref to ProcessFactSheet (nullable) |
| 5 | ValueStreamId | `Guid?` | Ref to ValueStreamFactSheet (nullable) |
| 6 | ContextualTIME | `PortFolioStrategy.StrategyEnum` | TIME per this specific mapping |
| 7 | ContextualCriticality | `BusinessSupport.CriticalityEnum` | Criticality per this mapping |
| 8 | ValidFrom | `DateTime?` | KamstrupData col 2 (Active from date) |
| 9 | ValidTo | `DateTime?` | KamstrupData col 3 (End date) |
| 10 | Projects | `string` | KamstrupData col 19 (Projects text) |
| 11 | Comment | `string` | KamstrupData col 20 (Comment) |
| 12 | ValueStreamOrder | `int` | KamstrupData col 18 (sort order) |

### Code:

```csharp
[ProtoContract]
public class ApplicationContextMappingFactSheet : FactSheet
{
    public override string GetColor() => "var(--fs-mapping)";
    public override bool GetRenderMaturity() => false;
    public override void UpdateConcerns() { }

    [ProtoMember(1)] public Guid ApplicationId { get; set; }
    [ProtoMember(2)] public Guid BusinessCapabilityId { get; set; }
    [ProtoMember(3)] public Guid? OrganizationId { get; set; }
    [ProtoMember(4)] public Guid? ProcessId { get; set; }
    [ProtoMember(5)] public Guid? ValueStreamId { get; set; }

    [ProtoMember(6)]
    [Newtonsoft.Json.JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
    public PortFolioStrategy.StrategyEnum ContextualTIME { get; set; } = PortFolioStrategy.StrategyEnum.Unmapped;

    [ProtoMember(7)]
    [Newtonsoft.Json.JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]
    public BusinessSupport.CriticalityEnum ContextualCriticality { get; set; } = BusinessSupport.CriticalityEnum.Unmapped;

    [ProtoMember(8)] public DateTime? ValidFrom { get; set; }
    [ProtoMember(9)] public DateTime? ValidTo { get; set; }
    [ProtoMember(10)] public string Projects { get; set; }
    [ProtoMember(11)] public string Comment { get; set; }
    [ProtoMember(12)] public int ValueStreamOrder { get; set; }

    // Display helpers
    public string ApplicationDisplay => GetReferencedName(ApplicationId);
    public string CapabilityDisplay => GetReferencedName(BusinessCapabilityId);
    public string OrganizationDisplay => OrganizationId.HasValue ? GetReferencedName(OrganizationId.Value) : "";
    public string ProcessDisplay => ProcessId.HasValue ? GetReferencedName(ProcessId.Value) : "";
    public string ValueStreamDisplay => ValueStreamId.HasValue ? GetReferencedName(ValueStreamId.Value) : "";

    private string GetReferencedName(Guid id)
    {
        var fs = FactSheetContainer.Instance.GetFactSheetById(id);
        return fs?.DisplayName ?? "(unresolved)";
    }
}
```

---

## 5.2 Register in FactSheet + FactSheetContainer

### FactSheet base class:
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\FactSheet.cs`

- [ ] Add `[ProtoInclude(519, typeof(ApplicationContextMappingFactSheet))]`
  - 519 is next after 518 (OrganizationFactSheet from Phase 1)

### FactSheetContainer:
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\FactSheetContainer.cs`

- [ ] Add `[ProtoMember(20)] public List<ApplicationContextMappingFactSheet> ApplicationContextMappingFactSheets { get; set; } = new();`
  - 20 is next after 19 (OrganizationFactSheets from Phase 1)
- [ ] Update `RemoveFactSheet()` — add case
- [ ] Update `AllFactSheets` — add `.Concat(ApplicationContextMappingFactSheets)`
- [ ] Update `AddIfNotExists()` — add case
- [ ] Update `GetFactSheetsByType<T>()` — add case

### RelationshipManager:
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Components\FactSheetRelations\RelationshipManager.cs`

- [ ] No new rules needed — the mapping factsheet uses direct Guid references, not ParentFactSheetsIds relationships

### CSS:
- [ ] Add `--fs-mapping: #9C27B0;` (purple — distinct from other types) to theme file

---

## 5.3 Import KamstrupData as Context Mappings

**Source sheet:** `KamstrupData` (5,399 total rows × 20 cols, ~5,395 data rows starting at row 5)  
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Services\Import\Kamstrup\KamstrupContextMappingImporter.cs` (NEW)

### Column mapping:

| KamstrupData Col | # | Field | Maps to |
|------------------|---|-------|---------|
| B (2) | Active from date | `ValidFrom` | Parse DateTime |
| C (3) | End date | `ValidTo` | Parse DateTime |
| D (4) | IdLevel123 | → `BusinessCapabilityId` | Lookup via capability dictionary |
| E-H (5-8) | Capability levels | → `DisplayName` | Auto-generate: "AppName → CapabilityName (OrgName)" |
| I (9) | CountryCode | → `OrganizationId` part 1 | Lookup |
| J (10) | Business Area | → `OrganizationId` part 2 | Lookup |
| K (11) | Department/Team | → `OrganizationId` part 3 | Lookup (most specific) |
| L (12) | NoApplication | → `ApplicationId` | Lookup via app dictionary |
| M (13) | Application Name | Used for DisplayName generation | |
| N (14) | **Gartner TIME** | → `ContextualTIME` | Map: Tolerate→1, Invest→2, Migrate→3, Eliminate→4 |
| O (15) | **Business Criticality** | → `ContextualCriticality` | Map: Administrative→1, Operational→2, Critical→3, MissionCritical→4 |
| P (16) | NoProcess | → `ProcessId` | Lookup via process dictionary |
| Q (17) | Value Stream | → `ValueStreamId` | Lookup via VS dictionary |
| R (18) | Value Stream Order | → `ValueStreamOrder` | Parse int |
| S (19) | Projects | → `Projects` | Direct string |
| T (20) | Comment | → `Comment` | Direct string |

### Criticality mapping:

| Kamstrup Criticality | OmniGaze `CriticalityEnum` |
|---------------------|---------------------------|
| Administrative Service | `AdministrativeService` (1) |
| Business Operational | `BusinessOperational` (2) |
| Business Critical | `BusinessCritical` (3) |
| Mission Critical | `MissionCritical` (4) |
| Empty | `Unmapped` (0) |

### Import logic:

- [ ] Read all ~5,395 data rows from KamstrupData (starting at row 5, skipping 4 header rows)
- [ ] For each row:
  1. Resolve ApplicationId from NoApplication (col 12)
  2. Resolve BusinessCapabilityId from IdLevel123 (col 4)
  3. Resolve OrganizationId from CountryCode+BusinessArea+Team (cols 9-11) — use most specific match
  4. Resolve ProcessId from NoProcess (col 16)
  5. Resolve ValueStreamId from Value Stream name (col 17)
  6. Map ContextualTIME from col 14
  7. Map ContextualCriticality from col 15
  8. Parse ValidFrom/ValidTo from cols 2-3
  9. Set Projects and Comment from cols 19-20
  10. Generate DisplayName: "{AppName} → {CapabilityName} ({OrgName})"
  11. Generate deterministic GUID from composite key
- [ ] Create `ApplicationContextMappingFactSheet` for each row
- [ ] Add to `FactSheetContainer.ApplicationContextMappingFactSheets`
- [ ] **Handle unresolved references:** Create mapping anyway with null Guid fields, log warning
- [ ] **Validate:** ~5,395 mappings created

---

## 5.4 Create List Page

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\ApplicationContextMappingsEAPage.razor` (NEW)  
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\ApplicationContextMappingsEAPage.razor.cs` (NEW)

- [ ] Route: `@page "/ea/context-mappings"`
- [ ] Grid columns:
  - Application (link to app detail)
  - Capability (link to capability detail)
  - Organization (link to org detail)
  - Process (link to process detail)
  - Value Stream
  - Contextual TIME (color-coded: Invest=green, Tolerate=yellow, Migrate=orange, Eliminate=red)
  - Contextual Criticality (color-coded)
  - Valid From / Valid To
- [ ] Filters:
  - Filter by Application
  - Filter by Capability (L1, L2, L3)
  - Filter by Organization
  - Filter by TIME rating
  - Filter by Criticality
- [ ] Use `Virtualize` for 5,396 rows
- [ ] Add to navigation menu under EA section

---

## 5.5 Create Detail Section

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\ApplicationContextMappingSummarySection.razor` (NEW)

- [ ] Display all 5 referenced entities as clickable links
- [ ] Show Contextual TIME with color chip
- [ ] Show Contextual Criticality with color chip
- [ ] Show ValidFrom / ValidTo dates
- [ ] Show Projects and Comment text
- [ ] Show ValueStreamOrder
- [ ] Register in `FactsheetSummary.razor` — add case for `ApplicationContextMappingFactSheet`

---

## 5.6 Capability Map Integration (Optional Enhancement)

**Existing file:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\CapabilitiesAndApplicationsPage\` (or equivalent)

When showing an application tile on the capability map:

- [ ] Instead of showing the app's global TIME (from `PortFolioStrategy.TIME`):
  - Look up `ApplicationContextMappingFactSheets` where `ApplicationId == app.Id && BusinessCapabilityId == capability.Id`
  - If found: use `ContextualTIME` for color-coding
  - If not found: fall back to global TIME
- [ ] This makes the capability map contextually accurate

**Note:** This is an enhancement — can be deferred to after basic Phase 5 validation.

---

## 5.7 Backup and Execute

- [ ] Backup `FactSheets.bin` → `FactSheets.bin.backup-pre-phase5`
- [ ] Run context mapping import
- [ ] Persist FactSheetContainer

---

## 5.8 Git Commit

- [ ] `git add -A`
- [ ] `git commit -m "feat: Phase 5 — Kamstrup context mapping (~5,395 n-ary mapping factsheets with contextual TIME/Criticality)"`
- [ ] `git push`

---

## Verification (Jane's Checkpoint)

### List Page
- [ ] Open `/ea/context-mappings` — page loads
- [ ] Total rows: ~5,395 (check count display)
- [ ] Scroll through list — virtualization works (no UI freeze)

### Filter Tests
- [ ] Filter by Application "IFS ERP" — see all its capability mappings
- [ ] Filter by TIME = "Migrate" — see only migrate mappings
- [ ] Filter by Organization "Denmark" — see only DK mappings

### Contextual TIME Verification
- [ ] Find an application that has **different TIME ratings** across capabilities:
  - Open context mapping list
  - Filter by that app
  - Verify at least two rows with different ContextualTIME values
  - Cross-reference with KamstrupData in Excel
- [ ] This is the **key test** — if the same app shows different TIME per capability, the n-ary model works

### Criticality Verification
- [ ] Find an app with "Mission Critical" for one capability but "Administrative Service" for another
- [ ] Verify both rows show correct ContextualCriticality

### Detail Page
- [ ] Click on a mapping row → detail page opens
- [ ] All 5 referenced entities shown as links
- [ ] Click each link → navigates to correct factsheet

### Cross-reference with Excel
- [ ] Pick 3 random rows from KamstrupData in Excel
- [ ] Find same mapping in OmniGaze
- [ ] Verify: all fields match (App, Capability, Org, Process, VS, TIME, Criticality, dates)

---

## Rollback

1. Restore `FactSheets.bin.backup-pre-phase5`
2. `git revert HEAD` (removes the new factsheet type code)
3. **Important:** If reverting code, also remove the `ProtoInclude(519)` and `ProtoMember(20)` — BUT the old .bin file won't have data for these, so loading is safe even without code revert
4. Capability map integration changes (§5.6) can be reverted independently

---

## Files Changed Summary

| File | Action | Key Changes |
|------|--------|-------------|
| `ApplicationContextMappingFactSheet.cs` | NEW | New factsheet type (12 ProtoMembers) |
| `FactSheet.cs` | EDIT | ProtoInclude(519) |
| `FactSheetContainer.cs` | EDIT | ProtoMember(20), update 4+ methods |
| `KamstrupContextMappingImporter.cs` | NEW | Import 5,396 rows |
| `ApplicationContextMappingsEAPage.razor` + `.cs` | NEW | List page with filters |
| `ApplicationContextMappingSummarySection.razor` | NEW | Detail section |
| `FactsheetSummary.razor` | EDIT | Add case for new type |
| `CustomNavMenu.razor` | EDIT | Add Context Mappings link |
| CSS theme file | EDIT | Add `--fs-mapping` color |
| Capability map page (optional) | EDIT | Contextual TIME display |

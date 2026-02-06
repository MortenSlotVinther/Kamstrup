# Phase 1: Model Foundation

**Prerequisites:** None  
**Estimated effort:** 2–3 days (Ole)  
**Output:** All schema changes committed, zero data import  
**Blocks:** Phases 2, 3, 4, 5, 6

---

## 1.1 Create OrganizationFactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\OrganizationFactSheet.cs` (NEW)

- [x] Create new file `OrganizationFactSheet.cs`
- [x] Class inherits `FactSheet`
- [x] Add `[ProtoContract]` attribute
- [x] Add `[ProtoMember(1)] public string OrgType { get; set; }` — values: "Country", "BusinessUnit", "Department", "Team"
- [x] Add `[ProtoMember(2)] public string CountryCode { get; set; }` — e.g., "DK10", "ES10"
- [x] Add `[ProtoMember(3)] public string CostCenter { get; set; }` — optional financial link
- [x] Override `GetColor()` → return `"var(--fs-organization)"` (define CSS var later)
- [x] Override `GetRenderMaturity()` → `return false;`
- [x] Override `UpdateConcerns()` → empty body
- [x] Add display helpers: `ApplicationsDisplay`, `CapabilitiesDisplay`, `ProcessesDisplay` (same pattern as `UserGroupFactSheet`)

**Proto number allocation:**
| ProtoMember | Field | Type |
|-------------|-------|------|
| 1 | OrgType | string |
| 2 | CountryCode | string |
| 3 | CostCenter | string |

---

## 1.2 Register OrganizationFactSheet in Base Class

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\FactSheet.cs`

- [x] Add `[ProtoInclude(518, typeof(OrganizationFactSheet))]` after line `[ProtoInclude(517, typeof(ValueChainFactSheet))]`

**Verification:** 518 is the next available ProtoInclude number (517 = ValueChainFactSheet is current max).

---

## 1.3 Update FactSheetContainer

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\FactSheetContainer.cs`

- [x] Add property: `[ProtoMember(19)] public List<OrganizationFactSheet> OrganizationFactSheets { get; set; } = new List<OrganizationFactSheet>();`
  - Place after `[ProtoMember(18)] ... ValueChainFactSheets` (line ~29)
- [x] Update `RemoveFactSheet()` — add: `else if (sheet is OrganizationFactSheet) OrganizationFactSheets.Remove(sheet as OrganizationFactSheet);`
- [x] Update `AllFactSheets` getter — add: `.Concat(OrganizationFactSheets)` to the chain
- [x] Update `AddIfNotExists()` (search for the method) — add case for `OrganizationFactSheet`
- [x] Update `GetFactSheetsByType<T>()` (search for the method) — add case for `OrganizationFactSheet`
- [x] Search for any other switch/if-else on factsheet types and add OrganizationFactSheet

**ProtoMember 19** is the next available (18 = ValueChainFactSheets is current max).

---

## 1.4 Create New Enums

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\Enums.cs` (add to existing) or create a new `KamstrupEnums.cs`

### PaceLayerEnum
- [x] Create enum `PaceLayerEnum`:
```csharp
public enum PaceLayerEnum
{
    [Description("Unspecified")] Unspecified = 0,
    [Description("Systems of Innovation")] SystemsOfInnovation = 1,
    [Description("Systems of Differentiation")] SystemsOfDifferentiation = 2,
    [Description("Systems of Commodity")] SystemsOfCommodity = 3
}
```

### NIS2CriticalityEnum
- [x] Create enum `NIS2CriticalityEnum`:
```csharp
public enum NIS2CriticalityEnum
{
    [Description("Not Evaluated")] NotEvaluated = 0,
    [Description("Low")] Low = 1,
    [Description("Medium")] Medium = 2,
    [Description("High")] High = 3
}
```

### EditingStateEnum
- [x] Create enum `EditingStateEnum`:
```csharp
public enum EditingStateEnum
{
    [Description("N/A")] NotApplicable = 0,
    [Description("Draft")] Draft = 1,
    [Description("Current")] Current = 2,
    [Description("Pending Approval")] PendingApproval = 3,
    [Description("Review")] Review = 4
}
```

### UtilizationEnum
- [x] Create enum `UtilizationEnum`:
```csharp
public enum UtilizationEnum
{
    [Description("Unknown")] Unknown = 0,
    [Description("None")] None = 1,
    [Description("Low")] Low = 2,
    [Description("Medium")] Medium = 3,
    [Description("High")] High = 4
}
```

---

## 1.5 Add Enum Values to Existing Enums

### HostingTypeEnum (+3 values)
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\Hosting.cs`

Current enum: `Unmapped=0, Desktop=1, Mobile=2, OnPrem=3, Hybrid=4, SaaS=5, PaaS=6, IaaS=7`

- [x] Add `ThirdPartyHosted = 8`
- [x] Add `EdgeComputing = 9`
- [x] Add `DistributedApp = 10`

### AIRiskLevel (+1 value)
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\AIClassification.cs`

Current enum: `NotApplicable=0, Minimal=1, Limited=2, High=3, Unacceptable=4`

- [x] Add `[Description("Not Evaluated")] NotEvaluated = 5`

### SecurityDebtLevel (+1 value)
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\SecurityAssessment.cs`

Current enum: `Unknown=0, None=1, Low=2, Medium=3, High=4, Critical=5`

- [x] Add `[Description("Investigate")] Investigate = 6`

---

## 1.6 Add Fields to BusinessCapabilityFactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\BusinessCapabilityFactSheet.cs`

Current max used ProtoMember on this class: 100 (_level). Safe next sequential block: 6-39 are available (5=CapabilityType, 40=SupportedValueStreamIds).

- [x] Add `[ProtoMember(6)] public PaceLayerEnum PaceLayer { get; set; } = PaceLayerEnum.Unspecified;`
- [x] Add `[ProtoMember(7)] public NIS2CriticalityEnum NIS2Criticality { get; set; } = NIS2CriticalityEnum.NotEvaluated;`
- [x] Add appropriate `using` for enum namespace
- [x] Add `[Description]` and `[Newtonsoft.Json.JsonConverter(typeof(Newtonsoft.Json.Converters.StringEnumConverter))]` attributes

**Proto numbers verified:** 6 and 7 are unused in BusinessCapabilityFactSheet (jumps from 5 to 40).

---

## 1.7 Add Fields to ProcessFactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\ProcessFactSheet.cs`

Current ProtoMembers: 51 (Frequency), 52 (DurationInHours). Next safe: 53.

- [ ] Add `[ProtoMember(53)] public string DocumentNumber { get; set; }` — e.g., "SP01.1"
- [ ] Add `[ProtoMember(54)] public EditingStateEnum EditingState { get; set; } = EditingStateEnum.NotApplicable;`
- [ ] Add `[ProtoMember(55)] public string Approver { get; set; }` — email or name, separate from Responsible

**Proto numbers verified:** 53, 54, 55 are all unused in ProcessFactSheet.

---

## 1.8 Add LifecycleStageLabel to Base FactSheet

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Model\EnterpriseArchitecture\FactSheet.cs`

Current max used ProtoMember on base: 44 (ShortDescription). Next safe: 45.

- [ ] Add `[ProtoMember(45)] public string LifecycleStageLabel { get; set; }` — stores Kamstrup's original stage name (e.g., "1-Strategic", "5-Investigate")

This preserves the customer's own lifecycle classification alongside OmniGaze's 5-phase model.

---

## 1.9 Update RelationshipManager

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Components\FactSheetRelations\RelationshipManager.cs`

Add a new method `AddOrganizationRules()` and call it from `InitializeRelationshipRules()`:

- [ ] Add `Organization → Application` (ParentChild) — org uses app
- [ ] Add `Organization → BusinessCapability` (ParentChild) — org needs capability
- [ ] Add `Organization → Process` (ParentChild) — org runs process
- [ ] Add `Organization → ValueStream` (ParentChild) — org participates in VS
- [ ] Add `Process → ValueStream` (ParentChild) — process belongs to value stream (**Gap G8**)

New method:
```csharp
private void AddOrganizationRules(Dictionary<(Type source, Type target), RelationshipRule> rules)
{
    var orgChildren = new[]
    {
        typeof(ApplicationFactSheet),
        typeof(BusinessCapabilityFactSheet),
        typeof(ProcessFactSheet),
        typeof(ValueStreamFactSheet)
    };

    foreach (var childType in orgChildren)
    {
        rules.Add(
            (typeof(OrganizationFactSheet), childType),
            new RelationshipRule(typeof(OrganizationFactSheet), childType, RelationType.ParentChild)
        );
    }

    // Process → ValueStream (Gap G8)
    rules.Add(
        (typeof(ProcessFactSheet), typeof(ValueStreamFactSheet)),
        new RelationshipRule(typeof(ProcessFactSheet), typeof(ValueStreamFactSheet), RelationType.ParentChild)
    );
}
```

- [x] Call `AddOrganizationRules(rules);` inside `InitializeRelationshipRules()` before `return rules;`
- [x] Add `using` for `OrganizationFactSheet` and `ValueStreamFactSheet` if needed

---

## 1.10 Create Organization EA List Page

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\OrganizationsEAPage.razor` (NEW)
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\OrganizationsEAPage.razor.cs` (NEW)

- [x] Create `OrganizationsEAPage.razor` — follow pattern from `UserGroupsEAPage.razor`
- [x] Route: `@page "/EA/Sheets/OrganizationsPage"`
- [x] Grid columns: DisplayName, OrgType, CountryCode, CostCenter, ParentOrg, ChildCount, RelatedApps count
- [x] Use `EAGrid` or existing EA grid component
- [x] Support hierarchy expand/collapse (same pattern as BusinessCapabilityEAPage)
- [x] Inline code (no separate .cs) `.razor.cs` file with data loading from `FactSheetContainer.Instance.OrganizationFactSheets`

---

## 1.11 Create Organization Summary Section

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\OrganizationSummarySection.razor` (NEW)

- [x] Create summary section — follow pattern from `UserGroupSummarySection.razor`
- [x] Display fields: OrgType (dropdown), CountryCode (text), CostCenter (text)
- [x] Show related factsheets: Applications, Capabilities, Processes
- [x] Register in `FactsheetSummary.razor` — add case for `OrganizationFactSheet`

---

## 1.12 Add Organization to Navigation Menu

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Shared\CustomNavMenu.razor`

- [x] Add navigation entry for Organizations under the EA section
- [x] Icon: uses organization/building icon (MudBlazor `Icons.Material.Filled.Business` or `CorporateFare`)
- [x] Link: `/EA/Sheets/OrganizationsPage`
- [x] Position: after Business Processes, before Value Streams (or logical EA ordering)

---

## 1.13 Update BusinessCapability Summary Section

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\BusinessCapabilitySummarySectionDisplay.razor`
**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\BusinessCapabilitySummarySectionEdit.razor`

### Display mode:
- [x] Add "Pace Layer" field display — show `PaceLayerEnum` value with color coding
  - SystemsOfInnovation → green
  - SystemsOfDifferentiation → blue  
  - SystemsOfCommodity → gray
- [x] Add "NIS2 Criticality" field display — show `NIS2CriticalityEnum` value
  - High → red chip
  - Medium → yellow chip
  - Low → green chip

### Edit mode:
- [x] Add PaceLayer dropdown selector (3 values + Unspecified)
- [x] Add NIS2Criticality dropdown selector (3 values + NotEvaluated)

---

## 1.14 Update Process Summary Section

**Files to update:**
- `F:\RootContext\OmniGazeRoot\OmniGaze\Pages\EA\FactsheetPage\` — find or create Process summary section

- [ ] Add "Document Number" text field — displays `DocumentNumber` (e.g., "SP01.1")
- [ ] Add "Editing State" dropdown — displays/edits `EditingStateEnum`
- [ ] Add "Approver" text field — separate from Responsible

---

## 1.15 Add CSS Variable for Organization Color

**File:** `F:\RootContext\OmniGazeRoot\OmniGaze\wwwroot\css\` (find theme file)

- [x] Add `--fs-organization: #FF6B00;` (orange — distinct from existing colors) or suitable EA color

---

## 1.16 Build and Test

- [ ] Run `dotnet build` in `F:\RootContext\OmniGazeRoot\` — zero errors
- [ ] Run `dotnet test` in `F:\RootContext\OmniGazeRoot\OmniGaze.Tests\` — all existing tests pass
- [ ] Load existing `FactSheets.bin` with new code — no deserialization errors
- [ ] Verify `OrganizationFactSheets` list is empty (not null) after loading old .bin
- [ ] Verify new enum fields on existing types default to 0/Unspecified/NotApplicable
- [ ] Save and reload — round-trip test passes

---

## 1.17 Git Commit

- [ ] `cd F:\RootContext\OmniGazeRoot`
- [ ] `git add -A`
- [ ] `git commit -m "feat: Phase 1 — Kamstrup model foundation (OrganizationFS, new enums, new fields, new relationships)"`
- [ ] `git push`

---

## Verification (Jane's Checkpoint)

After Ole deploys Phase 1:

- [ ] **Navigate to /ea/organizations** — page loads without error, shows empty grid
- [ ] **Open Business Capability detail page** — see PaceLayer and NIS2 Criticality fields (both showing default/empty)
- [ ] **Open Process detail page** — see Document Number, Editing State, and Approver fields
- [ ] **Check nav menu** — Organizations link visible in sidebar
- [ ] **Open existing app/capability/process** — all existing data intact, no corruption

---

## Rollback

If Phase 1 causes issues:
1. `git revert HEAD` (reverts the Phase 1 commit)
2. `dotnet build` — old code restores
3. No .bin changes were made, so data is safe
4. All schema changes are additive — even if we don't revert, old .bin files load fine

---

## Files Changed Summary

| File | Action | Key Changes |
|------|--------|-------------|
| `OrganizationFactSheet.cs` | NEW | New factsheet type |
| `FactSheet.cs` | EDIT | ProtoInclude(518), ProtoMember(45) LifecycleStageLabel |
| `FactSheetContainer.cs` | EDIT | ProtoMember(19) OrganizationFactSheets, update 4+ methods |
| `Enums.cs` or `KamstrupEnums.cs` | NEW/EDIT | 4 new enums |
| `Hosting.cs` | EDIT | +3 enum values |
| `AIClassification.cs` | EDIT | +1 enum value |
| `SecurityAssessment.cs` | EDIT | +1 enum value |
| `BusinessCapabilityFactSheet.cs` | EDIT | +2 fields (PM 6, 7) |
| `ProcessFactSheet.cs` | EDIT | +3 fields (PM 53, 54, 55) |
| `RelationshipManager.cs` | EDIT | +5 relationship rules |
| `OrganizationsEAPage.razor` + `.cs` | NEW | List page |
| `OrganizationSummarySection.razor` | NEW | Detail section |
| `BusinessCapabilitySummarySectionDisplay.razor` | EDIT | +PaceLayer, +NIS2 |
| `BusinessCapabilitySummarySectionEdit.razor` | EDIT | +PaceLayer, +NIS2 |
| `CustomNavMenu.razor` | EDIT | +Organizations link |
| CSS theme file | EDIT | +`--fs-organization` color |

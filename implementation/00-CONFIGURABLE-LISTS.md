# Phase 0: Configurable Lists — Replacing Hardcoded Enums

**Created:** 2026-02-07  
**Owner:** Morten Vinther  
**Architect:** Ole (AI)  
**Status:** Implementation Complete — Pending Tests & Manual Verification (2026-02-07)

---

## 1. Executive Summary

Certain hardcoded C# enums in OmniGaze need to become **customer-configurable dropdown lists** so that different customers (Kamstrup, OmniGaze default, future customers) can define their own values. This document designs a **backwards-compatible** migration path that preserves all existing `.bin` data.

### Target Enums (5)
| Enum | Current Location | OmniGaze Values | Kamstrup Values | Mismatch |
|------|-----------------|-----------------|-----------------|----------|
| **Lifecycle Stages** | `LifeCycle` class (date-based phases) | 5 phases (Plan→EndOfLife) | 11 stages (Strategic, Important, etc.) | 🔴 Critical |
| **CostType** | `Cost.cs` enum | 2 (YearlyLicense, OneOffCapex) | 9 (License, Support, Maintenance, Hosting, FTE, etc.) | 🔴 Critical |
| **HostingType** | `Hosting.HostingTypeEnum` | 8 (Unmapped→IaaS) | 5 (OnPrem, Cloud, ThirdParty, Edge, Distributed) | 🟡 Medium |
| **ITComponentType** | `ITComponentFactSheet.ITComponentType` | String "Server" (default) | Platform, Suite, Programming Language, etc. | 🟡 Medium |
| **EditingState** | New (not yet in codebase) | N/A | 5 (Current, Draft, PendingApproval, Review, N/A) | 🟢 New |

### Hardcoded Enums (Stay as-is)
- Gartner TIME (4 values — industry standard)
- Business Criticality (4 values — standard)
- Pace Layer (3 values — Gartner standard)
- TechnicalFit / FunctionalFit (5 values — standard assessment scale)
- NIS2 Criticality (4 values — regulatory)
- AI Risk Level (5 values — EU AI Act)

---

## 2. Architecture Design

### 2.1 Key Insight: What Already Exists

The codebase already has a **complete extensible field system** via `CustomColumnDefinition` and `CustomFieldValue`:

- `CustomColumnDefinition` supports `Dropdown` and `MultiSelect` field types with `AllowedValues` list
- `CustomFieldValue` stores values as strings, keyed by `ColumnId` (Guid)
- `CustomerSettings.CustomColumnDefinitions` is the central registry (serialized to `CustomerSettings.bin`)
- `StandardGrid2` automatically registers custom columns into grids
- Values stored on each `FactSheet` in `List<CustomFieldValue> CustomFields` (ProtoMember 42)

**However, this system is designed for truly custom "extra" columns**, not for replacing core model properties that have UI bindings, display logic, color coding, and computation logic (like LifeCycle).

### 2.2 Chosen Approach: **ConfigurableListDefinition** (New System)

We introduce a new `ConfigurableListDefinition` concept — similar to `CustomColumnDefinition` but purpose-built for replacing enums:

```
┌──────────────────────────────────────────┐
│         CustomerSettings.bin             │
│                                          │
│  ConfigurableListDefinitions:            │
│  ┌─────────────────────────────────┐     │
│  │ ListId: "HostingType"           │     │
│  │ DisplayName: "Install Type"     │     │
│  │ Values:                         │     │
│  │   [0] "Unmapped" (legacy=0)     │     │
│  │   [1] "Desktop" (legacy=1)     │     │
│  │   [2] "Mobile" (legacy=2)      │     │
│  │   ...                           │     │
│  │   [8] "Edge Computing" (new)    │     │
│  │   [9] "Distributed" (new)       │     │
│  └─────────────────────────────────┘     │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │ ListId: "LifecycleStage"        │     │
│  │ DisplayName: "Lifecycle Stage"  │     │
│  │ Values:                         │     │
│  │   [0] "Not Planned" (legacy=0)  │     │
│  │   [1] "Planning" (legacy=1)     │     │
│  │   ...                           │     │
│  │   [5] "Strategic" (new)         │     │
│  │   [6] "Important" (new)         │     │
│  └─────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

### 2.3 The Dual-Field Migration Pattern

For each enum-to-configurable migration, we use **dual fields**:

```csharp
// BEFORE (current code):
[ProtoMember(1)] public HostingTypeEnum Criticality { get; set; }

// AFTER (migrated):
[ProtoMember(1)] public HostingTypeEnum Criticality { get; set; }  // KEEP for backwards compat
[ProtoMember(3)] public string HostingTypeValue { get; set; }       // NEW string field

// On deserialization: if HostingTypeValue is null/empty, populate from Criticality enum
// On save: always write HostingTypeValue (string). Criticality stays frozen for old readers.
```

**Why this works:**
1. Old `.bin` files contain `ProtoMember(1)` with integer enum → deserializes correctly into `Criticality`
2. Post-load migration hook checks: if `HostingTypeValue` is null, set it from `Criticality.ToString()`
3. All UI and logic switches to reading `HostingTypeValue` (string)
4. On save, both fields are written — the old enum field for any theoretical rollback, the new string for current use
5. New customer-added values (e.g., "Edge Computing") only exist in the string field — enum has no equivalent
6. ProtoMember(3) is the next safe number on `Hosting` class (1,2 are used)

### 2.4 ConfigurableListDefinition Class Design

```csharp
[ProtoContract]
public class ConfigurableListDefinition
{
    [ProtoMember(1)] public string ListId { get; set; }          // e.g., "HostingType", "LifecycleStage"
    [ProtoMember(2)] public string DisplayName { get; set; }     // e.g., "Install Type"
    [ProtoMember(3)] public List<ConfigurableListValue> Values { get; set; } = new();
    [ProtoMember(4)] public string Description { get; set; }
    [ProtoMember(5)] public bool AllowCustomerEdit { get; set; } = true;
    [ProtoMember(6)] public string DefaultValue { get; set; }    // Default for new records
    [ProtoMember(7)] public DateTime ModifiedDate { get; set; }
    [ProtoMember(8)] public string AppliesTo { get; set; }       // FactSheet type(s)
    
    /// <summary>
    /// Gets the display name for a value, handling legacy enum integers
    /// </summary>
    public string GetDisplayName(string storedValue) { ... }
    
    /// <summary>
    /// Validates that a value is in the allowed list
    /// </summary>
    public bool IsValid(string value) { ... }
}

[ProtoContract]
public class ConfigurableListValue
{
    [ProtoMember(1)] public string Value { get; set; }           // The stored/display value
    [ProtoMember(2)] public int? LegacyEnumInt { get; set; }     // Maps to old enum int (null for new values)
    [ProtoMember(3)] public string Description { get; set; }
    [ProtoMember(4)] public int DisplayOrder { get; set; }
    [ProtoMember(5)] public bool IsActive { get; set; } = true;  // Soft delete
    [ProtoMember(6)] public string Color { get; set; }           // Optional color for UI
    [ProtoMember(7)] public string Icon { get; set; }            // Optional icon
}
```

### 2.5 ConfigurableListService

```csharp
public class ConfigurableListService
{
    /// <summary>
    /// Gets all values for a named list, with defaults if not yet configured
    /// </summary>
    public List<string> GetListValues(string listId) { ... }
    
    /// <summary>
    /// Converts a legacy enum integer to the current string value
    /// </summary>
    public string FromLegacyEnum(string listId, int enumValue) { ... }
    
    /// <summary>
    /// Initializes default list definitions (called once on first run / upgrade)
    /// </summary>
    public void InitializeDefaults() { ... }
}
```

---

## 3. Migration Strategy — Per-Enum Plans

### 3.1 HostingType (Hosting.HostingTypeEnum → Configurable)

**Current state:**
```csharp
// Hosting.cs
public enum HostingTypeEnum { Unmapped=0, Desktop=1, Mobile=2, OnPrem=3, Hybrid=4, SaaS=5, PaaS=6, IaaS=7 }

[ProtoMember(1)] public HostingTypeEnum Criticality { get; set; } = HostingTypeEnum.Unmapped;
[ProtoMember(2)] public string HostingTypeDescription { get; set; }
```

**ProtoMember inventory:** Max used = 2. Next safe = **3**.

**Migration:**
```csharp
// Keep existing:
[ProtoMember(1)] public HostingTypeEnum Criticality { get; set; } = HostingTypeEnum.Unmapped;
[ProtoMember(2)] public string HostingTypeDescription { get; set; }

// Add new:
[ProtoMember(3)] public string HostingTypeValue { get; set; }  // NEW configurable string

// Post-deserialize hook:
[ProtoAfterDeserialization]
private void OnDeserialized()
{
    if (string.IsNullOrEmpty(HostingTypeValue) && Criticality != HostingTypeEnum.Unmapped)
        HostingTypeValue = Criticality.ToString();
}
```

**Default list definition:**
```
ListId: "HostingType"
Values: Unmapped(0), Desktop(1), Mobile(2), OnPrem(3), Hybrid(4), SaaS(5), PaaS(6), IaaS(7)
        + ThirdPartyHosted(new), EdgeComputing(new), DistributedApp(new)
```

**UI change:** `OperationalParametersSectionEdit.razor` switches from:
```razor
@foreach (var option in Enum.GetNames(typeof(Hosting.HostingTypeEnum)))
```
to:
```razor
@foreach (var option in ConfigurableListService.GetListValues("HostingType"))
```

**Backwards compatibility proof:**
- Old .bin has `ProtoMember(1) = 5` (SaaS) → deserializes to `Criticality = SaaS` → `OnDeserialized()` sets `HostingTypeValue = "SaaS"` ✅
- New .bin has `ProtoMember(3) = "Edge Computing"` + `ProtoMember(1) = 0` (Unmapped) → `HostingTypeValue = "Edge Computing"` ✅
- Old code reads new .bin → ignores unknown ProtoMember(3), reads ProtoMember(1) = Unmapped → loses new values but doesn't crash ✅

---

### 3.2 CostType (enum → Configurable)

**Current state:**
```csharp
// Cost.cs  
public enum CostType { YearlyLicenseCost = 0, OneOffCapexExpense = 1 }
```

**Important note:** `CostType` is defined as an enum but is **NOT currently used as a ProtoMember** on the `Cost` class! The `Cost` class has `CapExAmount`, `OpExAmount` etc. but no `CostType` field. The enum exists but appears unused in serialization.

**Migration approach:** Since `CostType` is not serialized via ProtoMember, this is the simplest case. We can:
1. Keep the enum for compile compatibility
2. Add a `ConfigurableListDefinition` for "CostType"
3. When we eventually add a CostType field to the Cost class, use a string ProtoMember directly

**Default list definition:**
```
ListId: "CostType"
Values: YearlyLicenseCost(0), OneOffCapexExpense(1)
        + Support(new), Maintenance(new), Hosting(new), FTE-Actual(new), 
          FTE-Required(new), Consumption(new), OPEX-ProfessionalService(new), CAPEX(new)
```

**Backwards compatibility:** No serialized data to migrate — pure addition. ✅

---

### 3.3 Lifecycle Stages (Date-based phases → Configurable stage labels)

**Current state:**
```csharp
// LifeCycle.cs
[ProtoMember(1)] public DateTime Plan { get; set; }
[ProtoMember(2)] public DateTime PhaseIn { get; set; }
[ProtoMember(3)] public DateTime Active { get; set; }
[ProtoMember(4)] public DateTime PhaseOut { get; set; }
[ProtoMember(5)] public DateTime EndOfLife { get; set; }
```

**This is fundamentally different from the others.** LifeCycle is NOT an enum — it's 5 DateTime fields. The "lifecycle stage" is computed from which dates have passed. Kamstrup's model uses explicit stage labels (Strategic, Important, etc.) that don't correspond to date ranges.

**The challenge:** LifeCycle dates are deeply embedded:
- `GetLifeCycleIndex()` computes current phase from dates
- `GetColor()` uses the index for visual coding
- `ToString()` returns "Not Planned", "Planning", "Active", "Phasing Out", "End of Life"

**Migration approach — Hybrid:**

1. **Keep all 5 date fields** — they work perfectly for date-based lifecycle tracking
2. **Add `LifecycleStage` string field** on the `FactSheet` base class (ProtoMember 45) — this is the configurable label
3. **The configurable list** provides stage names; each stage can optionally map to a LifeCycle phase for color/computation
4. **On load from old data:** If `LifecycleStage` is null, compute it from `LifeCycle.ToString()` 

```csharp
// On FactSheet base class:
[ProtoMember(45)] public string LifecycleStage { get; set; }  // NEW: configurable stage label

// Post-load migration:
if (string.IsNullOrEmpty(LifecycleStage))
    LifecycleStage = LifeCycle?.ToString() ?? "Not Planned";
```

**Default list definition (OmniGaze default):**
```
ListId: "LifecycleStage"
Values: Not Planned, Planning, Active, Phasing Out, End of Life, Obsolete
```

**Kamstrup list definition:**
```
ListId: "LifecycleStage"  
Values: Under Evaluation, 1-Strategic, 2-Important, 3-Kamstrup Application, 
        4-Saved for now, 5-Investigate, 7-Potential for Phase Out, 
        8-Phase Out, 8-Kamstrup App Phase Out, 9-End of Life, Not in use
```

**ConfigurableListValue extension for lifecycle:**
Each value can have an optional `PhaseMapping` that maps to the date-based phase for color/computation:
```csharp
[ProtoMember(8)] public string PhaseMapping { get; set; }  // "Plan", "Active", "PhaseOut", "EndOfLife"
```

This lets Kamstrup's "1-Strategic" map to the "Active" phase for green color coding, while "7-Potential for Phase Out" maps to "PhaseOut" for yellow.

**Backwards compatibility proof:**
- Old .bin has no ProtoMember(45) → `LifecycleStage = null` → post-load sets it from `LifeCycle.ToString()` ✅
- Old .bin dates still work → `GetLifeCycleIndex()` still functional for color coding ✅
- New .bin with stage="2-Important" → UI shows "2-Important", color derived from PhaseMapping→Active=green ✅

---

### 3.4 ITComponentType (Already a string! Simplest case)

**Current state:**
```csharp
// ITComponentFactSheet.cs
[ProtoMember(1)] public string ITComponentType { get; set; } = "Server";
```

**This is already a string ProtoMember!** No dual-field migration needed.

**Migration:** Simply add a `ConfigurableListDefinition` to control the dropdown values:

```
ListId: "ITComponentType"
Values: Server (default), Switch, Router, Storage, Firewall, Load Balancer, 
        Platform, Suite, Programming Language, Phase Out
```

**UI change:** `ITComponentsPage.razor` already uses a text input — switch to dropdown from configurable list.

**Backwards compatibility:** Trivially safe — no schema change at all. ✅

---

### 3.5 EditingState (New field — no legacy data)

**Current state:** Does not exist in codebase.

**Migration:** This was already planned as a new ProtoMember on `ProcessFactSheet` (PM 54 per the master plan).

Since there's no legacy data, we implement it as a string field from day one:

```csharp
// ProcessFactSheet.cs
[ProtoMember(54)] public string EditingState { get; set; }  // Configurable list values
```

**Default list definition:**
```
ListId: "EditingState"
Values: Current, Draft, Pending Approval, Review, N/A
```

**Backwards compatibility:** No old data exists — pure addition. ✅

---

## 4. Backwards Compatibility Verification Matrix

| Scenario | HostingType | CostType | LifecycleStage | ITComponentType | EditingState |
|----------|------------|----------|----------------|-----------------|-------------|
| Old .bin → New code | ✅ Enum→string via `OnDeserialized` | ✅ Not serialized | ✅ null→computed from dates | ✅ Already string | ✅ N/A (new) |
| New .bin → New code | ✅ Reads string field | ✅ Reads string field | ✅ Reads string field | ✅ Reads string field | ✅ Reads string field |
| New .bin → Old code (rollback) | ⚠️ String field ignored, enum=Unmapped for new values | ✅ No impact | ⚠️ String field ignored, dates still work | ✅ Still a string | ⚠️ Field ignored (PM 54 unknown) |
| Custom value added | ✅ Stored as string | ✅ Stored as string | ✅ Stored as string | ✅ Stored as string | ✅ Stored as string |
| Customer upgrades | ✅ Auto-migrate on first load | ✅ No migration | ✅ Auto-migrate on first load | ✅ No migration | ✅ No migration |

**Rollback risk (New .bin → Old code):**
- HostingType: Apps with new hosting values (e.g., "Edge Computing") will show as "Unmapped" in old code. The legacy enum field gets Unmapped for values without enum equivalents. **Data is not lost** — the string field remains in the .bin (old code ignores unknown ProtoMembers, protobuf-net skips them).
- LifecycleStage: Stage label is lost on rollback, but dates remain intact. Acceptable.
- If the old code re-saves, the string fields are **preserved** because protobuf-net's default behavior retains unknown fields during round-trip (when using `RuntimeTypeModel` default settings). However, this should be verified by test.

---

## 5. UI Design for List Configuration

### 5.1 Admin Settings Page

Location: **Settings → Configurable Lists** (new tab/section in the existing admin area)

```
┌──────────────────────────────────────────────────────────┐
│ ⚙ Configurable Lists                                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ ┌─ Hosting Type ─────────────────────────────────┐       │
│ │ Applies to: Application                        │       │
│ │                                                │       │
│ │  ☰ Unmapped          [🔒 Built-in]            │       │
│ │  ☰ Desktop           [🔒 Built-in]            │       │
│ │  ☰ Mobile            [🔒 Built-in]            │       │
│ │  ☰ OnPrem            [🔒 Built-in]            │       │
│ │  ☰ Hybrid            [🔒 Built-in]            │       │
│ │  ☰ SaaS              [🔒 Built-in]            │       │
│ │  ☰ PaaS              [🔒 Built-in]            │       │
│ │  ☰ IaaS              [🔒 Built-in]            │       │
│ │  ☰ Edge Computing    [✏️ Custom]  [🗑️]       │       │
│ │  ☰ Third Party       [✏️ Custom]  [🗑️]       │       │
│ │                                                │       │
│ │  [+ Add Value]                                 │       │
│ └────────────────────────────────────────────────┘       │
│                                                          │
│ ┌─ Lifecycle Stage ──────────────────────────────┐       │
│ │ Applies to: All FactSheets                     │       │
│ │                                                │       │
│ │  ☰ Not Planned  → Phase: None     [🔒]        │       │
│ │  ☰ Planning     → Phase: Plan     [🔒]        │       │
│ │  ☰ Active       → Phase: Active   [🔒]        │       │
│ │  ☰ Phasing Out  → Phase: PhaseOut [🔒]        │       │
│ │  ☰ End of Life  → Phase: EndOfLife[🔒]        │       │
│ │  ☰ Strategic    → Phase: Active   [✏️] [🗑️]  │       │
│ │  ☰ Important    → Phase: Active   [✏️] [🗑️]  │       │
│ │                                                │       │
│ │  [+ Add Value]                                 │       │
│ └────────────────────────────────────────────────┘       │
│                                                          │
│ ┌─ Cost Type ────────────────────────────────────┐       │
│ │  ☰ Yearly License Cost   [🔒]                 │       │
│ │  ☰ One-Off CapEx         [🔒]                 │       │
│ │  ☰ Support               [✏️] [🗑️]           │       │
│ │  ☰ Maintenance           [✏️] [🗑️]           │       │
│ │  ...                                           │       │
│ │  [+ Add Value]                                 │       │
│ └────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────┘
```

**Key UI features:**
- ☰ Drag handles for reordering
- 🔒 Built-in values cannot be deleted (they map to legacy enum ints), but can be renamed
- ✏️ Custom values can be edited and deleted
- Deletion is soft (marks inactive) — values already in use show a warning
- Phase mapping dropdown for lifecycle stages (determines color coding)

### 5.2 FactSheet Form Dropdowns

Replace `Enum.GetNames(typeof(...))` loops with:

```razor
@inject ConfigurableListService ListService

<select class="form-control" @bind="Application.HostedOn.HostingTypeValue">
    @foreach (var option in ListService.GetListValues("HostingType"))
    {
        <option value="@option">@option</option>
    }
</select>
```

### 5.3 Grid Filters

`StandardGrid2` already supports custom columns with filtering. For configurable list columns:
- Filter type: Dropdown (multi-select checkboxes)
- Values populated from `ConfigurableListService.GetListValues(listId)`
- Grouping works on string values (already supported)

---

## 6. Impact on Kamstrup Implementation Phases

### Recommendation: **Phase 0** (Before Phase 1)

Configurable lists should be implemented **before** the model foundation phase because:

1. **Phase 1 (Model Foundation)** currently plans to add enum values to `HostingTypeEnum` and create new enums like `EditingStateEnum`. With configurable lists, we instead add list definitions — cleaner approach.
2. **Phase 3 (Application Import)** needs lifecycle stage mapping. With configurable lists, the import script writes stage strings directly instead of lossy enum mapping.
3. Doing it first means all subsequent phases use the new system consistently.

### Revised Phase Plan

| Phase | Name | Change from Original |
|-------|------|---------------------|
| **0** | **Configurable Lists Infrastructure** | **NEW** — 2 days |
| 1 | Model Foundation | Simplified: no new enum definitions, use configurable lists instead |
| 2-6 | Unchanged | Import scripts write string values |

### Phase 0 Detailed Tasks

| Task | Effort | Description |
|------|--------|-------------|
| 0.1 | 2h | Create `ConfigurableListDefinition` and `ConfigurableListValue` classes |
| 0.2 | 2h | Create `ConfigurableListService` with defaults initialization |
| 0.3 | 1h | Add `ConfigurableListDefinitions` list to `CustomerSettings` (ProtoMember 34) |
| 0.4 | 2h | Migrate `Hosting.cs`: add `HostingTypeValue` (PM 3) + `[ProtoAfterDeserialization]` |
| 0.5 | 1h | Add `LifecycleStage` string to `FactSheet` base (PM 45) + post-load hook |
| 0.6 | 0.5h | `ProcessFactSheet`: add `EditingState` as string (PM 54) |
| 0.7 | 0.5h | `ITComponentType`: just add list definition (already a string) |
| 0.8 | 0.5h | `CostType`: add list definition (no schema change needed yet) |
| 0.9 | 3h | Create Admin UI: `ConfigurableListsAdmin.razor` settings page |
| 0.10 | 2h | Update `OperationalParametersSectionEdit.razor` — hosting dropdown |
| 0.11 | 1h | Update `ITComponentsPage.razor` — component type dropdown |
| 0.12 | 1h | Build + test + backwards compat verification |
| 0.13 | 0.5h | Git commit: `feat: Phase 0 — Configurable lists infrastructure` |
| **Total** | **~2 days** | |

### Phase 1 Changes (with Configurable Lists)

Remove from Phase 1:
- ~~1.2 Create 4 new enums~~ → EditingState is now a configurable list string field
- ~~1.3 Add enum values to existing enums~~ → HostingType values are configurable list entries

Add to Phase 1 instead:
- 1.2a Add Kamstrup-specific values to configurable lists (HostingType, LifecycleStage, CostType, etc.)
- 1.5 ProcessFactSheet.EditingState already added in Phase 0 as string field

---

## 7. Implementation Checklist

### Phase 0.1: Core Infrastructure
- [x] Create `F:\...\Model\EnterpriseArchitecture\ConfigurableListDefinition.cs` ✅ 2026-02-07
- [x] Create `F:\...\Model\EnterpriseArchitecture\ConfigurableListValue.cs` ✅ 2026-02-07
- [x] Create `F:\...\Services\ConfigurableListService.cs` ✅ 2026-02-07
- [x] Add `[ProtoMember(34)] public List<ConfigurableListDefinition> ConfigurableListDefinitions` to `CustomerSettings` ✅ 2026-02-07
- [x] Implement `InitializeDefaults()` — seeds 5 lists with built-in values matching current enums ✅ 2026-02-07
- [ ] Write unit test: defaults initialization creates correct values ⚠️ (blocked: OmniGaze.exe locks DLLs, need to stop running instance first)

### Phase 0.2: Hosting Type Migration
- [x] Add `[ProtoMember(3)] public string HostingTypeValue` to `Hosting.cs` ✅ 2026-02-07
- [x] Add `[ProtoAfterDeserialization]` migration hook on `Hosting` ✅ 2026-02-07
- [x] Update `OperationalParametersSectionEdit.razor` — use `ConfigurableListService` ✅ 2026-02-07
- [x] Update `OperationalParametersSectionDisplay.razor` — display `HostingTypeValue` ✅ 2026-02-07
- [ ] Update any grid columns that display hosting type (deferred to Phase 1 grid integration)
- [ ] Write unit test: old .bin with enum int → correct string after load ⚠️ (blocked: file locks)

### Phase 0.3: Lifecycle Stage Migration
- [x] Add `[ProtoMember(45)] public string LifecycleStage` to `FactSheet` base class ✅ 2026-02-07
- [ ] Add post-deserialization migration in `FactSheet` or `FactSheetContainer.Load()` (deferred: needs careful testing)
- [ ] Update lifecycle display components to show `LifecycleStage` string (deferred to Phase 1)
- [x] Keep `LifeCycle` date fields intact (they serve a different purpose — date-based phase) ✅ verified
- [ ] Write unit test: old .bin with only dates → stage computed correctly ⚠️ (blocked: file locks)

### Phase 0.4: Simple String Fields
- [x] `ProcessFactSheet`: add `[ProtoMember(53)] public string EditingState` (new, no migration) ✅ 2026-02-07 (NOTE: PM 53, not 54 — PM 52 was last used)
- [x] `ITComponentType`: already string — add configurable list definition only ✅ 2026-02-07
- [x] `CostType`: add configurable list definition only (no schema change yet) ✅ 2026-02-07

### Phase 0.5: Admin UI
- [x] Create `ConfigurableListsPage.razor` admin page ✅ 2026-02-07
- [ ] Implement drag-to-reorder (display order) — partial: uses up/down buttons, not drag
- [x] Implement add/edit/soft-delete value ✅ 2026-02-07
- [x] Built-in values: show lock icon, prevent deletion, allow rename ✅ 2026-02-07
- [x] Lifecycle stage: show phase mapping dropdown per value ✅ 2026-02-07
- [x] Save to CustomerSettings on changes ✅ 2026-02-07
- [x] Add navigation link in Settings section ✅ 2026-02-07

### Phase 0.6: Verification
- [x] Build solution — `dotnet build` ✅ Zero CS compilation errors (MSB file lock warnings only because OmniGaze.exe running)
- [ ] Run tests — `dotnet test` ⚠️ Blocked: OmniGaze.exe (PID 2660) locks DLLs, cannot copy to output. Need to stop OmniGaze.exe first.
- [ ] Load existing production .bin — verify no data loss (manual test needed)
- [ ] Round-trip test: load old .bin → save → reload → verify (manual test needed)
- [ ] Create new app with custom hosting type → save → reload → verify (manual test needed)
- [x] Git commit: `feat: Phase 0 — Configurable lists infrastructure` ✅ Commit c969568
- [ ] **JANE CHECKPOINT:** Settings page shows configurable lists. Add a custom hosting type. Create an app with the custom type. Reload — custom type persists.

---

## 8. Technical Details

### 8.1 ProtoMember Numbers Used

| Class | Field | ProtoMember | Status |
|-------|-------|-------------|--------|
| `CustomerSettings` | `ConfigurableListDefinitions` | **34** | New |
| `Hosting` | `HostingTypeValue` | **3** | New |
| `FactSheet` (base) | `LifecycleStage` | **45** | New |
| `ProcessFactSheet` | `EditingState` | **53** | New (PM 52 was last used, so 53 is correct) |

All verified against the proto compatibility guide — no conflicts.

### 8.2 Default List Definitions (Seeded on First Run)

**HostingType:**
| Value | LegacyEnumInt | DisplayOrder |
|-------|--------------|-------------|
| Unmapped | 0 | 0 |
| Desktop | 1 | 10 |
| Mobile | 2 | 20 |
| OnPrem | 3 | 30 |
| Hybrid | 4 | 40 |
| SaaS | 5 | 50 |
| PaaS | 6 | 60 |
| IaaS | 7 | 70 |

**LifecycleStage (OmniGaze default):**
| Value | PhaseMapping | DisplayOrder |
|-------|-------------|-------------|
| Not Planned | None | 0 |
| Planning | Plan | 10 |
| Active | Active | 20 |
| Phasing Out | PhaseOut | 30 |
| End of Life | EndOfLife | 40 |
| Obsolete | EndOfLife | 50 |

**CostType:**
| Value | LegacyEnumInt | DisplayOrder |
|-------|--------------|-------------|
| Yearly License Cost | 0 | 0 |
| One-Off CapEx Expense | 1 | 10 |

**ITComponentType:**
| Value | DisplayOrder |
|-------|-------------|
| Server | 0 |
| Switch | 10 |
| Router | 20 |
| Storage | 30 |
| Firewall | 40 |
| Load Balancer | 50 |

**EditingState:**
| Value | DisplayOrder |
|-------|-------------|
| Current | 0 |
| Draft | 10 |
| Pending Approval | 20 |
| Review | 30 |
| N/A | 40 |

### 8.3 Migration Flow on Application Startup

```
Application.Start()
  → CustomerSettings.Load()
    → Check ConfigurableListDefinitions
    → If empty/null: call ConfigurableListService.InitializeDefaults()
      → Creates 5 list definitions with built-in values
      → Save CustomerSettings
  
  → FactSheetContainer.Load()
    → Protobuf deserializes all factsheets
    → For each ApplicationFactSheet:
      → Hosting.OnDeserialized() runs
      → If HostingTypeValue is null && Criticality != Unmapped:
        → HostingTypeValue = Criticality.ToString()
    → For each FactSheet:
      → If LifecycleStage is null:
        → LifecycleStage = LifeCycle.ToString()
    → Migration complete, no explicit save needed (lazy — saves on next user action)
```

### 8.4 Relationship to Existing CustomColumnDefinition System

These are **separate systems** by design:

| Aspect | CustomColumnDefinition | ConfigurableListDefinition |
|--------|----------------------|---------------------------|
| Purpose | Add entirely new columns to grids | Replace existing hardcoded enums |
| Storage | Values in `FactSheet.CustomFields` (string key-value) | Values in dedicated ProtoMember fields |
| Schema | Dynamic (Guid-keyed) | Typed (named string fields) |
| UI | Auto-registered grid columns | Bound to existing form controls |
| Performance | Dictionary lookup per field | Direct property access |

We keep them separate because configurable lists replace core model properties with defined semantics (lifecycle affects colors, hosting affects categorization), while custom columns are genuinely extensible extra data.

---

## 9. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| protobuf-net drops unknown fields on round-trip | Low | High | Test explicitly; configure `RuntimeTypeModel` if needed |
| Customer deletes a built-in value | N/A | N/A | UI prevents deletion of built-in values (🔒) |
| Customer renames a built-in value | Low | Medium | Rename updates the display; stored value stays consistent |
| Performance of string vs enum comparison | Very Low | Low | String comparisons are fast; grid filtering already uses strings |
| Lifecycle color coding breaks | Medium | Low | PhaseMapping on each list value provides the color mapping |

---

*This design enables customer-specific terminology while preserving all existing data. The dual-field approach is proven in protobuf schema evolution and matches patterns already used in the OmniGaze codebase (e.g., ApplicationType enum → ApplicationTypeTags migration on ApplicationFactSheet).*

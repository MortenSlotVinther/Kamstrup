# Protobuf-net Backwards Compatibility Guide — OmniGaze

**Date:** 2026-02-06  
**Author:** Ole (AI Assistant)  
**Purpose:** Ensure zero breaking changes when adding OrganizationFactSheet, new fields, and new enums to the OmniGaze protobuf schema.

---

## 1. Current Schema Inventory

### 1.1 FactSheet Base Class — ProtoInclude Numbers

The base `FactSheet` class (abstract) uses `ProtoInclude` to register all derived types. These numbers are in the **500-517** range:

| ProtoInclude # | Type | Status |
|---|---|---|
| 500 | ApplicationFactSheet | ✅ Active |
| 501 | DataObjectFactSheet | ✅ Active |
| 502 | ProjectFactSheet | ✅ Active |
| 503 | ITComponentFactSheet | ✅ Active |
| 504 | ProviderFactSheet | ✅ Active |
| 505 | TechCategoryFactSheet | ✅ Active |
| 506 | UserGroupFactSheet | ✅ Active |
| 507 | BusinessCapabilityFactSheet | ✅ Active |
| 508 | ProcessFactSheet | ✅ Active |
| 509 | InterfaceFactSheet | ✅ Active |
| 510 | ObjectiveFactSheet | ✅ Active |
| 511 | ServerFactSheet | ✅ Active |
| 512 | SQLInstanceFactSheet | ✅ Active |
| 513 | DatabaseFactSheet | ✅ Active |
| 514 | StakeholderFactSheet | ✅ Active |
| 515 | ModuleFactSheet | ✅ Active |
| 516 | ValueStreamFactSheet | ✅ Active |
| 517 | ValueChainFactSheet | ✅ Active |

> **Next safe ProtoInclude: 518** (for OrganizationFactSheet)

**Note:** `WindowsProcessFactSheet` extends `ITComponentFactSheet` (not `FactSheet` directly), so it does NOT need a ProtoInclude on the base. Similarly, `WebServerFactSheet` extends `ServerFactSheet`. Neither has its own ProtoInclude on the base class.

### 1.2 FactSheetContainer — ProtoMember Numbers

`FactSheetContainer` holds a `List<T>` for each factsheet type:

| ProtoMember # | Property | Type |
|---|---|---|
| 1 | ApplicationFactSheets | List\<ApplicationFactSheet\> |
| 2 | DataObjectFactSheets | List\<DataObjectFactSheet\> |
| 3 | ProjectFactSheets | List\<ProjectFactSheet\> |
| 4 | ITComponentFactSheets | List\<ITComponentFactSheet\> |
| 5 | ProviderFactSheets | List\<ProviderFactSheet\> |
| 6 | TechCategoryFactSheets | List\<TechCategoryFactSheet\> |
| 7 | UserGroupFactSheets | List\<UserGroupFactSheet\> |
| 8 | BusinessCapabilityFactSheets | List\<BusinessCapabilityFactSheet\> |
| 9 | ProcessFactSheets | List\<ProcessFactSheet\> |
| 10 | InterfaceFactSheets | List\<InterfaceFactSheet\> |
| 11 | ObjectiveFactSheets | List\<ObjectiveFactSheet\> |
| 12 | SQLInstanceFactSheets | List\<SQLInstanceFactSheet\> |
| 13 | ServerFactSheets | List\<ServerFactSheet\> |
| 14 | DatabaseFactSheets | List\<DatabaseFactSheet\> |
| 15 | StakeholderFactSheets | List\<StakeholderFactSheet\> |
| 16 | ModuleFactSheets | List\<ModuleFactSheet\> |
| 17 | ValueStreamFactSheets | List\<ValueStreamFactSheet\> |
| 18 | ValueChainFactSheets | List\<ValueChainFactSheet\> |

> **Next safe ProtoMember: 19** (for OrganizationFactSheets list)

### 1.3 FactSheet Base Class — ProtoMember Numbers

The abstract `FactSheet` base class has these field numbers:

| # | Field | Notes |
|---|---|---|
| 1 | DisplayName | |
| 2 | ParentFactSheetsIds | |
| — | *3 is unused/skipped* | Gap — **DO NOT reuse** |
| 4 | Id | |
| 5 | Concerns | List\<FactSheetConcern\> |
| 6 | LifeCycle | |
| — | *7 is unused/skipped* | Gap — **DO NOT reuse** |
| 8 | Responsible | |
| 9 | ResponsibleMail | |
| 10 | PortFolioStrategy | |
| 11 | Gartner6RStrategy | |
| 12 | BusinessSupport | |
| — | *13 commented out* | Was Comments — **DO NOT reuse** |
| 14 | RichDescription | |
| 15 | HierarchyChildrenIds | ObservableCollection\<Guid\> |
| 16 | LeanIXId | |
| 17 | FunctionalFit | enum |
| 18 | FunctionalFitDescription | |
| — | *19 is unused/skipped* | Gap — **DO NOT reuse** |
| 20 | ContributorGuids | |
| 21 | ResponsibleTeamGuid | |
| 22 | SuccessorId | |
| 23 | Cost | |
| 24 | Retired | |
| — | *25 is unused/skipped* | Gap — **DO NOT reuse** |
| 26 | CurrentMaturity | |
| 27 | TargetMaturity | |
| — | *28 commented out* | Was Contributors — **DO NOT reuse** |
| 29 | LastChanged | |
| 30 | AccessHandler | |
| 31 | MaturityControls | |
| 32 | CurrentMaturityDescription | |
| 33 | TargetMaturityDescription | |
| 34 | CreatedBy | |
| 35 | CreatedDateTime | |
| 36 | ModifiedBy | |
| 37 | ModifiedDateTime | |
| 38 | Url | |
| 39 | Urls | LinkList |
| 40 | CreationMetadata | |
| 41 | Owners | List\<OwnerAssignment\> |
| 42 | CustomFields | List\<CustomFieldValue\> |
| 43 | OrganizationTags | List\<string\> |
| 44 | ShortDescription | |

> **Next safe ProtoMember on base FactSheet: 45**

### 1.4 Derived FactSheet Types — ProtoMember Numbers

#### ApplicationFactSheet (extends FactSheet)
| # | Field | Notes |
|---|---|---|
| 1 | TechnicalFit | |
| — | *2 unused* | Gap |
| 3 | HostedOn | Hosting |
| 4 | LinkedProcessNames | |
| 5 | ApplicationExecutableLinks | |
| 6 | Category | |
| 7 | DisasterSLA | |
| 8 | InternallyDeveloped | |
| 9 | RequiresLicense | |
| 10 | DatabaseLinks | |
| 11 | CloudResourceLinks | |
| — | *12 unused* | Gap |
| 13 | QA | |
| 14 | IsBusinessApplication | |
| 15-20 | Support fields | Provider, Model, Hours, Email, Phone, Documentation |
| 50-51 | Value stream/chain refs | |
| — | *52 unused* | |
| 53 | ApplicationType | enum (legacy) |
| 54 | SecurityAssessment | |
| 55 | AIClassification | |
| 56 | PlatformTags | |
| 57 | UserBase | |
| 58 | ApplicationTypeTags | |

> **Max used: 58. Next safe: 59** (or any unused number in gaps, but safest is 59+)

#### BusinessCapabilityFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1 | ValueChains |
| 2 | ComplianceControls |
| 3 | RiskAssessments |
| 4 | KPIs |
| 5 | CapabilityType |
| 40 | SupportedValueStreamIds |
| 41 | EnabledValueChainActivityIds |
| 42 | MaturityRequirements |
| 100 | _level (private) |

> **Max used: 100. Next safe: 101** (but 6-39, 43-99 are technically available — stick to sequential after last used block)

#### ITComponentFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1-11 | ITComponentType through ContractType |

> **Max used: 11. Next safe: 12**

#### ServerFactSheet (extends ITComponentFactSheet)
| # | Field |
|---|---|
| 1 | Hostname |

> **⚠️ Number conflict!** ServerFactSheet uses ProtoMember(1) which is also used by ITComponentFactSheet.ITComponentType. This works because protobuf-net scopes ProtoMember numbers per declared type in the hierarchy — each level gets its own numbering namespace. **BUT this is subtle and easy to confuse.**

#### InterfaceFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 3-17 | Various fields (3-5, 7-17) |

> **Max used: 17. Next safe: 18** (note: 1, 2, 6 are gaps)

#### ProcessFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 51 | Frequency |
| 52 | DurationInHours |

> **Starts at 51 — likely to avoid collision with base class numbers (unnecessary since derived types get their own namespace, but harmless). Next safe: 53**

#### ProviderFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1 | Evaluation |
| 2 | ProviderType |
| 3 | ContractEndDate |

> **Max used: 3. Next safe: 4**

#### DataObjectFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1-6 | Various fields |

> **Max used: 6. Next safe: 7**

#### ModuleFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1-8 | ModuleType through SupportDocumentation |

> **Max used: 8. Next safe: 9**

#### StakeholderFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1 | Mail |

> **Max used: 1. Next safe: 2**

#### SQLInstanceFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1 | sqlInstanceId |

> **Max used: 1. Next safe: 2**

#### ValueStreamFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1-4 | Steps, CostPerUnit, DefectRate, CustomerSatisfaction |
| 20-22 | RelatedValueChainIds, EnabledByApplicationIds, SupportedByCapabilityIds |

> **Max used: 22. Next safe: 23** (5-19 are gaps)

#### ValueChainFactSheet (extends FactSheet)
| # | Field |
|---|---|
| 1-7 | Various fields |

> **Max used: 7. Next safe: 8**

#### Types with NO derived ProtoMembers:
- ProjectFactSheet — no own fields
- TechCategoryFactSheet — no own fields
- UserGroupFactSheet — no own fields
- ObjectiveFactSheet — no own fields
- DatabaseFactSheet — no own fields
- WindowsProcessFactSheet — no own fields
- WebServerFactSheet — no own fields

### 1.5 Key Supporting Types — ProtoMember Numbers

| Type | Max ProtoMember | Next Safe |
|---|---|---|
| FactSheetConcern | 8 | 9 |
| FactSheetCreationMetadata | 5 | 6 |
| OwnerAssignment | 6 | 7 |
| CustomFieldValue | 4 | 5 |
| FactSheetMaturityControl | 11 | 12 |
| Hosting | 2 | 3 |
| AIClassification | 5 | 6 |
| SecurityAssessment | 5 | 6 |
| UserBase | 4 | 5 |
| Cost | 7 | 8 |
| QualityAssurance | 9 | 10 |
| ProviderEvaluation | 4 | 5 |
| ValueStreamStep | 17 | 18 |
| ValueChainActivity | 14 | 15 |
| ValueStreamStepReference | 4 | 5 |
| Link | 3 | 4 |
| LinkList | 1 | 2 |

---

## 2. Rules for Safe Additions (Do's and Don'ts)

### ✅ DO — Safe Operations

1. **Add new ProtoMember fields with NEW numbers**
   - Use the next available number (never reuse retired/commented-out numbers)
   - Old .bin files will deserialize with new fields as `default(T)` (null for reference types, 0 for value types, empty for collections)
   - **This is the core protobuf guarantee**

2. **Add new ProtoInclude types**
   - Old .bin won't contain data for the new subtype
   - protobuf-net simply won't encounter the field tag for the new type, so it's safely skipped
   - The new list in FactSheetContainer will deserialize as empty (`new List<T>()` from the initializer)

3. **Add new enum values at the END**
   - Protobuf serializes enums as their **integer value**, not their name
   - New enum values with new integer values are safe — old data won't contain them
   - Old data will still deserialize to the correct existing enum values

4. **Add new ProtoContract types** (for nested objects)
   - If a field references a new `[ProtoContract]` type and old data doesn't have it, the field deserializes as `null`
   - Initialize with `= new T()` in the property declaration to get a default instance if desired

5. **Rename enum value names**
   - Protobuf uses the integer, not the name
   - `Unmapped = 0` → `NotSpecified = 0` is **safe** for serialization
   - **But:** code referencing the old name will break at compile time — this is a code change, not a data change

6. **Add new properties WITHOUT ProtoMember**
   - Non-serialized properties (computed, display-only) can be added freely
   - They won't affect the binary format at all

### ❌ DON'T — Breaking Operations

1. **NEVER reuse a ProtoMember number**
   - Even if the old field is deleted/commented out, the number is BURNED
   - Old .bin files may contain data at that field number with a different type → **deserialization crash**
   - Example: `[ProtoMember(13)]` (Comments) and `[ProtoMember(28)]` (Contributors) in FactSheet are commented out — those numbers are FOREVER reserved

2. **NEVER change the type of an existing ProtoMember**
   - Changing `string` → `int` or `List<string>` → `List<int>` on an existing number → **crash**

3. **NEVER renumber existing ProtoMember fields**
   - Moving `[ProtoMember(5)]` to `[ProtoMember(50)]` changes the wire format → **data loss**

4. **NEVER change enum integer values**
   - Changing `Unmapped = 0` to `Unmapped = 5` → all old data with value 0 now maps to wrong enum

5. **NEVER remove ProtoInclude entries**
   - If old .bin contains data for ProtoInclude(511, ServerFactSheet) and you remove it → **crash**

6. **NEVER change inheritance hierarchy of serialized types**
   - Moving a type from one base class to another changes the wire nesting

7. **NEVER change ProtoMember on a base class field that derived types depend on**

### ⚠️ CAUTION — Requires Care

1. **Changing default values of existing fields**
   - If old data was saved with `default`, changing the code default won't retroactively change old data
   - New fields with `= new List<T>()` are fine — the initializer runs after deserialization only if the field wasn't in the .bin

2. **Collection initialization patterns**
   - `List<T>` initialized in declaration: if the .bin has data for that field, the deserialized list **replaces** the initialized one
   - If the .bin has NO data for that field, the initializer value is kept
   - This is the correct behavior for additive changes

---

## 3. Specific Plan for Each Planned Change

### 3.1 Adding OrganizationFactSheet

**Step 1: Create the class**
```csharp
[ProtoContract]
public class OrganizationFactSheet : FactSheet
{
    // Use ProtoMember starting at 1 (own namespace, doesn't conflict with base)
    [ProtoMember(1)] public string OrgType { get; set; }
    [ProtoMember(2)] public string IndustryCode { get; set; }
    // ... etc.
}
```

**Step 2: Register in FactSheet base class**
```csharp
// Add after the last ProtoInclude (517 = ValueChainFactSheet)
[ProtoInclude(518, typeof(OrganizationFactSheet))]
```

**Step 3: Add list to FactSheetContainer**
```csharp
// Add after ProtoMember(18) = ValueChainFactSheets
[ProtoMember(19)] public List<OrganizationFactSheet> OrganizationFactSheets { get; set; } = new List<OrganizationFactSheet>();
```

**Step 4: Update all switch/if-else chains in FactSheetContainer**
- `RemoveFactSheet()` — add `else if (sheet is OrganizationFactSheet)`
- `AllFactSheets` — add `.Concat(OrganizationFactSheets)`
- `AddIfNotExists()` — add case
- `GetFactSheetsByType<T>()` — add case
- `DeleteFactSheet()` — should work via AllFactSheets already

**Step 5: Update FactSheet base class**
- Add `OrganizationFactSheet` to `_factSheetCollections` dictionary if hierarchy is needed
- Update `HierarchyParentId` if applicable

**Backwards compatibility impact: NONE** — Old .bin files won't have ProtoInclude 518 data or ProtoMember 19 data. Both will default to empty/null.

### 3.2 Adding New Fields to Existing FactSheets

Example: Adding PaceLayer to ApplicationFactSheet

```csharp
// In ApplicationFactSheet — next safe number is 59
[ProtoMember(59)]
public PaceLayerEnum PaceLayer { get; set; } = PaceLayerEnum.Unspecified;
```

**Backwards compatibility impact: NONE** — Old .bin won't have field 59. It deserializes as `PaceLayerEnum.Unspecified` (value 0, the default).

### 3.3 Adding New Enum Values

Example: Adding to `HostingTypeEnum`

**Current:**
```csharp
public enum HostingTypeEnum
{ Unmapped, Desktop, Mobile, OnPrem, Hybrid, SaaS, PaaS, IaaS }
// Values: 0, 1, 2, 3, 4, 5, 6, 7
```

**Adding new values — SAFE:**
```csharp
public enum HostingTypeEnum
{ Unmapped, Desktop, Mobile, OnPrem, Hybrid, SaaS, PaaS, IaaS, 
  Containerized, Serverless }
// Values: 0-7 unchanged, new: 8, 9
```

**Backwards compatibility impact: NONE** — Old .bin data only contains values 0-7, which still map correctly.

### 3.4 Adding New ProtoContract Types for Complex Fields

Example: Adding a new `NIS2Compliance` type as a property

```csharp
[ProtoContract]
public class NIS2Compliance
{
    [ProtoMember(1)] public bool IsInScope { get; set; }
    [ProtoMember(2)] public string Classification { get; set; }
    [ProtoMember(3)] public DateTime? LastAssessment { get; set; }
}

// In the relevant FactSheet (e.g., OrganizationFactSheet):
[ProtoMember(3)] public NIS2Compliance NIS2 { get; set; } = new NIS2Compliance();
```

**Backwards compatibility impact: NONE** — Old .bin won't have this field. The property initializer provides the default.

---

## 4. Risk Assessment

### 4.1 Low Risk (Safe)
| Change | Risk | Why |
|---|---|---|
| New FactSheet type | ✅ None | Additive ProtoInclude + new list |
| New fields on existing types | ✅ None | New ProtoMember numbers default to zero/null |
| New enum values (appended) | ✅ None | Old data retains valid integer mappings |
| New nested ProtoContract types | ✅ None | Null/default when absent |

### 4.2 Medium Risk (Needs Testing)
| Change | Risk | Why |
|---|---|---|
| Adding fields to the base `FactSheet` class | ⚠️ Low-Medium | All 18+ derived types inherit this; must verify no ProtoMember number collision between base (which goes up to 44) and derived types. **Note: protobuf-net numbers are scoped per declared type, NOT accumulated, so base 44 and derived 1 are independent.** But test anyway. |

### 4.3 High Risk (Avoid)
| Change | Risk | Why |
|---|---|---|
| Reusing any ProtoMember/ProtoInclude number | 🔴 Critical | Data corruption, crashes |
| Changing enum integer assignments | 🔴 Critical | All existing data maps to wrong values |
| Removing types from ProtoInclude | 🔴 Critical | Existing data can't deserialize |

### 4.4 Forward Compatibility Concern

**Scenario:** New version saves data with OrganizationFactSheet entries → old version loads the .bin.

**What happens:**
- protobuf-net encounters field tag 19 in FactSheetContainer but doesn't know about it
- **By default, protobuf-net SILENTLY SKIPS unknown fields** ← This is the protobuf design principle
- The old version loads fine, but OrganizationFactSheet data is **LOST** if the old version re-saves
- This is called "round-trip data loss" — the old version drops data it doesn't understand

**Mitigation options:**
1. **Don't allow downgrades** — document that downgrading after saving with a new version may lose new data
2. **Backup before upgrade** — already a best practice
3. **Schema version marker** — see section 4.5

### 4.5 Schema Versioning

**Current state:** The codebase already has a schema versioning precedent! In `DataAccessLayer.Load(GlobalData)`:

```csharp
if (localData.DataSchemaVersion < 2)
{
    FixIds(localData.DeserializedNodeListForDataAccess);
    localData.DataSchemaVersion = 2;
}
```

This pattern exists for `GlobalData` (scan.bin) but **NOT for FactSheetContainer** (FactSheets.bin).

**Recommendation:** Add a schema version to FactSheetContainer:

```csharp
[ProtoMember(100)] public int SchemaVersion { get; set; } = 1;
```

Use `100` to leave plenty of room for new List<T> properties. This allows:
- Detecting if data was saved by a newer version
- Running migration code on load
- Warning users about forward-compatibility risks

### 4.6 Known Existing Patterns

The codebase shows clear evidence of **iterative schema growth**:
1. ProtoMember gaps in base FactSheet (3, 7, 13, 19, 25, 28 are skipped) — these were removed/deprecated fields
2. ApplicationFactSheet jumps from 20 to 50 — intentional gap for future fields
3. ProcessFactSheet starts at 51 — shows awareness of numbering importance
4. BusinessCapabilityFactSheet jumps from 5 to 40 to 100 — same pattern
5. The `CreationSource` enum uses explicit `[ProtoEnum]` attributes with sequential values — good practice
6. `ValueChainType` enum uses explicit `[ProtoEnum]` with assigned values — also good practice

---

## 5. Testing Strategy

### 5.1 Pre-Release Backwards Compatibility Test

**Step 1: Capture a baseline .bin**
```
1. Run current production OmniGaze
2. Ensure FactSheets.bin has representative data (all factsheet types, various enums set)
3. Copy FactSheets.bin → test_baseline_v4.bin
```

**Step 2: Load with new code**
```
1. Build OmniGaze with all schema changes
2. Replace FactSheets.bin with test_baseline_v4.bin
3. Start OmniGaze
4. Verify:
   - All existing factsheets load correctly
   - Display names, descriptions, enums are intact
   - No exceptions in log
   - New OrganizationFactSheets list is empty (not null)
   - New fields on existing types are default values
```

**Step 3: Round-trip test**
```
1. After loading old .bin with new code, save
2. Reload
3. Verify all data is intact
4. Verify new default values are persisted correctly
```

**Step 4: Automated unit test**
```csharp
[TestMethod]
public void OldBinFile_LoadsWithNewSchema_NoDataLoss()
{
    // Arrange: serialize a FactSheetContainer with OLD schema
    var oldContainer = new FactSheetContainer();
    var app = new ApplicationFactSheet 
    { 
        DisplayName = "TestApp", 
        TechnicalFit = TechnicalFitEnum.Appropriate,
        Category = "Business"
    };
    oldContainer.ApplicationFactSheets.Add(app);
    
    byte[] oldBytes;
    using (var ms = new MemoryStream())
    {
        Serializer.SerializeWithLengthPrefix(ms, oldContainer, PrefixStyle.Base128);
        oldBytes = ms.ToArray();
    }
    
    // Act: deserialize with current (new) schema
    FactSheetContainer loaded;
    using (var ms = new MemoryStream(oldBytes))
    {
        loaded = Serializer.DeserializeWithLengthPrefix<FactSheetContainer>(ms, PrefixStyle.Base128);
    }
    
    // Assert
    Assert.AreEqual(1, loaded.ApplicationFactSheets.Count);
    Assert.AreEqual("TestApp", loaded.ApplicationFactSheets[0].DisplayName);
    Assert.AreEqual(TechnicalFitEnum.Appropriate, loaded.ApplicationFactSheets[0].TechnicalFit);
    Assert.AreEqual("Business", loaded.ApplicationFactSheets[0].Category);
    
    // New collections should be empty, not null
    Assert.IsNotNull(loaded.OrganizationFactSheets);
    Assert.AreEqual(0, loaded.OrganizationFactSheets.Count);
    
    // New fields should be default
    // (e.g., PaceLayer == PaceLayerEnum.Unspecified)
}
```

**Step 5: Enum value preservation test**
```csharp
[TestMethod]
public void ExistingEnumValues_PreservedAfterSchemaChange()
{
    // Test that HostingTypeEnum.SaaS (=5) still serializes/deserializes as 5
    var hosting = new Hosting { Criticality = Hosting.HostingTypeEnum.SaaS };
    
    byte[] bytes;
    using (var ms = new MemoryStream())
    {
        Serializer.Serialize(ms, hosting);
        bytes = ms.ToArray();
    }
    
    using (var ms = new MemoryStream(bytes))
    {
        var loaded = Serializer.Deserialize<Hosting>(ms);
        Assert.AreEqual(Hosting.HostingTypeEnum.SaaS, loaded.Criticality);
    }
}
```

### 5.2 Forward Compatibility Test (Optional but Recommended)

```
1. Save FactSheets.bin with NEW code (includes OrganizationFactSheet data)
2. Load with OLD code (before changes)
3. Verify:
   - Old code loads without crash
   - All pre-existing data is intact
   - OrganizationFactSheet data is silently ignored
   - Re-saving with old code WILL lose OrganizationFactSheet data (expected, document this)
```

### 5.3 Customer Data Test

```
1. Obtain anonymized/test customer .bin files
2. Load each with new code
3. Verify no exceptions
4. Verify data integrity (spot-check counts, names, enum values)
```

---

## 6. Quick Reference: Adding OrganizationFactSheet Checklist

- [ ] Create `OrganizationFactSheet.cs` with `[ProtoContract]`, ProtoMembers starting at 1
- [ ] Add `[ProtoInclude(518, typeof(OrganizationFactSheet))]` to `FactSheet` base class
- [ ] Add `[ProtoMember(19)] public List<OrganizationFactSheet> OrganizationFactSheets` to `FactSheetContainer`
- [ ] Update `FactSheetContainer.RemoveFactSheet()` — add case
- [ ] Update `FactSheetContainer.AllFactSheets` — add `.Concat()`
- [ ] Update `FactSheetContainer.AddIfNotExists()` — add case
- [ ] Update `FactSheetContainer.GetFactSheetsByType<T>()` — add case
- [ ] Update `FactSheet._factSheetCollections` dictionary if hierarchy needed
- [ ] Add to `FactSheet.HierarchyParentId` if applicable
- [ ] Create backwards-compat unit test
- [ ] Test with production .bin file
- [ ] Verify no ProtoMember/ProtoInclude number conflicts

---

## 7. Summary

**The bottom line: All planned changes are SAFE as long as we follow additive-only rules.**

Protobuf (and protobuf-net specifically) was designed for schema evolution. The key invariants:
1. **Never reuse numbers** (ProtoMember, ProtoInclude)
2. **Never change types** on existing numbers
3. **Never reorder enum integer values**
4. **Always add, never remove** serialized fields

The existing OmniGaze codebase already follows these patterns (evidence: gaps in numbering from removed fields, explicit enum value assignments). Continue this discipline.

**Specific numbers for the OrganizationFactSheet addition:**
- **ProtoInclude: 518** on FactSheet base
- **FactSheetContainer ProtoMember: 19** for the list
- **Internal ProtoMembers: start at 1** (per-type namespace)

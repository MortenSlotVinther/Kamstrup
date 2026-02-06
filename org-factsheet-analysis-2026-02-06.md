# Organization FactSheet — Analysis of Morten's Idea

**Date:** February 6, 2026  
**Context:** Morten asks: "What about introducing a factsheet for org's? This would give us a dimension more?"

---

## The Insight

UserGroupFactSheet is semantically wrong for what Kamstrup needs. Today it models "who uses the app" — consumers. But Kamstrup's org hierarchy (Country → BU → Department → Team) represents "which organizational unit owns/operates/needs this in context." That's a fundamentally different dimension.

Making Organization a first-class factsheet type doesn't just rename UserGroup — it **reframes the entire relationship model** and has direct implications for the n-ary problem.

---

## What UserGroupFactSheet Is Today

Thin. Very thin:

```csharp
public class UserGroupFactSheet : FactSheet
{
    // No custom fields at all
    // Just display helpers for related Apps and Processes
    public string ApplicationsDisplay => FormatRelatedFactSheets<ApplicationFactSheet>();
    public string ProcessesDisplay => FormatRelatedFactSheets<ProcessFactSheet>();
}
```

**Current relationships** (from `RelationshipManager`):
- UserGroup → Application (parent-child)
- UserGroup → DataObject (parent-child)
- UserGroup → Interface (parent-child)
- Objective → UserGroup (parent-child)

That's it. UserGroup can't even relate to BusinessCapability or Process directly in the relationship model (only Apps can). This is a gap.

**Current UI:** `UserGroupsEAPage.razor` — a simple grid showing name, related apps, related processes. Labeled "Application Users."

---

## What OrganizationFactSheet Would Be

A factsheet type that represents an organizational unit with structural meaning:

```csharp
[ProtoContract]
public class OrganizationFactSheet : FactSheet
{
    [ProtoMember(1)] public string OrganizationType { get; set; }  // Country/BU/Department/Team
    [ProtoMember(2)] public string CountryCode { get; set; }       // "DK", "IN", etc.
    [ProtoMember(3)] public string CostCenter { get; set; }        // Optional financial link
    
    // Hierarchy is already built into FactSheet base (HierarchyParentId, HierarchyChildrenIds)
    // So Country → BU → Department → Team comes free
}
```

**New relationships to register:**
- Organization → Application (which org uses this app)
- Organization → BusinessCapability (which org needs this capability)
- Organization → Process (which org runs this process)
- Organization → ValueStream (which org participates in this value stream)
- Organization → ITComponent (which org's infrastructure)
- Organization → DataObject (which org's data)

---

## The N-ary Problem: Does Org-as-FactSheet Solve It?

### The Original Problem
KamstrupData row = App × Capability × Org × Process × ValueStream + contextual TIME/Criticality

### What Three Separate Binary Relationships Give You

With `OrganizationFactSheet` as first-class, you get:

| Relationship | Example | Stored As |
|---|---|---|
| App → Capability | "IFS ERP supports Strategic Management" | ParentFactSheetsIds |
| App → Organization | "IFS ERP is used by DK_Digitalization" | ParentFactSheetsIds |
| Capability → Organization | "Strategic Management is needed by DK_Digitalization" | ParentFactSheetsIds |
| App → Process | "IFS ERP supports P10-Sourcing" | ParentFactSheetsIds |
| Capability → Process | "Strategic Management maps to P10-Sourcing" | ParentFactSheetsIds |

### Can You Reconstruct the N-ary From the Intersection?

**Partially, but not fully.** If you know:
- App A → Capability C ✓
- App A → Org O ✓  
- Capability C → Org O ✓

The **intersection** (A ∩ C ∩ O) tells you these three things are related. This is much better than today where Org context is hacked into concerns or missing entirely.

**But you still can't answer:** "What is the TIME rating for App A *specifically in* Capability C *for* Org O?" Because TIME varies per context — the same app might be "Invest" for one capability-org combination and "Migrate" for another.

### Verdict: Org FactSheet Reduces but Does NOT Eliminate the N-ary Need

The n-ary mapping (Solution 2 from the earlier analysis) is still needed for **contextual attributes** (TIME, Criticality per combination). But Org as a first-class citizen:

1. **Reduces what the n-ary mapping needs to carry** — it doesn't need to encode Org identity, just reference it
2. **Enables independent Org queries** — "Show me all apps for DK_Digitalization" becomes a simple relationship traversal, no mapping table needed
3. **Enables Org-based views** — capability maps filtered by org, app portfolios per org, process landscapes per org — all using standard relationship navigation

---

## How Org FactSheet Interacts With Solution 2 (ApplicationContextMapping)

**They complement each other perfectly:**

```
ApplicationContextMapping references:
  → ApplicationFactSheet (Guid)
  → BusinessCapabilityFactSheet (Guid)
  → OrganizationFactSheet (Guid)     ← was UserGroup, now proper Org
  → ProcessFactSheet (Guid)
  → ValueStreamFactSheet (Guid)
  + ContextualTIME
  + ContextualCriticality
```

With Org as first-class:
- **Without mapping table:** Navigate App→Org, Capability→Org, Process→Org directly. Covers 80% of reporting needs.
- **With mapping table:** Get contextual TIME/Criticality for specific combinations. Covers the remaining 20%.

**Key insight:** Most users ask "what apps does this org use?" or "what capabilities does this org need?" — these are binary queries that Org-as-FactSheet handles natively. The n-ary mapping is only needed for the analytical/contextual layer.

This means the ApplicationContextMapping factsheet could potentially be **deferred** — ship Org FactSheet first, get immediate value, add the mapping type later if Kamstrup needs contextual TIME reporting.

---

## Dev Effort for OrganizationFactSheet

Based on the existing pattern (UserGroupFactSheet as template):

| Task | Effort | Notes |
|---|---|---|
| `OrganizationFactSheet.cs` | 30min | Simple class, few custom fields |
| `FactSheet.cs` — add `[ProtoInclude(518, typeof(OrganizationFactSheet))]` | 5min | Next available slot |
| `FactSheetContainer.cs` — add `[ProtoMember(19)] List<OrganizationFactSheet>` | 30min | Update AllFactSheets, RemoveFactSheet, AddIfNotExists, GetFactSheetsByType |
| `RelationshipManager.cs` — add Org relationship rules | 30min | Org → App, Org → Capability, Org → Process, etc. |
| `OrganizationsEAPage.razor` — list page | 1-2h | Copy UserGroupsEAPage pattern, add org-specific columns |
| `OrganizationSummarySection.razor` — detail section | 1h | Type, country, cost center fields |
| Navigation/menu update | 30min | Add to EA sidebar |
| Import script for Kamstrup org data | 1-2h | Create Org factsheets from Country/BU/Department/Team hierarchy |
| **Total** | **~5-7h (1 day)** | |

**Importantly:** This is LESS effort than Solution 2 (ApplicationContextMapping at 14h) and delivers standalone value.

---

## Does It Generalize?

**Yes, strongly.** Every EA customer has an organization dimension:

| Customer Pattern | OrganizationFactSheet Maps To |
|---|---|
| Multi-country enterprise (Kamstrup) | Country → BU → Department → Team |
| Holding company | Legal Entity → Division → Unit |
| Government | Ministry → Agency → Department |
| University | Faculty → Institute → Group |
| Matrix org | Function × Region (multiple hierarchies via tags) |

UserGroup stays for what it actually means — application consumers/user communities. Organization becomes the structural/operational dimension. They're orthogonal.

**LeanIX comparison:** LeanIX doesn't have a separate Org type — they overload UserGroup. This is actually a known pain point in LeanIX implementations. Having a dedicated Org type would be a differentiator.

---

## Recommendation

### Phase 0 (NEW — 1 day): OrganizationFactSheet
- Create the type, wire it up, import Kamstrup's org hierarchy
- Establish App→Org, Capability→Org, Process→Org relationships
- **Immediate value:** Org-filtered views, org-based navigation, proper dimensional model

### Phase 1 (2 days): Binary relationships + Concerns
- Import all Kamstrup binary relationships (including to new Org factsheets)
- Contextual TIME/Criticality as auto-generated concerns (quick win)

### Phase 2 (if needed): ApplicationContextMapping
- Only if Kamstrup explicitly needs per-combination TIME/Criticality reporting
- Org FactSheet might make this unnecessary for v1

**Bottom line:** Morten's instinct is right. Org-as-dimension is the architecturally clean move. It's low effort, high generalizability, and it might reduce the urgency of the n-ary mapping factsheet by making the most common queries (org-filtered views) work through standard binary relationships.

---

*Analysis based on: UserGroupFactSheet.cs, FactSheet.cs (ProtoInclude 500-517), FactSheetContainer.cs (ProtoMember 1-18), RelationshipManager.cs, UserGroupsEAPage.razor, UserGroupSummarySection.razor*

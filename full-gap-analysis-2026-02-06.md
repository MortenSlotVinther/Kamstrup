# Full Gap Analysis: Kamstrup Spreadsheet vs OmniGaze Model

**Date:** February 6, 2026  
**Prepared by:** Ole (subagent analysis)  
**Source:** `Kamstrup_Business-Capability-Map.xlsx` (22 sheets)  
**Cross-referenced against:** OmniGaze codebase at `F:\RootContext\OmniGazeRoot\OmniGaze\`

---

## 1. Per-Sheet Analysis

### 1.1 KamstrupData (5,399 rows × 20 cols) — 🔴 CRITICAL

The core fact table. Each row = App × Capability × Org × Process mapping.

| Col | Field | Kamstrup Values | OmniGaze Mapping | GAP? |
|-----|-------|-----------------|------------------|------|
| 2 | Active from date | DateTime | No relationship lifecycle | 🔴 **GAP: No from/to dates on relationships** |
| 3 | End date | DateTime | No relationship lifecycle | 🔴 Same as above |
| 4 | Capability ID | Composite key `1007-Strategic Management--` | BusinessCapabilityFactSheet lookup | ✅ Via lookup |
| 5-7 | Capability Level 1/2/3 | Denormalized from B-BC | Hierarchy on BCFS | ✅ |
| 8 | Level 4 | Unused | N/A | ✅ |
| 9 | Country code | `DK10`, `ES10` etc. | UserGroupFactSheet | ⚠️ See Org gap |
| 10 | Business Area | `DK_Digitalization_EA...` | UserGroupFactSheet | ⚠️ See Org gap |
| 11 | Department/Team | `Cloud and Infra` etc. | UserGroupFactSheet | ⚠️ See Org gap |
| 12 | Application No | `1 - IFS ERP` | ApplicationFactSheet lookup | ✅ Via lookup |
| 13 | Application Name | Denormalized | DisplayName | ✅ |
| 14 | **Contextual Gartner TIME** | Tolerate/Invest/Migrate/Eliminate | `PortFolioStrategy.TIME` is **global per app** | 🔴 **GAP: TIME is per-app, not per-mapping** |
| 15 | **Contextual Business Criticality** | Administrative/Operational/Critical/Mission Critical | `BusinessSupport.Criticality` is **global per app** | 🔴 **GAP: Criticality is per-app, not per-mapping** |
| 16 | Process ID | `P10-Sourcing--` | ProcessFactSheet lookup | ✅ Via lookup |
| 17 | Value Stream | 12 distinct values | ValueStreamFactSheet | ⚠️ Value count mismatch (see §2.4) |
| 18 | Value Stream Order | Integer sort | No sort property on VS relationship | 🟡 **GAP: No ordering on value stream references** |
| 19 | Projects | Free text | ProjectFactSheet reference | 🟡 **GAP: Text, not structured refs** |
| 20 | Comment | Free text | FactSheetConcern or notes | ✅ Via Concerns |

**STRUCTURAL GAP — N-ary Mapping:**
- OmniGaze stores **binary** relationships (App→Capability, App→UserGroup, App→Process)
- Kamstrup's model is **n-ary** (App × Capability × Org × Process per row with contextual attributes)
- The same app can map to the same capability with **different TIME/Criticality per org context**
- **This is the #1 architectural gap.** Binary relationships cannot express "IFS ERP is Invest for Strategic Management in DK_Digitalization but Tolerate for Finance in ES_Sales"

---

### 1.2 A-Applications (995 rows × 42 cols) — 🔴 CRITICAL

| Col | Field | Kamstrup Values | OmniGaze Mapping | GAP? |
|-----|-------|-----------------|------------------|------|
| 4 | Application name | Text | `DisplayName` | ✅ |
| 5 | Application Group | 24 distinct groups | `Category` | ✅ |
| 6 | Introduction date | DateTime | `LifeCycle.Active` or `LifeCycle.PhaseIn` | ✅ |
| 7 | Install type | On Premise, Cloud, Distributed Applications, Edge Computing (4 values) | `Hosting.HostingTypeEnum` has: Unmapped, Desktop, Mobile, OnPrem, Hybrid, SaaS, PaaS, IaaS (8 values) | 🟡 **GAP: Enum mismatch** — "Distributed Applications" and "Edge Computing" don't map; "Third Party Hosted" in Tabels also missing |
| 8 | Gartner TIME (global) | Tolerate/Invest/Migrate/Eliminate | `PortFolioStrategy.TIME` | ✅ Perfect match |
| 9 | Application Type | Production IT, Service Tools, Kamstrup Software, Development Tools, Customer Experience, etc. (8+ values) | `ApplicationType` enum or `ApplicationTypeTags` | ✅ Tags handle this |
| 10 | Software Vendor | Text (vendor name) | → `ProviderFactSheet` relationship | ✅ Via relationship |
| 11 | ItemNumber | Vendor item/contract number | No field | 🟡 **GAP: No item/contract number on App or Provider** |
| 12 | Consultancy | Vendor name | → `ProviderFactSheet` (consultancy type) | ✅ Via ProviderType |
| 13 | User base | 0-9, 10-49, 50-99, 100-499, 500-999, 1000-> (6 ranges) | `UserBase.Size` enum: Unknown, VerySmall(1-9), Small(10-49), Medium(50-99), Large(100-499), VeryLarge(500-999), Enterprise(1000+) | ✅ Perfect match (Kamstrup "0-9" → VerySmall) |
| 14 | Lifecycle stage | **9 stages**: 1-Strategic, 2-Important, 3-Kamstrup app, 4-Saved for now, 5-Investigate, 7-Potential for phase out, 8-Phase out, 8-Kamstrup app-Phase out, 9-End of Life | `LifeCycle` has **5 phases**: Plan, PhaseIn, Active, PhaseOut, EndOfLife | 🔴 **GAP: 9 stages → 5 phases. Lossy mapping. No "Strategic/Important/Investigate" distinction** |
| 15 | Expected End-of-Life Year | DateTime | `LifeCycle.EndOfLife` | ✅ |
| 16 | Replaced by | App name | `SuccessorId` | ✅ |
| 17 | Details | Free text description | `RichDescription` | ✅ |
| 18 | URL | URL | `Url` | ✅ |
| 19 | Business Owner | Initials (e.g. "MIBN") | `Owners` (Business Owner role) | ✅ But needs initials→name lookup |
| 20 | Supported by Group IT | Yes/No/X | No field | 🟡 **GAP: No "IT-supported" flag** |
| 21 | Details2 | Free text | `RichDescription` (append) | ✅ |
| 22 | Owner | Name/initials | `Responsible` | ✅ |
| 23 | Super User | Initials | No field | 🟡 **GAP: No Super User role** |
| 24 | Named users | Comma-sep initials | No field | 🟡 **GAP: No named users list** |
| 25 | OLD-Data integration | Text | Deprecated — skip | ✅ |
| 26 | Temp | Text | Temporary — skip | ✅ |
| 27 | SLA | Text | `DisasterSLA` exists but different structure | ✅ Close enough |
| 28 | License responsible | Initials | No field | 🟡 **GAP: No license responsible role** |
| 29 | Sub component to | App reference | HierarchyParentId (app hierarchy) | ✅ |
| 30 | Supporting applications | App names | ParentFactSheetsIds (app→app) | ⚠️ Needs App↔App bidirectional relationship |
| 31 | Org (primary department) | Text | No field | 🟡 **GAP: No "primary org" field on app** |
| 32 | AI | No, Yes, Yes-Minimal Risk, Yes-Limited Risk, Yes-Risk not evaluated (5 values) | `AIClassification.UsesAI` + `AIClassification.RiskLevel` (NotApplicable, Minimal, Limited, High, Unacceptable) | ⚠️ **GAP: Kamstrup has "Yes - Risk not evaluated" → no OmniGaze equivalent for "uses AI but risk unknown"** |
| 33 | Used in capability mapping | Yes/No | No field | 🟡 **GAP: No mapping-eligibility flag** |
| 34 | Platform | Platform name | `PlatformTags` | ✅ |
| 35 | Clean up: Note | Text | No native field | 🟡 Custom field needed |
| 36 | Clean up: Recommendation | Text | No native field | 🟡 Custom field needed |
| 37 | Clean up: Reason | Text | No native field | 🟡 Custom field needed |
| 38 | Clean up: WP Size | S/M/L/Project/Project-initiated | No native field | 🟡 Custom field needed |
| 39 | Security approved | Yes/No | `SecurityAssessment.Status` → Approved/NotAssessed | ✅ |
| 40 | Security approved date | DateTime | `SecurityAssessment.ApprovedDate` | ✅ |
| 41 | Security debt | Low/Investigate | `SecurityAssessment.DebtLevel` (Low, Medium, High, Critical, None, Unknown) | ⚠️ **GAP: "Investigate" not in DebtLevel enum** |
| 42 | Crown Jewels | Crown Jewel_1 | No native field | 🟡 **GAP: No Crown Jewels classification** |

---

### 1.3 B-Business Capability (677 rows × 17 cols) — 🔴 CRITICAL

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 2 | IdLevel123 | Composite key | Generated from hierarchy | ✅ |
| 3 | Column1 | Numeric ID | Internal | ✅ |
| 4 | Type | "BusinessCapability" | Type discriminator | ✅ |
| 5 | Level 0 (group) | "All", "Sales" etc. | Top hierarchy node | ✅ |
| 6 | Level 1 | 8 top-level capabilities | BCFS L1 via HierarchyChildren | ✅ |
| 7 | Level 2 | ~53 capabilities | BCFS L2 | ✅ |
| 8 | Level 3 | ~300+ capabilities | BCFS L3 | ✅ |
| 9 | **Pace Layer** | Systems of Innovation, Systems of Differentiation, Systems of Commodity (3 values) | No native field. `CapabilityType` exists but holds "Business/Technical/Strategic/Compliance" | 🔴 **GAP: No Pace Layer field on BCFS** |
| 10 | Description | Text | `RichDescription` | ✅ |
| 11 | **Value Stream** | 12 distinct value streams | `SupportedValueStreamIds` (Guid refs) | ✅ Structure exists |
| 12 | Value Stream Order | Integer | No sort property | 🟡 **GAP: No sort order on VS relationship** |
| 13 | **NIS2 Criticality** | High/Medium/Low/Not evaluated (from Tabels) | No native field | 🔴 **GAP: No NIS2/regulatory criticality field** |
| 14 | Updated date | DateTime | `ModifiedDateTime` | ✅ |
| 15 | Business Responsible | Initials | `Responsible` | ✅ |
| 16 | Comment | Text | Concerns or notes | ✅ |
| 17 | PowerAppsId | GUID | Import metadata — skip | ✅ |

---

### 1.4 O-Organization (76 rows × 14 cols) — 🔴 CRITICAL

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 2 | Level 2 (Organization/BU) | Sales & Marketing, Customer Service, Finance, etc. | UserGroupFactSheet L2 | ⚠️ Semantic mismatch |
| 3 | Level 3 (Business Area) | DK_Sales, CH_Customer Services, etc. | UserGroupFactSheet L3 | ⚠️ Same |
| 4 | Level 1 (Country) | Denmark, Switzerland, Spain, France, Netherlands, etc. (19 countries) | UserGroupFactSheet L1 | ⚠️ Same |
| 5 | Level 4 (Team) | Only header present (unused in current data) | UserGroupFactSheet L4 | ⚠️ |
| 9 | CountryCode | AT10, CA10, CH10, CN10, DE10, DK10, etc. | No field | 🔴 **GAP: No country code on UserGroupFactSheet** |
| 10 | Country name | Austria, Canada, Switzerland, etc. | DisplayName | ✅ |
| 14 | DepartmentTeam | Business Development, Project Management, etc. (67 entries) | DisplayName for teams | ✅ |

**STRUCTURAL GAP — Organization vs UserGroup:**
- `UserGroupFactSheet` has **zero custom fields** — just inherits from FactSheet
- Kamstrup's org model needs: `OrganizationType` (Country/BU/Department/Team), `CountryCode`, possibly `CostCenter`
- UserGroup semantically means "who uses the app" (consumers), Kamstrup needs "which org unit owns/operates" (structural)
- **Missing relationships:** UserGroup cannot relate to BusinessCapability or ValueStream in RelationshipManager
- Current RelationshipManager allows: UserGroup → Application, UserGroup → DataObject, UserGroup → Interface
- **Needed:** Org → BusinessCapability, Org → Process, Org → ValueStream

---

### 1.5 C-Business Context (656 rows × 18 cols) — 🟡 HIGH

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 3 | NoProcess | Composite key | ProcessFactSheet lookup | ✅ |
| 4 | Document no | Process number | No field | 🟡 **GAP: No document/process number** |
| 5 | Process group | 36 groups | ProcessFactSheet L1 | ✅ |
| 6 | Process | ~150 processes | ProcessFactSheet L2 | ✅ |
| 7 | Document no SubProcess | SP01.1 etc. | No field | 🟡 Same as Doc no |
| 8 | SubProcess | ~300 subprocesses | ProcessFactSheet L3 | ✅ |
| 9 | **Approver** | Email/name | `Responsible` | ✅ |
| 10 | **Business Unit** | Text | No field on ProcessFactSheet | 🟡 **GAP: No owning BU on process** |
| 11 | **Country** | Country code | No field on ProcessFactSheet | 🟡 **GAP: No country scope on process** |
| 12 | **Editing state** | Current, Draft, Pending approval, Review, N/A | No field | 🟡 **GAP: No editing/approval state on process** |
| 13 | Test | Internal | Skip | ✅ |
| 16 | **Value Stream** | 12 distinct values | No ValueStream relationship on ProcessFactSheet | 🔴 **GAP: Process→ValueStream relationship doesn't exist** |
| 17 | **Description** | Text | `RichDescription` | ✅ |
| 18 | **Platform** | Aras, Supply Chain, etc. | No field | 🟡 **GAP: No platform association on process** |

**KEY GAP:** ProcessFactSheet has only `Frequency` and `DurationInHours` as custom fields. Missing: document number, BU/country scope, editing state, value stream link, platform association.

---

### 1.6 P_Platform (44 rows × 10 cols) — 🟡 HIGH

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 2 | Platform name | 35+ platforms | ITComponentFactSheet.DisplayName | ✅ |
| 3 | **Platform or Suite** | Platform, Programming Language, Existing single app, New app, Phase Out (5 types) | `ITComponentType` (default "Server") | 🟡 **GAP: Type values don't match** |
| 4 | **Friendly name** | Short display name (PLM, CRM, etc.) | No field | 🟡 **GAP: No friendly/alias name** |
| 5 | **Description** | Short desc | No native short description | ✅ via `RichDescription` or description field |
| 6 | **Long description** | Rich text | `RichDescription` | ✅ |
| 7 | **Strategic** | Strategic / Non-strategic | No native field | 🔴 **GAP: No strategic classification on platforms** |
| 8 | **Comment** | Internal notes | Concerns | ✅ |
| 9 | **AI** | Yes/No | No AI field on ITComponentFactSheet | 🟡 **GAP: AI flag only on ApplicationFactSheet** |
| 10 | **Platform Owner** | Initials | `Responsible` | ✅ |

**Conceptual issue:** Kamstrup's "Platform" is a **strategic grouping** of applications (IFS platform = IFS ERP + IFS modules). OmniGaze's ITComponentFactSheet models infrastructure components (servers, switches). These are semantically different. A dedicated **PlatformFactSheet** or repurposing ITComponent with a "Platform" type would be needed.

---

### 1.7 P-PlatformData (341 rows × 17 cols) — 🟡 HIGH

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 2 | Platform | Platform name | ITComponentFactSheet ref | ✅ |
| 3 | Capability ID | Composite key | BCFS ref | ✅ |
| 4 | "North" Names | Business unit names | UserGroup refs | ⚠️ |
| 5 | **SubModule** | Module/feature name within platform | No direct mapping | 🔴 **GAP: Platform→Capability module mapping doesn't exist as a concept** |
| 6 | **Utilization** | No, Low, Medium, High, ? | No field | 🔴 **GAP: No utilization assessment on platform-capability mapping** |
| 7 | **Module technical assessment** | Fully Appropriate, Adequate, Unreasonable, Inappropriate | `TechnicalFitEnum` exists on ApplicationFactSheet but not on platform mapping | 🔴 **GAP: Tech fit per platform-capability, not just per app** |
| 8 | **Module functional assessment** | Perfect, Appropriate, Insufficient, Unreasonable | `FunctionalFitEnum` exists on ApplicationFactSheet but not on platform mapping | 🔴 Same |
| 9 | **AI** | Yes/No per module | No field | 🟡 |
| 10 | **Description** | Per-module description | No field | 🟡 |
| 11 | **Long description** | Detailed per-module | No field | 🟡 |
| 12 | **Kamstrup bought module** | Yes/No | No field | 🟡 **GAP: No "licensed/purchased" flag on module** |
| 13 | **From date** | DateTime | No lifecycle on mapping | 🟡 |
| 14 | **To date** | DateTime | No lifecycle on mapping | 🟡 |
| 15 | NoApplication | App reference | App→Module relationship | ✅ |
| 16 | Capability check | Validation | Skip | ✅ |
| 17 | Expected End-of-Life | Date | LifeCycle.EndOfLife | ✅ |

**This is essentially a ModuleFactSheet capability mapping with per-module assessments.** OmniGaze's `ModuleFactSheet` exists but has limited fields (ModuleType, QA, SupportProvider). It lacks: utilization, technical fit, functional fit, AI flag, purchased flag, and module→capability mapping.

---

### 1.8 D-Data Object (35 rows × 9 cols) — 🟢 MEDIUM

| Col | Field | Values | OmniGaze Mapping | GAP? |
|-----|-------|--------|------------------|------|
| 2 | Source application | App reference | InterfaceFactSheet.ProviderApplications | ⚠️ |
| 3 | Target application | App reference | InterfaceFactSheet.ConsumerApplications | ⚠️ |
| 4 | Integration name | Text | InterfaceFactSheet.DisplayName | ✅ |
| 5 | Comments | Text | `RichDescription` | ✅ |
| 6 | Owner | Text (e.g. "Digitalization-Integration") | `Responsible` | ✅ |
| 9 | Original list from FFM | Legacy reference | Skip | ✅ |

**Note:** Kamstrup's "Data Object" sheet is actually an **integration mapping** (which app sends data to which app), not a data entity catalog. This maps better to `InterfaceFactSheet` than `DataObjectFactSheet`. OmniGaze's DataObjectFactSheet has EntityCategory, DataElement, ElementType, MasterDataApplication — wrong abstraction for this data.

---

### 1.9 Security Assessment (24 rows × 41 cols) — 🟢 MEDIUM

This sheet has the **same columns as A-Applications** (it's essentially a filtered view of apps under security review). Columns 2-41 match A-Applications 1:1. No additional gaps beyond those already identified in §1.2.

**The only addition:** Col 16 "Replaced by" is actively used here for apps being phased out for security reasons.

---

### 1.10 A-Applications_Removed (242 rows × 39 cols) — 🟢 MEDIUM

Decommissioned applications with extra financial tracking:

| Col | Field | OmniGaze Mapping | GAP? |
|-----|-------|------------------|------|
| 7 | Yearly saving DKR | No field | 🟡 **GAP: No savings tracking on retired apps** |
| 8 | Date of removal | `LifeCycle.EndOfLife` | ✅ |
| 10 | Number of NEW apps replacing | No field | 🟡 |
| 11 | Replacement app | `SuccessorId` | ✅ |
| 12 | Yearly cost for replacement | No field | 🟡 |
| 13-26 | **Full cost columns**: CostGroup, Supplier, ItemNumber, CostType, FromDate, ToDate, Interval, Termination notice, FTE, Opex rate, Currency, Yearly costs, VendorID | `Cost` has only CapEx/OpEx/Currency/Description | 🔴 **GAP: Cost model far too simple** |
| 27 | Vendor (finance) | Provider relationship | ✅ |
| 28 | Finance info yearly licence | No field | 🟡 |
| 31 | License Owner | No field | 🟡 |
| 32 | License Approver | No field | 🟡 |
| 33 | Department (Approver) | No field | 🟡 |
| 34 | Country | No field | 🟡 |
| 35 | Termination date | No field on contract | 🟡 |
| 36-39 | Finance tracking (last payment, budget owner, actual saving, validated) | No finance workflow | 🔴 **GAP: No financial lifecycle/cleanup workflow** |

---

### 1.11 A-Application_Approval (6 rows × 18 cols) — ⚪ LOW (WIP)

| Col | Field | GAP? |
|-----|-------|------|
| 2 | Application ref | ✅ |
| 3 | ECS approved (Yes/No) | 🟡 **GAP: No multi-party approval workflow** |
| 4 | ECS Approval date | 🟡 |
| 5 | ECS Approved by | 🟡 |
| 6 | Legal approved | 🟡 |
| 7 | Legal Approval date | 🟡 |
| 8 | Legal Approved by | 🟡 |

**GAP:** OmniGaze has no concept of multi-party approval workflows (ECS + Legal + Security).

---

### 1.12 A-Application_Budget (10 rows × 5 cols) — ⚪ LOW (WIP)

| Col | Field | GAP? |
|-----|-------|------|
| 2 | Description (Azure, Licenses) | 🟡 |
| 3 | Date | 🟡 |
| 4 | Type (Budget/Actual) | 🔴 **GAP: No budget vs actual cost tracking** |
| 5 | Amount (24M, 82M DKK) | `Cost` has OpExAmount but integer only | 🟡 |

**GAP:** OmniGaze Cost model has no concept of Budget vs Actual, no time-series cost tracking, no category breakdown.

---

### 1.13 Tabels (229 × 83) — Configuration/Lookup Reference

Key lookup lists that need OmniGaze enum/config matches:

| Tabels Column | Values | OmniGaze Enum | Match? |
|---------------|--------|---------------|--------|
| **YesNo** | Yes, No | Boolean | ✅ |
| **NIS2 Criticality** | High, Medium, Low, Not evaluated | **No enum** | 🔴 GAP |
| **Strategy** | Strategic, Non-strategic | **No enum** | 🔴 GAP |
| **User base** | 0-9, 10-49, 50-99, 100-499, 500-999, 1000-> | `UserBaseSize` | ✅ |
| **Lifecycle stage** | Under Evaluation, 1-Strategic through 9-End of Life, Not in use (11 values) | `LifeCycle` (5 phases) | 🔴 **11 vs 5** |
| **Install type** | On Premise, Cloud, Third Party Hosted, Edge Computing, Distributed Applications (5 values) | `HostingTypeEnum` (8 values, different labels) | 🟡 Mismatch |
| **Gartner TIME** | Tolerate, Invest, Migrate, Eliminate | `PortFolioStrategy.StrategyEnum` | ✅ |
| **Technical Fit** | Fully Appropriate, Adequate, Unreasonable, Inappropriate (4 values) | `TechnicalFitEnum`: Unmapped, Unreasonable, Inappropriate, Adequate, Appropriate (5 values) | ⚠️ Kamstrup "Fully Appropriate" → OmniGaze "Appropriate"? Close but names differ |
| **Functional Fit** | Perfect, Appropriate, Insufficient, Unreasonable (4 values) | `FunctionalFitEnum`: Unmapped, Unreasonable, Insufficient, Appropriate, Perfect (5 values) | ✅ Perfect match |
| **Pace Layer** | Systems of Innovation, Systems of Differentiation, Systems of Commodity (3 values) | **No enum** | 🔴 GAP |
| **Currency** | DKR, USD, EUR, NOK, SEK (5 values) | `Cost.Currency` (ISO code string) | ✅ |
| **CostType** | License, Support, Maintenance, Hosting, FTE-Actual, FTE-Required, Consumption, OPEX/Professional Service, CAPEX (9 types) | `CostType` enum: YearlyLicenseCost, OneOffCapexExpense (2 types) | 🔴 **9 vs 2** |
| **Business Criticality** | Administrative Service, Business Operational, Business Critical, Mission Critical (4 values) | `BusinessSupport.CriticalityEnum` | ✅ |
| **Application Group** | 24 groups | `Category` (free text) | ✅ |
| **Users** | 227 entries (email + initials + department + country) | `Contributor` / AD users | ✅ Via AD integration |
| **AI** | No, Yes-Risk not evaluated, Yes-Minimal, Yes-Limited, Yes-High, Yes-Unacceptable, Unknown (7 values) | `AIClassification`: UsesAI + AIRiskLevel (5 levels) + "NotApplicable" | ⚠️ "Yes-Risk not evaluated" and "Unknown" need mapping |
| **WP Size** | S, M, L, Project, Project-initiated (5 values) | **No enum** | 🔴 GAP |

---

### 1.14 Processer280125 (1,289 rows × 8 cols) — ⚪ REFERENCE

Full process dump from Kamstrup's process management tool. Extra columns:

| Col | Field | GAP? |
|-----|-------|------|
| 1 | Document name | ✅ DisplayName |
| 2 | Document no (SP01.1) | 🟡 No doc number field |
| 3 | Document responsible (email) | ✅ Responsible |
| 4 | Approver(s) (email) | 🟡 **GAP: No approver field on ProcessFactSheet** |
| 5 | Public name | ✅ DisplayName |
| 6 | Editing state (Draft/Current) | 🟡 No state field |
| 7 | Pending since (date) | 🟡 No pending/queue date |

---

### 1.15 CleanUp Software Departments (120 rows × 8 cols) — ⚪ LOW

Cleanup tracking for Software Department apps. Uses same fields as A-Applications cleanup columns. No additional gaps.

---

### 1.16 Level1/Level2/Level3 / Capabilities_Default — ⚪ REFERENCE

Capability lookup tables. Absorbed into B-Business Capability. No additional gaps.

---

### 1.17 temp / temp_CapaText / Export — ⚪ SKIP

Working/temporary sheets. No import needed.

---

## 2. Summary of ALL Gaps Found

### 2.1 🔴 Critical Structural Gaps

| # | Gap | Impact | Where Found |
|---|-----|--------|-------------|
| **G1** | **N-ary relationship model** — Kamstrup's fact table (App × Capability × Org × Process) with contextual TIME/Criticality per combination. OmniGaze only has binary relationships with global attributes. | Cannot represent 40% of Kamstrup's data model | KamstrupData |
| **G2** | **Organization ≠ UserGroup** — UserGroupFactSheet has no custom fields, no country code, no org type. Semantically wrong for structural org hierarchy. Missing relationships to Capability, Process, ValueStream. | Org dimension completely unmodeled | O-Organization, KamstrupData |
| **G3** | **Lifecycle model mismatch** — 9-stage lifecycle (Strategic→End of Life) vs 5-phase (Plan→EndOfLife). Key distinction: "Strategic" vs "Important" vs "Kamstrup app" all collapse to "Active". | Loses strategic classification on import | A-Applications, Tabels |
| **G4** | **Relationship lifecycle** — From/To dates on mappings (KamstrupData cols 2-3). OmniGaze has no date properties on relationships. | Cannot track when a mapping was valid | KamstrupData |
| **G5** | **Platform capability mapping with assessments** — PlatformData has per-module utilization, tech fit, functional fit per capability. This is a structured mapping that doesn't exist. | Cannot import P-PlatformData at all | P-PlatformData |
| **G6** | **Pace Layer classification** — Used on capabilities, no field or enum exists | Missing strategic classification | B-Business Capability |
| **G7** | **NIS2/Regulatory Criticality** — Used on capabilities, no field or enum exists | Missing compliance classification | B-Business Capability |
| **G8** | **Process→ValueStream relationship** — Doesn't exist in RelationshipManager | Cannot link processes to value streams | C-Business Context |
| **G9** | **Cost model too simple** — 2 cost types vs 9; no Budget vs Actual; no time-series; no termination/savings tracking | Cannot model financial lifecycle | A-Applications_Removed, A-Application_Budget, Tabels |

### 2.2 🟡 Medium Gaps (Field/Enum Level)

| # | Gap | Where |
|---|-----|-------|
| **G10** | Install type enum mismatch: "Distributed Applications", "Edge Computing", "Third Party Hosted" missing from HostingTypeEnum | A-Applications, Tabels |
| **G11** | Security debt "Investigate" not in SecurityDebtLevel enum | A-Applications |
| **G12** | AI classification: "Yes - Risk not evaluated" and "Unknown" need mapping (AIRiskLevel has no "NotEvaluated") | A-Applications, Tabels |
| **G13** | Crown Jewels classification — no field, no enum | A-Applications |
| **G14** | Platform strategic classification — no field | P_Platform |
| **G15** | Platform type mismatch — ITComponentType defaults to "Server", Kamstrup uses "Platform/Suite/Programming Language/Phase Out" | P_Platform |
| **G16** | Value stream ordering — no sort property on VS references | KamstrupData, B-Business Capability |
| **G17** | Process document number — no field on ProcessFactSheet | C-Business Context |
| **G18** | Process approver — no approver field (separate from Responsible) | C-Business Context, Processer |
| **G19** | Process editing state — no workflow state field | C-Business Context |
| **G20** | Process→Platform association — no relationship | C-Business Context |
| **G21** | "Supported by Group IT" flag on applications | A-Applications |
| **G22** | Super User role on applications | A-Applications |
| **G23** | Named Users list on applications | A-Applications |
| **G24** | License responsible role on applications | A-Applications |
| **G25** | Item/contract number on applications | A-Applications |
| **G26** | Clean up workflow fields (4 fields: Note, Recommendation, Reason, WP Size) | A-Applications |
| **G27** | "Used in capability mapping" eligibility flag | A-Applications |
| **G28** | Module "purchased" flag | P-PlatformData |
| **G29** | Application→Application bidirectional "supports" relationship not in RelationshipManager | A-Applications |
| **G30** | D-Data Object is actually integration mapping, not data entity — wrong factsheet type | D-Data Object |
| **G31** | Multi-party approval workflow (ECS + Legal) | A-Application_Approval |
| **G32** | Value Stream count: Kamstrup has 12, earlier analysis identified only 7. Full list needs: Acquire-to-Retire, Concept-to-Customer, Customer Service and Support, Hire-to-Retire, Idea-to-Release, Maintenance and Support, Make-to-Delivery, Order-to-Cash, Plan-to-Produce, Procure-to-Pay, Quote-to-Quality, Subscription-to-Pay | KamstrupData, B-BC, C-BC |
| **G33** | TechnicalFit enum labels: Kamstrup "Fully Appropriate" vs OmniGaze "Appropriate" (should be fine but may confuse) | Tabels |
| **G34** | Platform friendly name / alias | P_Platform |

---

## 3. New FactSheet Types Needed

### 3.1 OrganizationFactSheet (HIGH PRIORITY)

**Justification:** UserGroupFactSheet is semantically wrong and structurally inadequate.

```csharp
[ProtoContract]
public class OrganizationFactSheet : FactSheet
{
    [ProtoMember(1)] public string OrganizationType { get; set; }  // Country, BusinessUnit, Department, Team
    [ProtoMember(2)] public string CountryCode { get; set; }       // DK10, ES10, etc.
    [ProtoMember(3)] public string CostCenter { get; set; }        // Optional financial link
}
```

**New relationships needed:**
- Organization → Application (which org uses this app)
- Organization → BusinessCapability (which org needs this capability)
- Organization → Process (which org runs this process)
- Organization → ValueStream (which org participates in this value stream)

**Effort:** ~5-7h (1 day)

### 3.2 ApplicationContextMapping (MEDIUM PRIORITY — solves G1)

**Justification:** The n-ary fact table cannot be represented with binary relationships.

```csharp
[ProtoContract]
public class ApplicationContextMapping : FactSheet
{
    [ProtoMember(1)] public Guid ApplicationId { get; set; }
    [ProtoMember(2)] public Guid BusinessCapabilityId { get; set; }
    [ProtoMember(3)] public Guid? OrganizationId { get; set; }
    [ProtoMember(4)] public Guid? ProcessId { get; set; }
    [ProtoMember(5)] public Guid? ValueStreamId { get; set; }
    [ProtoMember(6)] public PortFolioStrategy.StrategyEnum ContextualTIME { get; set; }
    [ProtoMember(7)] public BusinessSupport.CriticalityEnum ContextualCriticality { get; set; }
    [ProtoMember(8)] public DateTime? ValidFrom { get; set; }
    [ProtoMember(9)] public DateTime? ValidTo { get; set; }
    [ProtoMember(10)] public string Projects { get; set; }
    [ProtoMember(11)] public string Comment { get; set; }
}
```

**Effort:** ~12-16h (2 days) including UI and relationship wiring

### 3.3 PlatformFactSheet or Repurpose ITComponentFactSheet (LOW-MEDIUM)

**Justification:** Kamstrup's "Platform" concept (strategic grouping of apps around a vendor stack) is different from OmniGaze's ITComponent (infrastructure hardware/software).

Options:
1. **Add type variant to ITComponentFactSheet** — add "Platform" to ITComponentType, add Strategic/NonStrategic flag, AI flag
2. **Create dedicated PlatformFactSheet** — cleaner but more work

If option 1:
```csharp
// On ITComponentFactSheet, add:
[ProtoMember(12)] public bool IsStrategic { get; set; }
[ProtoMember(13)] public string FriendlyName { get; set; }
[ProtoMember(14)] public AIClassification AIClassification { get; set; }
```

**Effort:** Option 1: ~3h. Option 2: ~8h.

---

## 4. New Fields/Enums Needed on EXISTING Types

### 4.1 On FactSheet (base class)

| Field | Type | Purpose | Covers Gap |
|-------|------|---------|------------|
| None needed at base level | | | |

### 4.2 On ApplicationFactSheet

| Field | Type | Purpose | Covers Gap |
|-------|------|---------|------------|
| `CrownJewels` | `bool` or `CrownJewelLevel` enum | Crown jewel classification | G13 |
| `SupportedByIT` | `bool` | Group IT support flag | G21 |
| `UsedInCapabilityMapping` | `bool` | Mapping eligibility | G27 |
| `ItemNumber` | `string` | Vendor contract/item number | G25 |

**Roles to add to Owners system:**
- Super User (G22)
- License Responsible (G24)

**Named Users:** Use existing `ContributorGuids` or add `NamedUsers` list

**Cleanup fields (G26):** Best handled via CustomColumnDefinition (4 custom fields):
- Clean up: Note (TextArea)
- Clean up: Recommendation (Dropdown)
- Clean up: Reason (TextArea)
- Clean up: WP Size (Dropdown: S, M, L, Project, Project-initiated)

### 4.3 On BusinessCapabilityFactSheet

| Field | Type | Purpose | Covers Gap |
|-------|------|---------|------------|
| `PaceLayer` | `PaceLayerEnum` (Innovation/Differentiation/Commodity) | Gartner pace layer strategy | G6 |
| `NIS2Criticality` | `NIS2CriticalityEnum` (High/Medium/Low/NotEvaluated) | NIS2/regulatory criticality | G7 |

### 4.4 On ProcessFactSheet

| Field | Type | Purpose | Covers Gap |
|-------|------|---------|------------|
| `DocumentNumber` | `string` | Process document reference (SP01.1) | G17 |
| `EditingState` | `EditingStateEnum` (Draft/Current/PendingApproval/Review) | Document workflow state | G19 |
| `Approver` | `string` (email/name) | Separate from Responsible | G18 |

### 4.5 On ModuleFactSheet

| Field | Type | Purpose | Covers Gap |
|-------|------|---------|------------|
| `Utilization` | `UtilizationEnum` (None/Low/Medium/High) | Module utilization at customer | G5 partial |
| `TechnicalFit` | `TechnicalFitEnum` | Module technical assessment | G5 partial |
| `FunctionalFit` | `FunctionalFitEnum` | Module functional assessment | G5 partial |
| `IsPurchased` | `bool` | Whether customer bought this module | G28 |
| `AIEnabled` | `bool` | Module has AI features | — |

### 4.6 Enum Additions/Changes

| Enum | Change | Covers Gap |
|------|--------|------------|
| `HostingTypeEnum` | Add: `ThirdPartyHosted`, `EdgeComputing`, `DistributedApp` | G10 |
| `SecurityDebtLevel` | Add: `Investigate` (or map to existing) | G11 |
| `AIRiskLevel` | Add: `NotEvaluated` / `Unknown` | G12 |
| `CostType` | Expand from 2→9: License, Support, Maintenance, Hosting, FTE-Actual, FTE-Required, Consumption, OPEX, CAPEX | G9 partial |
| NEW `PaceLayerEnum` | SystemsOfInnovation, SystemsOfDifferentiation, SystemsOfCommodity | G6 |
| NEW `NIS2CriticalityEnum` | High, Medium, Low, NotEvaluated | G7 |
| NEW `EditingStateEnum` | Draft, Current, PendingApproval, Review | G19 |
| NEW `UtilizationEnum` | None, Low, Medium, High | G5 |
| NEW `WPSizeEnum` | Small, Medium, Large, Project, ProjectInitiated | G26 |

### 4.7 Lifecycle Enhancement

The 5-phase lifecycle model needs to accommodate 9+ stages. Options:

**Option A — Custom field for lifecycle stage (minimal change):**
- Keep 5-phase model for dates
- Add `LifecycleStageLabel` string field to store the customer's own stage name
- Map: 1-Strategic/2-Important/3-Kamstrup → Active, 4-Saved/5-Investigate/7-Potential → PhaseOut, 8-Phase out → PhaseOut, 9-End of Life → EndOfLife

**Option B — Configurable lifecycle stages (proper fix):**
- Make lifecycle stages configurable per customer
- Store as `List<LifecycleStage>` with custom names and date ranges
- Kamstrup defines 9 stages, another customer might define 4

**Recommendation:** Option A for Kamstrup import (1h), plan Option B for v5 (3-5 days).

---

## 5. New Relationship Types Needed

| # | Source | Target | Type | Purpose | Covers Gap |
|---|--------|--------|------|---------|------------|
| R1 | Organization → Application | ParentChild | Org uses/owns app | G2 |
| R2 | Organization → BusinessCapability | ParentChild | Org needs capability | G2 |
| R3 | Organization → Process | ParentChild | Org runs process | G2 |
| R4 | Organization → ValueStream | ParentChild | Org participates in VS | G2 |
| R5 | Process → ValueStream | ParentChild | Process belongs to VS | G8 |
| R6 | Application → Application | Bidirectional | "Supports" relationship | G29 |
| R7 | ITComponent(Platform) → BusinessCapability | ParentChild | Platform supports capability | G5 |
| R8 | ITComponent(Platform) → Module | ParentChild | Platform contains modules | G5 |
| R9 | Module → BusinessCapability | ParentChild | Module covers capability | G5 |

**Currently in RelationshipManager:**
- Objective → UserGroup, Stakeholder, BusinessCapability, Process
- BusinessCapability → Application, DataObject, Interface, Process, Module
- Process → Application, DataObject, Interface
- Application → ITComponent, Provider, Module, DataObject, Interface
- DataObject/Interface → ITComponent, Provider
- UserGroup/Stakeholder → Application, DataObject, Interface
- Process ↔ Process (bidirectional)

**Missing from above list:**
- Organization → anything (type doesn't exist yet)
- Process → ValueStream
- Application → Application
- ITComponent → BusinessCapability
- Module → BusinessCapability

---

## 6. Priority Ranking

### Tier 1 — Must-have for Kamstrup import (Week 1)

| Priority | Gap | Effort | Unlocks |
|----------|-----|--------|---------|
| **P1** | OrganizationFactSheet + relationships (G2) | 1 day | Org dimension, org-filtered views |
| **P2** | Lifecycle stage mapping + custom label (G3) | 2h | Correct lifecycle import |
| **P3** | Hosting enum additions (G10) | 30min | Correct install type import |
| **P4** | AI "Not Evaluated" addition (G12) | 30min | Correct AI classification import |
| **P5** | Security debt "Investigate" (G11) | 30min | Correct security import |
| **P6** | PaceLayer field + enum (G6) | 1h | Capability classification |
| **P7** | NIS2Criticality field + enum (G7) | 1h | Regulatory compliance |
| **P8** | Process→ValueStream relationship (G8) | 1h | Process-VS links |
| **P9** | Value Stream count (G32) — 12 VSs need to be created | 30min | Reference data |

### Tier 2 — Important for full model fidelity (Week 2)

| Priority | Gap | Effort | Unlocks |
|----------|-----|--------|---------|
| **P10** | ApplicationContextMapping factsheet (G1) | 2 days | N-ary mapping, contextual TIME/Criticality |
| **P11** | Relationship lifecycle dates (G4) | 4h | Temporal validity of mappings |
| **P12** | Platform strategic flag + type fixes (G14, G15) | 2h | Platform strategy views |
| **P13** | Module fields: utilization, fit, purchased (G5) | 3h | P-PlatformData import |
| **P14** | Process fields: doc number, editing state, approver (G17-19) | 2h | Full process import |
| **P15** | App→App bidirectional relationship (G29) | 1h | Supporting apps links |
| **P16** | Crown Jewels field (G13) | 30min | Critical asset classification |

### Tier 3 — Nice-to-have / Future (Week 3+)

| Priority | Gap | Effort | Unlocks |
|----------|-----|--------|---------|
| **P17** | Cost model expansion (G9) | 1-2 days | Financial lifecycle |
| **P18** | Cleanup workflow fields (G26) | 1h (custom fields) | App rationalization tracking |
| **P19** | Approval workflow (G31) | 3-5 days | Multi-party approval |
| **P20** | Budget vs Actual tracking | 2-3 days | Financial planning |
| **P21** | Owner roles (Super User, License Responsible) (G22, G24) | 1h | User role tracking |
| **P22** | Configurable lifecycle stages (Option B) | 3-5 days | Per-customer lifecycle |

### Total Effort Estimate

| Tier | Effort |
|------|--------|
| Tier 1 | ~2 days |
| Tier 2 | ~4 days |
| Tier 3 | ~10 days |
| **All tiers** | **~16 days** |

**For Kamstrup import (Tier 1 + Tier 2):** ~6 working days of model changes, plus the import script work from the earlier estimate.

---

## Appendix A: Complete Enum Value Mapping Tables

### Lifecycle Stages
| Kamstrup | OmniGaze Phase | Notes |
|----------|---------------|-------|
| Under Evaluation | Plan | New evaluation |
| 1-Strategic | Active | Core strategic app |
| 2-Important application | Active | Important but not core |
| 3-Kamstrup application | Active | Standard Kamstrup app |
| 4-Saved for now | PhaseOut | Kept but not invested |
| 5-Investigate | PhaseOut | Under review |
| 7-Potential for phase out | PhaseOut | Candidate for removal |
| 8-Phase out | PhaseOut | Actively retiring |
| 8-Kamstrup application-Phase out | PhaseOut | Kamstrup app retiring |
| 9-End of Life | EndOfLife | Decommissioned |
| Not in use | EndOfLife | Abandoned |

### Install Type
| Kamstrup | OmniGaze HostingType | Notes |
|----------|---------------------|-------|
| On Premise | OnPrem | ✅ |
| Cloud | SaaS | ⚠️ Could be SaaS/PaaS/IaaS |
| Third Party Hosted | **NEW: ThirdPartyHosted** | Needs enum addition |
| Edge Computing | **NEW: EdgeComputing** | Needs enum addition |
| Distributed Applications | **NEW: DistributedApp** | Needs enum addition |

### AI Classification
| Kamstrup | OmniGaze UsesAI | OmniGaze RiskLevel | Notes |
|----------|----------------|-------------------|-------|
| No | false | NotApplicable | ✅ |
| Yes | true | **NotEvaluated** (NEW) | Needs enum addition |
| Yes - Risk not evaluated | true | **NotEvaluated** (NEW) | Same |
| Yes - Minimal Risk | true | Minimal | ✅ |
| Yes - Limited Risk | true | Limited | ✅ |
| Yes - High Risk | true | High | ✅ |
| Yes - Unacceptable Risk | true | Unacceptable | ✅ |
| Unknown | false | **NotEvaluated** (NEW) | Or custom handling |

---

*Analysis complete. Cross-referenced 22 spreadsheet sheets (14 substantive) against 18 OmniGaze FactSheet types, 12 enum definitions, RelationshipManager rules, and CustomField system. Identified 34 gaps across 9 critical, 25 medium categories.*

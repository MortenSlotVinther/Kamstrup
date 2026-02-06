# Verification Report: Implementation Docs vs Actual Spreadsheet

**Generated:** 2026-02-06  
**Verified by:** Ole (automated cross-check)  
**Source:** `Kamstrup_Business-Capability-Map.xlsx` (22 sheets)

---

## Executive Summary

**Overall status: ⚠️ Mostly correct with several discrepancies requiring fixes**

- 6 implementation docs checked
- 12 discrepancies found (❌)
- 8 items needing attention (⚠️)
- 40+ items verified correct (✅)

---

## 1. Master Plan (00-MASTER-PLAN.md)

| Item | Status | Detail |
|------|--------|--------|
| Sheet count "22 sheets" | ✅ | Confirmed: 22 sheets |
| "~993 apps" | ❌ | Actual: **992** data rows (Row 3=header, rows 4-995 = 992 apps) |
| "~673 capabilities" | ❌ | Actual: **672** rows with data (rows 6-677, excluding empty rows). L1=**20** (not 8). L2=**101**. L3=**532** |
| "~76 orgs" | ✅ | 75 data rows (close enough — "~76" is fair) |
| "~656 processes" | ✅ | 655 data rows (row 2=header, rows 3-656 = 654+1) — close |
| "5,396 mapping rows" | ❌ | Actual: **5,395** data rows (rows 5-5399 with data, minus header rows) |
| "993 active + 242 removed" | ❌ | Active: **992**. Removed: **88** data rows (not 242 — 242 is total sheet rows including empties/headers) |
| "44 platforms" | ❌ | Actual: **34** platform rows in P_Platform (not 44; 44 is sheet max_row including headers) |
| "341 module records" | ⚠️ | 322 data rows with Platform name (col B). Row 20 is header row. Actual data: ~**302** (322 minus the header row and a few structural rows) |
| L1 capabilities "8" | ❌ | Actual L1: **20** unique values (including "All" and "Not mapped to capability") |
| "12 value streams" | ✅ | Confirmed 12 unique value streams across all sources |

---

## 2. Model Foundation (01-model-foundation.md)

### Enums

| Enum | Status | Detail |
|------|--------|--------|
| **PaceLayerEnum** | ✅ | 3 values match Tabels col 25: "Systems of Innovation", "Systems of Differentiation", "Systems of Commodity" |
| **NIS2CriticalityEnum** | ✅ | 4 values match Tabels col 4: "High", "Medium", "Low", "Not evaluated" |
| **EditingStateEnum** | ✅ | Values match C-Business Context col 12 actual: "N/A", "Draft", "Current", "Pending approval", "Review" |
| **UtilizationEnum** | ⚠️ | Tabels doesn't have a dedicated Utilization lookup. Values in P-PlatformData col 6: "No", "Low", "Medium", "High", "?". The enum maps "No"→None which is correct. |
| **HostingTypeEnum +3** | ✅ | ThirdPartyHosted, EdgeComputing, DistributedApp — matches Tabels col 12. Note: "Third Party Hosted" is only in Tabels, **not in actual A-Applications data** (0 occurrences). But having the enum value is correct for future-proofing. |
| **AIRiskLevel +1 (NotEvaluated)** | ⚠️ | Tabels has "Unknown" as a value (col 62), but the implementation maps "Unknown"→NotApplicable. Consider adding "Unknown" as a separate value, OR document that "Unknown" maps to NotApplicable. Also: actual data has bare "Yes" (1 occurrence) which maps to "NotEvaluated" — correct? Doc 03 maps "Yes"→`NotEvaluated(5)` which is reasonable. |
| **SecurityDebtLevel +1 (Investigate)** | ✅ | Actual data has "Investigate" (22 apps). Adding Investigate=6 is correct. |

### ProtoMember Numbers

| Item | Status | Detail |
|------|--------|--------|
| OrganizationFS ProtoInclude 518 | ✅ | Claimed next after 517 |
| Container ProtoMember 19 | ✅ | Claimed next after 18 |
| BC PaceLayer PM 6 | ✅ | Gap between 5 and 40 |
| BC NIS2Criticality PM 7 | ✅ | Gap between 5 and 40 |
| Process DocumentNumber PM 53 | ✅ | After 52 |
| Process EditingState PM 54 | ✅ | After 53 |
| Process Approver PM 55 | ✅ | After 54 |
| Base FactSheet LifecycleStageLabel PM 45 | ✅ | After 44 |

### Relationship Rules

| Rule | Status | Detail |
|------|--------|--------|
| Organization → Application | ✅ | Needed for KamstrupData |
| Organization → BusinessCapability | ✅ | Needed for KamstrupData |
| Organization → Process | ✅ | Needed for KamstrupData |
| Organization → ValueStream | ⚠️ | Not directly evidenced in the data — there's no direct Org→VS mapping in the spreadsheet. This is an inferred relationship. Consider if it's needed. |
| Process → ValueStream | ✅ | C-Business Context col 16 has Value Stream per process |

---

## 3. Master Data Import (02-master-data-import.md)

### B-Business Capability

| Item | Status | Detail |
|------|--------|--------|
| "673 items" | ❌ | Actual: **672** rows with any of L1/L2/L3 populated |
| "3-level hierarchy" | ⚠️ | Actually **4 levels**: L0 (group: Sales, Corporate Services, etc.) → L1 → L2 → L3. L0 is in col 5 and doc says "skip — grouping only" which is a valid design choice but should be explicitly documented. |
| "8 L1 capabilities" | ❌ | **20 unique L1 values** (not 8). Full list: All, Customer Relationship, Customer Service, Digital Management, Digital Platform and Operations, Finance, Governance Risk and Compliance, Legal, Manufacturing, Marketing, Not mapped to capability, OT Hosting, OT Manufacturing, People and Culture, Procurement & Logistics, Product & Software Development, Sales, Strategic Management, Supply Chain, Sustainability Management |
| "~53 L2 capabilities" | ❌ | Actual: **101 unique L2 values** |
| "~300+ L3 capabilities" | ❌ | Actual: **532 unique L3 values** |
| Column mapping | ⚠️ | Doc lists col C(3) as "Column1" = Type. Col D(4) is "Type". The actual header row 5 shows: B=IdLevel123, C=Column1, D=Type, E=Level 0, F=Level 1... This is correct in the mapping but Type field is not mapped to anything — it contains values like "BusinessCapability". Could be useful to store. |
| NIS2 mapping | ✅ | Matches Tabels col 4 values |
| Pace Layer mapping | ✅ | Matches Tabels col 25 values |
| "Digital Management" trailing space | ⚠️ | In the data, "Digital Management " (with trailing space) appears 25 times vs "Digital Management" (5 times). Import should `.Trim()` all names. |

### O-Organization

| Item | Status | Detail |
|------|--------|--------|
| "76 items" | ✅ | 75 data rows (close) |
| "4-level hierarchy" | ⚠️ | Level 4 (Team) is in col 14 (DepartmentTeam) but the header says "Level 4 - Kan ikke anvendes i denne model pga. Key" (Can't be used in this model due to Key). The doc maps col 5 as Level 4 but actual Level 4 data is in col N(14). Col 5 (Level 4 header) has only 1 value "Team" as header. The actual team names are in col 14. |
| Country codes | ✅ | 17 countries confirmed (AT10, CA10, CH10, CN10, DE10, DK10, ES10, FI10, FR10, IT10, MY10, NL10, NO10, PL10, SE10, US10 + FR10_2) |
| L2 unique values | ✅ | 16 unique BU names confirmed |

### C-Business Context

| Item | Status | Detail |
|------|--------|--------|
| "656 items" | ✅ | 655 data rows — close |
| "3-level hierarchy" | ✅ | Process Group (col 5) → Process (col 6) → SubProcess (col 8) |
| "~36 process groups" | ❌ | Actual: **5 process groups** (All, Core processes, Management processes, Not mapped, Supporting processes) |
| "~150 processes" | ⚠️ | Actual: **40 unique process names** (col 6) |
| EditingState values | ✅ | "Current", "Draft", "N/A", "Pending approval", "Review" — all in enum |
| Value Stream col is P(16) | ✅ | Confirmed |

### Value Streams

| Item | Status | Detail |
|------|--------|--------|
| "12 items" | ✅ | Confirmed 12 unique value streams |
| Names match | ⚠️ | Doc says "Make-to-Delivery" and "Order-to-Cash" and "Subscription-to-Pay" but data says "Make-to-Delivery (M2D)", "Order-to-Cash (O2C)", "Subscribtion-to-Pay (S2P)" — note the typo "Subscribtion" in the data (should be Subscription). Import should use exact data values. |
| "Acquire-to-Retire (A2R)" present | ✅ | In C-Business Context only (not in KamstrupData or B-Business Capability) |
| "Concept-to-Customer (C2C)" present | ✅ | In C-Business Context only |

### P_Platform

| Item | Status | Detail |
|------|--------|--------|
| "44 items" | ❌ | Actual: **34 platforms** (rows 5-44, excluding header row 4, but some rows empty. 34 non-null names in col B) |
| Column mapping | ✅ | Correct for cols B through J |
| Types | ✅ | Actual: Platform, Programming Language, Existing single applications, New applications, Phase Out |

### Providers

| Item | Status | Detail |
|------|--------|--------|
| "~100-150 unique providers" | ✅ | Not verified exact count but reasonable estimate |

---

## 4. Application Import (03-application-import.md)

### Row Counts

| Item | Status | Detail |
|------|--------|--------|
| "993 active applications" | ❌ | Actual: **992** (row 3=header, rows 4-995 = 992 data rows) |
| "242 removed applications" | ❌ | Actual: **88** rows with Application name in A-Applications_Removed. The sheet has 242 rows total but most are empty. |
| "42 columns" | ✅ | Confirmed 42 columns in A-Applications |

### Column Mapping (42 columns)

| Col | Status | Notes |
|-----|--------|-------|
| B(2) NoApplication | ⚠️ | Not in mapping table — should be used as lookup key (it IS mentioned in logic but not in the mapping table) |
| C(3) No | ⚠️ | Not in mapping table — numeric ID, used for Guid generation |
| D(4) Application name | ✅ | → DisplayName |
| E(5) Application Group | ✅ | → Category (24 groups confirmed) |
| F(6) Introduction date | ✅ | → LifeCycle.Active |
| G(7) Install type | ✅ | See mapping below |
| H(8) Gartner TIME | ⚠️ | Doc maps Tolerate/Invest/Migrate/Eliminate but actual data only has **Invest and Eliminate** in A-Applications col 8. Tolerate and Migrate only appear in KamstrupData (contextual). The mapping is still correct (all 4 should be handled) but it's noteworthy that most will be empty. |
| I(9) Application Type | ✅ | 11 actual values confirmed |
| J(10) Software Vendor | ✅ | → Provider relationship |
| K(11) ItemNumber | ✅ | Populated in 46 rows |
| L(12) Consultancy | ✅ | → Provider relationship |
| M(13) User base | ✅ | 6 values match mapping |
| N(14) Lifecycle stage | ✅ | 9 actual values (no "Under Evaluation" or "Not in use" in current data) |
| O(15) Expected End-of-Life | ✅ | |
| P(16) Replaced by | ✅ | |
| Q(17) Details | ✅ | → RichDescription |
| R(18) URL | ✅ | |
| S(19) Business Owner | ✅ | |
| T(20) Supported by Group IT | ✅ | Values: "X", "Yes", "No" |
| U(21) Details2 | ✅ | → append to RichDescription |
| V(22) Owner | ✅ | |
| W(23) Super User | ✅ | Col header "Delete,Superusers of the application" — 81 populated. Mapped to SuperUser field. |
| X(24) Named users | ⚠️ | 144 populated rows — **NOT in the mapping table**. Should be mapped somewhere (e.g., CustomField or dedicated field). |
| Y(25) OLD-Data integration | ✅ | Header says "Delete" — correctly low priority |
| Z(26) Temp | ✅ | Header says "EA Information related to closure" — mapped but empty |
| AA(27) SLA | ✅ | "Not relevant" per header |
| AB(28) License responsible | ✅ | "Not relevant" per header |
| AC(29) Sub component to | ✅ | → HierarchyParentId |
| AD(30) Supporting applications | ✅ | → Phase 4 relationship |
| AE(31) Org | ✅ | Primary cleanup track org |
| AF(32) AI | ✅ | See AI mapping check below |
| AG(33) Used in capability mapping | ✅ | Only "No" values (3 rows) |
| AH(34) Platform | ✅ | → Platform relationship |
| AI(35) Clean up: Note | ✅ | |
| AJ(36) Clean up: Recommendation | ✅ | |
| AK(37) Clean up: Reason | ✅ | |
| AL(38) Clean up: WP Size | ✅ | Values: S, M, Project, Project-initiated (no L in actual data vs Tabels which has L) |
| AM(39) Security approved | ✅ | Only "Yes" in actual data |
| AN(40) Security approved date | ✅ | |
| AO(41) Security debt | ✅ | Values: "Low" (1), "Investigate" (22) |
| AP(42) Crown Jewels | ✅ | Value: "Crown Jewel_1" (10 apps) |

### Lifecycle Stage Mapping

| Stage | In Tabels | In Actual Data | Status |
|-------|-----------|----------------|--------|
| Under Evaluation | ✅ | ❌ (0 rows) | ⚠️ In Tabels but not in data — mapping still correct |
| 1-Strategic | ✅ | ✅ (75) | ✅ |
| 2-Important application | ✅ | ✅ (224) | ✅ |
| 3-Kamstrup application | ✅ | ✅ (82) | ✅ |
| 4-Saved for now | ✅ | ✅ (119) | ✅ |
| 5-Investigate | ✅ | ✅ (376) | ✅ |
| 7-Potential for phase out | ✅ | ✅ (69) | ✅ |
| 8-Phase out | ✅ | ✅ (38) | ✅ |
| 8-Kamstrup application-Phase out | ✅ | ✅ (7) | ✅ |
| 9-End of Life | ✅ | ✅ (2) | ✅ |
| Not in use | ✅ | ❌ (0 rows) | ⚠️ In Tabels but not in data |

### Install Type Mapping

| Kamstrup | In Actual | Status |
|----------|-----------|--------|
| On Premise | ✅ (11 apps) | ✅ |
| Cloud | ✅ (81 apps) | ✅ |
| Third Party Hosted | ❌ (0 apps) | ⚠️ In Tabels, not in data |
| Edge Computing | ✅ (2 apps) | ✅ |
| Distributed Applications | ✅ (175 apps) | ✅ |
| Empty/unmapped | 723 apps | ✅ |

### AI Mapping

| Kamstrup | In Tabels | In Data | Status |
|----------|-----------|---------|--------|
| No | ✅ | ✅ (3) | ✅ |
| Yes | ❌ | ✅ (1) | ⚠️ Bare "Yes" not in Tabels but in data. Doc maps to NotEvaluated — acceptable |
| Yes - Risk not evaluated | ✅ | ✅ (10) | ✅ |
| Yes - Minimal Risk | ✅ | ✅ (1) | ✅ |
| Yes - Limited Risk | ✅ | ✅ (1) | ✅ |
| Yes - High Risk | ✅ | ❌ (0) | ✅ (in Tabels, not in data) |
| Yes - Unacceptable Risk | ✅ | ❌ (0) | ✅ (in Tabels, not in data) |
| Unknown | ✅ | ❌ (0) | ⚠️ In Tabels but not in data. Doc maps Unknown→NotApplicable |

### Security Mapping

| Item | Status | Detail |
|------|--------|--------|
| Security approved | ✅ | Only "Yes" (1 app) in actual data |
| Security debt | ✅ | "Low" (1), "Investigate" (22) — both in mapping |
| Missing values | ⚠️ | Tabels doesn't list security debt values explicitly. Doc adds "Investigate" to enum which is correct. Doc also lists Medium and High but these don't appear in actual data (only Low and Investigate). |

### A-Applications_Removed

| Item | Status | Detail |
|------|--------|--------|
| "242 items" | ❌ **CRITICAL** | Sheet has 242 total rows but only **88** have actual Application names. The rest are empty rows. The doc says "Read all 242 rows" — should be "Read ~88 rows" or "Read and filter non-empty rows". |
| Columns | ✅ | 39 columns confirmed. Mapping covers key fields. |
| "Retired = true" | ✅ | Correct approach |

---

## 5. Relationships (04-relationships.md)

### Data Sources

| Source | Status | Detail |
|--------|--------|--------|
| KamstrupData (5,396 rows) | ❌ | Actual: **5,395** data rows (row 1=header, row 2=section headers, row 3=empty, row 4=field headers, rows 5-5399 = data) |
| A-Applications vendor/platform | ✅ | Correct sources |
| B-Business Capability value stream | ✅ | Col K(11) confirmed |
| C-Business Context value stream | ✅ | Col P(16) confirmed |

### Relationship Types

| Relationship | Status | Detail |
|-------------|--------|--------|
| App → Capability | ✅ | From KamstrupData cols 12+4 |
| App → Organization | ✅ | From KamstrupData cols 12+9-11 |
| App → Process | ✅ | From KamstrupData cols 12+16. **Note:** Doc says col 16 is "NoProcess" but actual KamstrupData col 16 is "Business process applying to the capability" (header row 1). The short name in row 4 is "NoProcess". This is correct. |
| Capability → ValueStream | ✅ | From B-BC col K(11) to SupportedValueStreamIds |
| Capability → Organization | ✅ | Derived from KamstrupData intersection |
| Process → ValueStream | ✅ | From C-BC col P(16) |
| App → Provider | ✅ | From A-Apps col J(10) + L(12) |
| App → Platform | ✅ | From A-Apps col AH(34) |
| **App → Supporting Apps** | ⚠️ | Col AD(30) "Supporting applications" — mentioned in Phase 3 mapping but **not explicitly listed as a relationship in Phase 4**. Should be an App→App relationship. |

---

## 6. Context Mapping (05-context-mapping.md)

### Column Mapping

| KamstrupData Col | Status | Detail |
|------------------|--------|--------|
| B(2) Active from date | ✅ | → ValidFrom |
| C(3) End date | ✅ | → ValidTo |
| D(4) IdLevel123 | ✅ | → BusinessCapabilityId |
| E-H(5-8) Capability levels | ✅ | For display name |
| I(9) CountryCode | ✅ | → OrganizationId part 1 |
| J(10) Business Area | ✅ | → OrganizationId part 2 |
| K(11) Department/Team | ✅ | → OrganizationId part 3 |
| L(12) NoApplication | ✅ | → ApplicationId |
| M(13) Application Name | ✅ | For DisplayName |
| N(14) Gartner TIME | ✅ | → ContextualTIME. Values: Tolerate, Invest, Migrate, Eliminate |
| O(15) Business Criticality | ✅ | → ContextualCriticality. Values: Administrative Service, Business Operational, Business Critical, Mission Critical |
| P(16) NoProcess | ✅ | → ProcessId |
| Q(17) Value Stream | ✅ | → ValueStreamId |
| R(18) Value Stream Order | ✅ | → ValueStreamOrder |
| S(19) Projects | ✅ | → Projects |
| T(20) Comment | ✅ | → Comment |

### Criticality Mapping

| Kamstrup | Status | Detail |
|----------|--------|--------|
| Administrative Service | ✅ | Maps to enum value |
| Business Operational | ✅ | Maps to enum value |
| Business Critical | ✅ | Maps to enum value |
| Mission Critical | ✅ | Maps to enum value |

### "5,396 mappings"

| Item | Status | Detail |
|------|--------|--------|
| Row count | ❌ | Actual: **5,395** (off by 1 — likely a header/empty row difference) |

---

## 7. Platform/Module Import (06-platform-module-import.md)

### Row Count

| Item | Status | Detail |
|------|--------|--------|
| "341 rows" | ❌ | Actual: **302** data rows (322 rows with col B populated, minus 1 header row at R20, minus ~19 structural/capability header rows at R3-R19 that don't have Platform in col B). The first 19 rows are capability label headers, not module data. Data starts at row 20. |

### Column Mapping

| Col | Status | Detail |
|-----|--------|--------|
| B(2) Platform | ✅ | Parent ITComponentFactSheet |
| C(3) Capability ID | ✅ | → BusinessCapabilityFactSheet |
| D(4) "North" Names | ✅ | Org reference for context |
| E(5) SubModule | ✅ | → DisplayName |
| F(6) Utilization | ✅ | Values: "No", "Low", "Medium", "High", "?" — matches mapping |
| G(7) Technical Fit | ✅ | Values: "Fully Approoriate" (sic), "Adequate", "Unreasonable", "Inappropriate" |
| H(8) Functional Fit | ✅ | Values: "Perfect", "Appropriate", "Insufficient", "Unreasonable" |
| I(9) AI | ✅ | Values: "Yes" only (no "No" in data) |
| J(10) Description | ✅ | → ShortDescription |
| K(11) Long description | ✅ | → RichDescription |
| L(12) Purchased | ✅ | Values: "Yes", "No" |
| M(13) From date | ✅ | |
| N(14) To date | ✅ | |
| O(15) NoApplication | ✅ | → ApplicationFactSheet reference. Has 17 unique app references. |
| **P(16)** | ⚠️ | Contains **business process/capability names** (73 unique values like "Accounting", "Asset Management", "Change Management"). **NOT in doc's column mapping.** This appears to be a capability sub-area or module function name. Should be considered for import. |
| Q(17) Expected End-of-Life | ✅ | |

### Technical Fit Mapping

| Kamstrup | Status | Detail |
|----------|--------|--------|
| "Fully Approoriate" | ⚠️ | **Typo in source data** — the doc maps this as "Fully Appropriate"→Appropriate(4). Import code must match the EXACT typo "Fully Approoriate" from the data. Both the Tabels sheet and the P-PlatformData use "Approoriate" with the typo. |

### New Enums

| Enum | Status | Detail |
|------|--------|--------|
| TechnicalFitEnum | ⚠️ | Not explicitly listed in Phase 1 enum creation. Should be created in Phase 1 or Phase 6. |
| FunctionalFitEnum | ⚠️ | Same — not in Phase 1. Should be created. |

---

## 8. Tabels Sheet Comprehensive Check

### All Lookup Columns in Tabels

| Col | Name | Values | In Docs? | Status |
|-----|------|--------|----------|--------|
| 2 | YesNo | Yes, No | ✅ | Used throughout |
| 4 | NIS2 Criticality | High, Medium, Low, Not evaluated | ✅ | In 01-model-foundation |
| 6 | Strategy | Strategic, Non-strategic | ✅ | In 02 (P_Platform) |
| 8 | User base | 0-9, 10-49, 50-99, 100-499, 500-999, 1000-> | ✅ | In 03-application-import |
| 10 | Lifecycle stage | 11 values (see above) | ✅ | In 03-application-import |
| 12 | Install type | On Premise, Cloud, Third Party Hosted, Edge Computing, Distributed Applications | ✅ | In 03-application-import |
| 15 | Gartner TIME | Tolerate, Invest, Migrate, Eliminate | ✅ | In 03 and 05 |
| 19 | Technical Fit | Fully Approoriate, Adequate, Unreasonable, Inappropriate | ✅ | In 06 (with typo noted) |
| 22 | Functional Fit | Perfect, Appropriate, Insufficient, Unreasonable | ✅ | In 06 |
| 25 | Pace Layer | Systems of Innovation, Systems of Differentiation, Systems of Commodity | ✅ | In 01-model-foundation |
| 41 | Currency | DKR, USD, EUR, NOK, SEK | ⚠️ | NOT in any doc — only relevant for cost import (future) |
| 44 | CostType | License, Support, Maintance, Hosting, etc. (9 values) | ⚠️ | NOT in any doc — only relevant for cost import (future) |
| 46 | Business Criticality | Administrative Service, Business Operational, Business Critical, Mission Critical | ✅ | In 05-context-mapping |
| 51 | Application Group | 24 values | ✅ | In 03-application-import |
| 55 | User | 227 users with email+name | ⚠️ | Not directly mapped but used for Responsible/Owner/Approver fields |
| 59 | CountryCode | 17+ country codes | ✅ | In 02-master-data (O-Organization) |
| 62 | AI | No, Yes-Risk not evaluated, Yes-Minimal, Yes-Limited, Yes-High, Yes-Unacceptable, Unknown | ✅ | In 03-application-import |
| 82 | WP Size | S, M, L, Project, Project-initiated | ✅ | In 03-application-import |

---

## 9. Sheets Not Covered by Implementation

| Sheet | Status | Comment |
|-------|--------|---------|
| KamstrupData | ✅ | Covered in Phases 4 + 5 |
| A-Applications | ✅ | Phase 3 |
| A-Application_Approval | ⚠️ | **Not imported** (6 rows) — noted as future in Phase 6 footnote |
| A-Application_Budget | ⚠️ | **Not imported** (10 rows) — noted as future |
| B-Business Capability | ✅ | Phase 2 |
| O-Organization | ✅ | Phase 2 |
| C-Business Context | ✅ | Phase 2 |
| D-Data Object | ⚠️ | **Not imported** (35 rows) — noted as future in Phase 6 |
| P_Platform | ✅ | Phase 2 |
| P-PlatformData | ✅ | Phase 6 |
| Tabels | ✅ | Used for enum values |
| A-Applications_Removed | ✅ | Phase 3 |
| temp, temp_CapaText | ✅ | Correctly skipped (temp data) |
| Processer280125 | ⚠️ | **Not imported** (1289 rows of process documents). Could be valuable for enriching ProcessFactSheet with more document references. |
| Security Assessment | ⚠️ | **Not imported** (24 rows of detailed security assessments). Could enrich security data. |
| Export | ✅ | Correctly skipped (derived data) |
| CleanUp Software Departments | ⚠️ | **Not imported** (120 rows). Contains department-specific cleanup updates. Could be used to enrich app cleanup data. |
| Level1/Level2/Level3 | ✅ | Reference data, used indirectly via B-Business Capability |
| Capabilities_Default | ✅ | Reference data, Gartner default capabilities |

---

## 10. Summary of Required Corrections

### Critical Fixes (❌)

1. **00-MASTER-PLAN.md & 02-master-data-import.md**: L1 capabilities = **20** (not 8). L2 = **101** (not ~53). L3 = **532** (not ~300+).
2. **00-MASTER-PLAN.md & 03-application-import.md**: Active apps = **992** (not 993).
3. **00-MASTER-PLAN.md & 03-application-import.md**: Removed apps = **88** with data (not 242). The sheet has 242 rows but most are empty.
4. **00-MASTER-PLAN.md & 02-master-data-import.md**: P_Platform = **34** platforms (not 44).
5. **00-MASTER-PLAN.md & 06-platform-module-import.md**: P-PlatformData = ~**302** data rows (not 341).
6. **00-MASTER-PLAN.md & 05-context-mapping.md**: KamstrupData = **5,395** data rows (not 5,396).
7. **02-master-data-import.md**: Process groups = **5** (not ~36). Unique processes = **40** (not ~150).

### Attention Items (⚠️)

1. **01-model-foundation.md**: TechnicalFitEnum and FunctionalFitEnum should be listed in Phase 1 enum creation (currently only in Phase 6).
2. **03-application-import.md**: Col 24 "Named users" (144 populated rows) not in mapping table.
3. **04-relationships.md**: App→Supporting Apps relationship (col 30) mentioned in Phase 3 but not listed in Phase 4.
4. **06-platform-module-import.md**: Col P(16) contains module function/capability names (73 unique) — not in mapping.
5. **06-platform-module-import.md**: "Fully Approoriate" typo in source data — code must match this exact string.
6. **02-master-data-import.md**: "Digital Management " trailing space in data needs `.Trim()`.
7. **02-master-data-import.md**: O-Organization Level 4 (Team) is in col 14 (DepartmentTeam), not col 5.
8. **Processer280125** sheet (1289 rows) and **Security Assessment** sheet (24 rows) are not imported and not mentioned explicitly as out-of-scope in the plan.

---

*End of verification report*

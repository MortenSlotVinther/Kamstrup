Data we already imported (at our cost, before POC sign-off)

Kamstrup's master data was loaded into OmniGaze and verified — so the POC starts on Day 1 with a full environment, not an empty tenant.

### Foundation modeled in OmniGaze
- Business Capability hierarchy
- Configurable lists tailored to Kamstrup's vocabulary
- CMMI maturity levels wired into the model

### Master data imported
| Entity | Count |
|---|---|
| Business Capabilities | 678 |
| Organizations | 210 |
| Processes | 654 |
| Value Streams | 12 |
| Platforms | 34 |
| Providers | 482 |

### Applications
- **989 applications** imported with lifecycle, classification, and metadata
- 992 active / 88 removed reconciled and verified against source

### Relationships — 9,088 in total
- App ↔ Capability, Org, Process, Provider, Platform, App
- Capability ↔ Value Stream, Org
- Process ↔ Value Stream

### Context mappings
- **5,371 mappings** connecting applications to capabilities with organizational context

### Platforms & modules (deep import)
- 321 module-level JSON definitions
- Platform/module hierarchies and full relationships

### Tooling built for the import
- ~25 Python import/transform scripts (rerunnable, idempotent)
- OmniGaze MCP utility + test scripts
- Failure log + verification report — **final import error count: 0**

### Headline numbers
| Metric | Count |
|---|---|
| FactSheets | **7,872** |
| Relationships | **9,088** |
| Context Mappings | **5,371** |
| Import Errors | **0** |

---

## 5. Custom OmniGaze platform development — built FOR Kamstrup

Shipped between **2026-02 and 2026-04** specifically to make this POC succeed. None of this was on our roadmap before the engagement.

### New first-class model objects
- **Organization FactSheet** — new entity with parent/child hierarchy and OrgType, dedicated `Organizations` page in the EA module, nav menu entries (desktop + mobile)
- **Application Context Mapping FactSheet** — new n-ary entity (12 fields) so Kamstrup's 5,371 app ↔ capability ↔ org context mappings could exist as first-class objects, with their own list page, filters, and inline editing
- **Org Chart visualization** — new hierarchical tree page for Kamstrup's multi-region structure

### Model extensions on existing FactSheets
- **Business Capability** — 4 new capability-level fields with new summary/edit/display sections
- **Process FactSheet** — 4 new fields: Process Owner, Maturity (CMMI), Automation Degree, Criticality, with badges in the grid and configurable dropdowns
- **Module FactSheet** — 5 new fields: Utilization, Technical Fit, Functional Fit, IsPurchased, AI Enabled
- **Application** — PaceLayer and NIS2 Criticality migrated from hardcoded enums to configurable lists, with auto-migration of legacy values

### Configurable Lists subsystem (new)
- New `ConfigurableListDefinition` / `ConfigurableListValue` model + service layer with admin UI
- 5 initial lists seeded: HostingType, LifecycleStage, CostType, ITComponentType, EditingState
- 3 process lists added: ProcessMaturity (CMMI), AutomationDegree, ProcessCriticality
- **Customers can now maintain enumerations at runtime — no platform release required**

### New reporting & dashboards
- **Lifecycle Matrix Dashboard** — portfolio-wide view of apps × lifecycle stages, KPI row, color-coded matrix, grouping by Business Capability or Organization, end-of-life and unmapped-app insight callouts
- **Org Chart page** — hierarchical visual explorer for the org tree

### Import API & MCP enhancements
- New `KamstrupImportController` (~850 lines) with custom DTO/JSON field-matching for Kamstrup's relationship export format
- Auto-assignment of OrgType based on org depth (Country → BU → Department → Team)
- MCP server extended with FactSheet create/update operations and bulk-import tools
- Per-mode MCP tool allowlisting + improved descriptions
- OData pagination standardized across all endpoints — consistent envelopes for ServiceNow / Power BI consumers

### Validation, normalization, and fixes
- Python schema validators (`check_schema.py`, `check_security_schema.py`, `check_userbase.py`) to pre-validate Kamstrup exports before import
- OrgChart string-mismatch fix after migrating OrgType to a configurable list
- Lifecycle phase calculation fixed to match ApplicationCard color logic — correctness for the new dashboard

### Test coverage added
- **2,396+ new unit tests** across 8 test classes:
  - ConfigurableListDefinition / Service (264)
  - ConfigurableList migration (260)
  - Organization FactSheet (299)
  - Application Context Mapping (345)
  - Process FactSheet extended fields (330)
  - Module FactSheet extended fields (299)
  - RelationshipManager (276)
- Protects Kamstrup's import paths from regression

### Summary of platform investment
- **3 new FactSheet types**
- **13+ new fields** on existing types
- **2 new dashboards**
- **A new configurable-lists subsystem**
- **A dedicated import controller**
- **MCP / OData hardening**
- **~2,400 new tests**

---


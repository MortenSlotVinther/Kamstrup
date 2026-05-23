# Plan: "Hvad har vi måske overset?" — udtømmende tjek-liste

**Status:** ground-truth-tællinger i `FactSheets.bin` matcher Excel-forventning 100% (9.615 factsheets total). Denne plan ridser hvad der STADIG kunne gemme sig under tæppet — sorteret efter sandsynlighed/impact.

## A. Reference-integritet (intra-instans dangling refs)
Mål: ingen factsheet peger på en GUID der ikke findes i instansen.
1. **Mappings → Application:** for hver af de 5872 mappings, slå `ApplicationId` op i container; tæl danglende. (Burde være 0 efter vi tilføjede de 10 mapping-refererede apps.)
2. **Mappings → BusinessCapability:** 5872 × `BusinessCapabilityId` → BC findes? Forventet 0 dangler.
3. **Mappings → Organization/Process/ValueStream:** for de der har værdi, verificér resolution.
4. **Orgs HierarchyParentId / HierarchyChildrenIds:** 
   - For hvert org-barn: peger ChildId på et eksisterende org? (vi satte HierarchyChildrenIds fra JSON).
   - Bi-direktionel: parent.HierarchyChildrenIds vs child.HierarchyParentId-getter (afledt) er konsistent?
5. **BC hierarchy:** L1's parent peger på en eksisterende L0 (de 8 grupper)? Tæl orphan-L1/L2/L3.

## B. Excel-coverage gaps (data vi ikke importerer)
1. **A-Applications kolonne 24 "Named users"** (144 udfyldte) — flagget i Feb-audit, ikke importeret. Skal det med?
2. **KamstrupData kolonne 18 "Value Stream Order"** — bruges af mapping (ValueStreamOrder), verificér at det rent faktisk er sat på de mappings hvor kilde-kolonnen har værdi.
3. **A-Application_Costs, A-Application_Approval, A-Application_Budget** — finansielle ark. Vi har `Cost`-felter på ApplicationFactSheet — bør disse populates?
4. **D-Data Object (186 rækker, +151 vs Feb)** — DataObjectFactSheet-collection er **tom (0)** i .bin. Var aldrig importeret.
5. **P-PlatformData (450 rækker)** — moduler/sub-platforme på ITComponents. Vi har ModuleFactSheet-collection (også tom).
6. **FRFS-Manufacturing Capabilities (nyt ark!)** — kun i den nye fil. Indeholder muligvis ekstra capability-detaljer eller OT-relateret struktur vi har overset.
7. **Security Assesment (24 detaljerede rækker)** — kun lette felter på app er populated; den fulde assessment ikke.
8. **Processer280125 (1289 rækker procesdokumenter)** — kun procesnavne importeret; dokument-referencer ikke.
9. **CleanUp Hardware Departments (nyt ark!)** — ny i nuværende fil; ikke importeret.

## C. KamstrupData kant-tilfælde
1. **21 skippede mappings** (capability-key matcher ikke B-Business Capability) — list de 21 cap-keys, slå op i Excel om de findes med anden stavning eller om de er fejl. Konsekvens: 21 mapping-relationer tabt.
2. **KamstrupData rækker uden `IdOrg`** — vi havde 100% IdOrg-dækning i kilde; verificér igen direkte mod .bin (alle 5872 har `OrganizationId` sat).
3. **KamstrupData rækker uden app** — skippet i source-parser; tæl hvor mange (kunne være mapping-rækker uden app-reference).
4. **Dublet-mappings:** to mapping-rækker med samme `(app, cap, org, process, vs)` kombination → samme deterministisk-GUID → kollideret i sættet. Skal verificeres mod kildens 5893.

## D. Custom fields / ConfigurableLists (afhænger af CustomerSettings.bin)
1. **App.CustomFields ColumnIds:** mappings/apps har `CustomFieldValue(ColumnId, value)` — for hver brugt ColumnId, findes der en `CustomColumnDefinition` i CustomerSettings? (Kritisk hvis exporten genimporteres uden CustomerSettings.bin.)
2. **OrgType-værdier:** vi sætter `"Country" / "Business Unit" / "Department" / "Team"` — eksisterer disse som ConfigurableList-værdier i CustomerSettings? Hvis ej, viser UI'en blanke labels.
3. **LifecycleStage-labels** ("1-Strategic", "2-Important application", …) — registreret som ConfigurableList?
4. **Tier-værdier** (T0/T1-D — NY kolonne 20) — registreret? Det er nye værdier vi nu sætter.

## E. Binære relationer (ud over ApplicationContextMapping)
Vores scope berørte kun ApplicationContextMappingFactSheets. De "klassiske" relationer (FactSheet.ParentFactSheetsIds — App→BC, App→Org, App→Process) blev IKKE genopbygget.
1. **App.ParentFactSheetsIds:** indeholder de gamle ref'er fra forrige import? Hvis ja, peger de på de nye orgs (forskellige GUIDs end gamle orgs) → danglende refs på 1109 apps?
2. **BC.ParentFactSheetsIds:** BC-hierarki er via HierarchyParentId/Children (verificeret). Anden brug?
3. **Org.ParentFactSheetsIds:** orgs har vi nyimporteret; ParentFactSheetsIds bør være tom (vi brugte kun HierarchyChildrenIds).

→ Konsekvens: hvis UI'en bruger ParentFactSheetsIds til andre views, kan de vise gamle eller danglende refs.

## F. App-konsistens (instans vs. Excel)
Allerede verificeret (37 i OmniGaze ikke i Excel; 7 i Excel ikke i OmniGaze; bevidst valg). Restpunkter:
1. **2 case-varianter** (Omnia/OMNIA, ReadyAPI/READyAPI) — er det reelt forskellige apps eller skal de merges?
2. **20 dublet-DisplayNames i instansen** (1119 → 1099 distinkte) — list dem og afgør om legit (forskellige varianter) eller fejl.

## G. UI spot-checks (visuel verifikation)
1. **Capabilities-side (BC-tree):** L0 `Operations` viser OT Hosting + alle 6 OT L2-børn? Den ANDEN "Operations" (under Corporate Services › Digital Platform and Operations) — er den stadig der med sine IT-børn? Begge skal være OK; OT må kun hænge under den rigtige.
2. **Organization-detalje:** klik på en Team-node (fx DK10 › Sales & Marketing › Marketing) — vises ægte parent-breadcrumb + Applications/Capabilities-relationer?
3. **5-10 random mappings end-to-end:** verificér KamstrupData-rækken stemmer med factsheet-detaljen (TIME, Criticality, ValidFrom, Projects, Comment, alle 5 refs).
4. **Application Context Mappings page:** filtrér "Application = Speedship" — 0 unresolved efter fix?
5. **OT Manufacturing (under L0 Manufacturing):** L2/L3-børn intakte?

## H. Export-zip-integritet
1. **Hash + size match** mellem zip-indhold og kildens `FactSheets.bin` (591.699 bytes, mtime 22:22).
2. **Round-trip test:** udpak zip på et midlertidigt sted → re-deserialiser → samme felt-tællinger som .bin'en på disk.
3. **Skal CustomerSettings.bin med?** Hvis target-instans ikke kender Kamstrup-CustomColumnDefinitions / OrgType-ConfigurableList → custom fields og org-type-labels vises ikke. Beslutning: tilføj som anden fil i exportbundle.

## I. Plan for udførelse (rækkefølge)
1. **A1-A3 + B5** (intern integritet): direkte fra .bin'en (jeg har allerede parseren) — kan køres uden at appen kører.
2. **C1 + C4** (KamstrupData-fund): re-parse Excel + sammenlign med .bin'ens mapping-set.
3. **D1-D4** (CustomerSettings-afhængighed): deserialisér CustomerSettings.bin + verificér ColumnId/ConfigurableList-coverage.
4. **E1** (App.ParentFactSheetsIds dangler?): tjek refs vs nye org-GUIDs.
5. **F1-F2** (apps stavevarianter/dubletter): rapport.
6. **G** (UI-spot-check): start app, Playwright-snapshots på 5-6 sider.
7. **H1-H3** (export-integritet): hash + round-trip.

Hver opgave producerer en kort "fund-rapport" — det hele samles til en endelig "intet overset"-attest, eller en liste over ting der skal handles på.

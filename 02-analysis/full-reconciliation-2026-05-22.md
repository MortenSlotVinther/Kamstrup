# Kamstrup: fuld Excel ↔ OmniGaze reconciliation (alle ark)

**Dato:** 2026-05-22 (efter scoped import + tilføjelse af mapping-refererede apps)
**Instans:** localhost:5000 (Kamstrup-data), kilde: `Kamstrup_Business-Capability-Map.xlsx`

## Antal pr. entitet

| Excel-ark | Excel | OmniGaze | Match | Kilde for OmniGaze-tal |
|---|---|---|---|---|
| B-Business Capability | 672 rækker → 678 (m. 8 L0-grupper) | **678** | ✅ | OData live |
| O-Organization | 169 rækker → 282 hierarki | **282** | ✅ | instans (importeret) |
| C-Business Context (Processer) | 654 | **654** | ✅ | instans/JSON |
| Value Streams | 12 | **12** | ✅ | JSON |
| KamstrupData (Context Mappings) | 5893 rækker (21 skippet, ukendt cap-key) | **5872** | ✅ | instans (importeret) |
| P_Platform | 34 | 34 findes (delmængde af 512 ITComponents) | ✅ (delmængde) | OData |
| A-Applications + _Removed | 1001 + 74 = **1069 distinkte** | **1119 (1099 distinkte)** | ❌ | OData live |
| Providers | (afledt ~483) | 486 | ~ (3 diff) | OData |
| ITComponents (total) | 34 (kun platforme) | 512 | ❌ (inkl. opdaget infra) | OData |

## Applications — detaljeret diff (det vigtigste fund)

OmniGaze har **37 apps der IKKE er i Excel** — ser ud som opdagede/miljø-specifikke instanser fra en anden kilde (ikke Excel-porteføljen):
`EKS-DEV/PROD/TEST, IFS-DK(+module1/2), OMNIA + OMNIA-AENB/AENP/AENR/C0306..C0702/HSTZ3..7, READY-CA01/DE02/DK01/DK13/DK15/GSS01/QA02/QA03/SE01/SG01/US03/US04, READyAPI, OmniGaze, OmniGaze-PoC`

Excel har **7 apps der IKKE er i OmniGaze**:
- Genuint manglende (5): `Azure event grid`, `EDNG electronic deliivery note generator`, `Kamstrup Analytics (bespoke malaga)`, `Oracle Subscribtion Management`, `Sharegate`
- Kun **case/stavevariant** (2): `Omnia` (Excel) vs `OMNIA` (OmniGaze); `ReadyAPI` (Excel) vs `READyAPI` (OmniGaze)

Desuden: **20 dublet-navne** i OmniGaze (1119 count vs 1099 distinkte).

## Tolkning
- BC, Org, Processer, Value Streams, Context Mappings og Excel-platformene **matcher Excel** ✅.
- **Applications + ITComponents afviger**, fordi den lokale instans indeholder **opdaget/scannet data + en tidligere app-import** der ikke kommer fra det nuværende Excel (OMNIA-/READY-/EKS-instanser, 512 ITComponents = servere/infra). Dette blev bevidst ikke rørt (scope = BC+Org+Mappings; apps urørt udover de 10 mapping-refererede der blev tilføjet).

## Kendte data-kvalitetsnoter (fra tidligere audit, gælder stadig)
- NIS2-Criticality-kolonnen er tom i Excel → NIS2 sat på 0 capabilities.
- 21 KamstrupData-rækker peger på capability-keys der ikke findes i B-Business Capability (skippet).

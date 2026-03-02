# Kamstrup EA Mapping Meeting - Transcript Summary

**Date:** February 5, 2026 (meeting date in transcript)  
**Duration:** 50m 41s  
**Participants:**
- **Morten Vinther** (OmniGaze)
- **Frank Friis** (Kamstrup - EA Lead)
- **Steen Breum Møller** (Kamstrup - EA Team)

---

## Executive Summary

This was a deep-dive demo meeting where Frank Friis walked through Kamstrup's comprehensive Excel-based EA repository. The data model is exceptionally granular - tracking applications mapped to business capabilities down to Level 3, with organizational context (country, business unit, department, team), business process mapping, Gartner TIME ratings from business users, and lifecycle management. OmniGaze was positioned as a potential EA tool to migrate this data into.

---

## Key Discussion Points

### 1. **Kamstrup's Excel-Based EA Repository**
Frank has built an impressive Excel-based EA system with multiple interconnected sheets:
- **Organization sheet**: 4-level hierarchy (Country → Business Unit → Department → Team)
- **Business Context sheet**: Processes from Lean IX model (36 main processes, ~300 sub-processes)
- **Application Cost sheet**: License management, contracts, vendor info, cost tracking (~97% app coverage)
- **Data sheet (main)**: The core mapping table linking all entities

### 2. **Data Model Architecture**
- **Unique ID approach**: Combines multiple columns to create unique keys (no separate ID column)
- **Color coding**: Salmon = user input fields, Yellow = auto-populated from other sheets
- **Lifecycle management**: From-date and To-date columns for tracking application transitions
- **Multi-dimensional**: Same application can appear multiple times (different capabilities, orgs, processes)

### 3. **Granularity Level**
- Business capabilities tracked to Level 3 (where applicable)
- Organization tracked down to team level
- Process mapping to sub-process level
- All this **per application** - resulting in many rows per app

### 4. **Business Ratings**
- **Gartner TIME model** (Invest, Tolerate, Migrate, Eliminate) - collected from business users
- **Business Criticality** ratings - in user context (not global)
- Functional/Technical fit considered but simplified to 4-level TIME for user clarity

### 5. **Value Streams & Projects**
- Value streams mapped to capabilities
- Value stream ordering for presentation control
- Project/initiative tags to show transformation scope

### 6. **Platform Strategy**
- Strategic vs non-strategic platforms identified
- Platform capabilities mapped (IFS example: identifying unused modules)
- Goal: Transform business into platform-centric architecture

---

## Opportunities for OmniGaze

### Immediate Opportunities
1. **Data Migration Project**
   - Kamstrup needs to migrate from Excel to a proper EA tool
   - Current Excel setup is sophisticated but has limitations (no multi-user, no surveys)
   - **Action**: Provide gap analysis and estimate for migrating the data model

2. **Flexible Data Model**
   - Kamstrup values Excel's flexibility - any new tool must match this
   - Quote from Steen: "It's just a table with column names where you can take a perspective on each column"
   - OmniGaze's approach aligns with this philosophy

3. **AI-Powered Surveys** 
   - Kamstrup expressed strong interest in automated data collection
   - OmniGaze's chat-based survey approach (via Teams/email) impressed them
   - This addresses a major pain point: building and managing traditional surveys

### Strategic Opportunities
1. **Reference Customer Potential**
   - Frank's framework could become a template for other enterprises
   - Quote from Morten: "This is interesting for us... you could push other EA vendors to come closer to this model"

2. **EA Hjørnet Presentation**
   - Kamstrup invited to present at EA Hjørnet (EA corner networking event)
   - Would showcase practical EA implementation
   - Morten is looking for a Jutland host for ~30-35 people

3. **Process Integration** 
   - Kamstrup has separate process management tool
   - Currently just reference links from EA to process tool
   - Integration opportunity (though not a hard requirement)

---

## Action Items

### OmniGaze Actions
| Action | Owner | Timeline |
|--------|-------|----------|
| Get access to Kamstrup's Excel sheets (under NDA) | Morten | Immediate |
| Perform gap analysis: Excel model vs OmniGaze data model | Morten/Team | ~1 week |
| Provide estimate for full model implementation | Morten/Team | ~1 week |
| Identify required lookup tables for granularity | Morten/Team | Part of gap analysis |

### Kamstrup Actions
| Action | Owner | Timeline |
|--------|-------|----------|
| Share full Excel repository with OmniGaze | Frank | After meeting |
| Discuss EA Hjørnet presentation internally | Frank/Steen | TBD |
| Communicate timeline delay to other vendors | Frank | Soon |

---

## Timeline & Decision Process

- **Original timeline**: Decision was expected before Christmas (delayed)
- **New timeline**: No decision before summer holiday due to priority 1 projects
- **Reason for delay**: Higher priority projects that actually depend on having EA inventory
- **Key insight**: Their existing inventory enables them to delay tool selection without impact

---

## Commitments Made

1. **Morten committed** to:
   - Providing a gap analysis within approximately 1 week
   - Making a "proper" estimate (not just quick guess)
   - Working with Christian on infrastructure/asset integration
   - Being "humble" as vendor and delivering quality

2. **Frank/Steen committed** to:
   - Sharing the Excel repository
   - Internal discussion about hosting EA Hjørnet
   - Keeping OmniGaze in the loop despite timeline changes

---

## Competitive Intelligence

### Other Vendors in Play
- **Lean IX** - Previously evaluated, had data import limitations at granular level
- **Ardoq** - Mentioned as flexible but had constraints they didn't expect
- Decision process has included multiple vendors; OmniGaze came in as "wildcard"

### Kamstrup's Requirements
1. Must handle their granularity level (Level 3 capabilities + team-level org)
2. Data import/export must work at full detail level
3. Flexibility comparable to Excel
4. Survey/data collection capabilities
5. Power BI integration for presentation layer

---

## Notable Quotes

> "Jeg er lidt imponeret af det her det du har bygget Frank. Jeg har ikke set noget lignende komme til det niveau i excel." 
> *(I'm a bit impressed by what you've built Frank. I haven't seen anything similar reach this level in Excel.)* - Morten

> "Det her det bliver lidt ping pong... Vi er lidt ydmyge som leverandør her"
> *(This becomes a bit back and forth... We're a bit humble as vendor here)* - Morten

> "I er simpelthen værter for EA hjørnet på et tidspunkt inden så længe"
> *(You'll definitely be hosts for EA hjørnet at some point soon)* - Morten

---

## Technical Notes

### Data Model Observations
- The model is essentially a **fact table** with dimensional lookups
- Very similar to data warehouse star schema thinking
- Presentation layer logic pushed to Excel (ordering, filtering)
- Power BI used for visualization/dashboards

### Integration Points
- Process management system (separate, linked via reference)
- Supply chain (for contract/cost updates)
- E-signing tool (contract period sync)
- Microsoft Graph potential (for vendor cost aggregation)

---

## Follow-up Meeting Needed

Topics for next meeting:
1. Review gap analysis results
2. Demo OmniGaze's current capabilities
3. Discuss AI survey feature in detail
4. Timeline for potential pilot

---

*Summary created: January 30, 2025*
*Source: Email attachment "Omnigace mapning-20260205_090842-Meeting Recording.docx"*

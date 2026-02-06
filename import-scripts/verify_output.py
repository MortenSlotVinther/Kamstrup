#!/usr/bin/env python3
"""Quick verification of import output."""
import json
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

with open(os.path.join(BASE, "applications_active.json"), encoding="utf-8") as f:
    apps = json.load(f)

with open(os.path.join(BASE, "applications_removed.json"), encoding="utf-8") as f:
    removed = json.load(f)

with open(os.path.join(BASE, "providers_extracted.json"), encoding="utf-8") as f:
    providers = json.load(f)

print("=" * 60)
print("  Phase 3 Output Verification")
print("=" * 60)

# Counts
print(f"\nActive applications: {len(apps)}")
print(f"Removed applications: {len(removed)}")
print(f"Total: {len(apps) + len(removed)}")
print(f"Unique providers: {len(providers)}")

# Lifecycle distribution
from collections import Counter
stages = Counter(a.get("LifecycleStage") for a in apps)
print("\nLifecycle distribution:")
for k, v in sorted(stages.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Install type
host_types = Counter(a["HostedOn"]["Criticality"] for a in apps)
print("\nHosting types:")
for k, v in sorted(host_types.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Spot-check IFS ERP
ifs = next(a for a in apps if a["DisplayName"] == "IFS ERP")
print("\n--- IFS ERP spot-check ---")
print(f"  Category: {ifs['Category']}")
print(f"  TIME: {ifs['PortFolioStrategy']['TIME']}")
print(f"  HostedOn: {ifs['HostedOn']['Criticality']}")
print(f"  Lifecycle: {ifs['LifecycleStage']}")
print(f"  UserBase: {ifs['UserBase']['Size']}")
print(f"  Security: {ifs['SecurityAssessment']['Status']}, Debt={ifs['SecurityAssessment']['DebtLevel']}")
print(f"  CrownJewel: {'CrownJewel' in ifs.get('OrganizationTags', [])}")
print(f"  Children: {len(ifs.get('HierarchyChildrenIds', []))}")

# Cloud app check
cloud_apps = [a for a in apps if a["HostedOn"]["Criticality"] == "SaaS"]
if cloud_apps:
    c = cloud_apps[0]
    print(f"\n--- Cloud app check: {c['DisplayName']} ---")
    print(f"  HostedOn: {c['HostedOn']['Criticality']} (correct: SaaS)")

# AI check
ai_apps = [a for a in apps if a["AIClassification"]["UsesAI"]]
print(f"\n--- AI apps ({len(ai_apps)}) ---")
for a in ai_apps:
    print(f"  {a['DisplayName']}: Risk={a['AIClassification']['RiskLevel']}")

# Phase out check
po = [a for a in apps if a.get("LifecycleStage") == "8-Phase out"]
print(f"\n--- 8-Phase out apps ({len(po)}) ---")
if po:
    print(f"  Example: {po[0]['DisplayName']}")

# Security debt investigate
inv = [a for a in apps if a["SecurityAssessment"]["DebtLevel"] == "Investigate"]
print(f"\n--- Security debt=Investigate ({len(inv)}) ---")
for a in inv[:3]:
    print(f"  {a['DisplayName']}")

# Hierarchy check
parents = [a for a in apps if a.get("_HierarchyParentId")]
children_parents = [a for a in apps if a.get("HierarchyChildrenIds")]
print(f"\n--- Hierarchy ---")
print(f"  Apps with parent: {len(parents)}")
print(f"  Apps with children: {len(children_parents)}")
for a in children_parents:
    kids = [next((x["DisplayName"] for x in apps if x["Id"] == cid), "?") for cid in a["HierarchyChildrenIds"]]
    print(f"  {a['DisplayName']} -> {kids}")

# Removed apps check
print(f"\n--- Removed apps ({len(removed)}) ---")
all_retired = all(a["Retired"] for a in removed)
print(f"  All marked Retired: {all_retired}")
with_eol = sum(1 for a in removed if a["LifeCycle"]["EndOfLife"] is not None)
print(f"  With EndOfLife date: {with_eol}")
if removed:
    r = removed[0]
    print(f"  First: {r['DisplayName']}, EOL={r['LifeCycle']['EndOfLife']}")

# Successors
with_succ = [a for a in apps if a.get("SuccessorId")]
print(f"\n--- Successors ---")
print(f"  Active apps with successor: {len(with_succ)}")
for a in with_succ:
    succ_names = []
    for sid in a["SuccessorId"]:
        sn = next((x["DisplayName"] for x in apps if x["Id"] == sid), "?")
        succ_names.append(sn)
    print(f"  {a['DisplayName']} -> {succ_names}")

# Custom fields
apps_with_custom = sum(1 for a in apps if a.get("CustomFields"))
print(f"\n--- Custom Fields ---")
print(f"  Apps with custom field values: {apps_with_custom}")

print("\n" + "=" * 60)
print("  Verification Complete")
print("=" * 60)

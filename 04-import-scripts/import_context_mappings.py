#!/usr/bin/env python3
"""
Phase 5: Kamstrup Context Mapping Import Script
================================================
Parses the KamstrupData sheet (~5,395 rows) and creates one
ApplicationContextMappingFactSheet per row — the n-ary mapping that
preserves contextual TIME and Criticality per App-Capability-Org combination.

Reads lookups from Phase 2/3/4 output and generates context-mappings.json.

Usage:
    python import_context_mappings.py [--excel PATH] [--output-dir DIR]

Author: Ole (Subagent)
Date: 2026-02-09
"""

import json
import os
import sys
import uuid
import argparse
from datetime import datetime

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl is required. Install with: pip install openpyxl")
    sys.exit(1)

# ─── Configuration ──────────────────────────────────────────────────────────

EXCEL_PATH = r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# Deterministic GUID namespace (same as other import scripts for consistency)
NAMESPACE_KAMSTRUP = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")

# Country code → country display name (from O-Organization / Phase 4)
COUNTRY_CODE_MAP = {
    "DK10": "Denmark",
    "DK20": "Denmark",
    "CH10": "Switzerland",
    "ES10": "Spain",
    "FR10": "France",
    "NL10": "Netherlands",
    "NO10": "Norway",
    "SE10": "Sweden",
    "US10": "United States",
    "MY10": "Malaysia",
    "PL10": "Poland",
    "AT10": "Austria",
    "CA10": "Canada",
    "CN10": "China",
    "DE10": "Germany",
    "FI10": "Finland",
    "IT10": "Italy",
}

# TIME mapping: Excel string → OmniGaze StrategyEnum (int)
TIME_MAP = {
    "tolerate": 1,
    "invest": 2,
    "migrate": 3,
    "eliminate": 4,
}

# Criticality mapping: Excel string → OmniGaze CriticalityEnum (int)
CRITICALITY_MAP = {
    "administrative service": 1,
    "business operational": 2,
    "business critical": 3,
    "mission critical": 4,
}

# ─── Helpers ─────────────────────────────────────────────────────────────────


def deterministic_guid(category: str, key: str) -> str:
    """Generate a deterministic GUID from category + key using UUID5."""
    composite = f"{category}::{key}"
    return str(uuid.uuid5(NAMESPACE_KAMSTRUP, composite))


def safe_str(value) -> str:
    """Convert cell value to trimmed string, or empty string if None."""
    if value is None:
        return ""
    return str(value).strip()


def safe_int(value) -> int:
    """Convert value to int, return 0 on failure."""
    if value is None:
        return 0
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return 0


def parse_date(value) -> str:
    """Parse date value from Excel. Returns ISO string or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    s = safe_str(value)
    if not s:
        return None
    # Try common date formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return None


def load_lookups(output_dir: str) -> dict:
    """Load all lookup dictionaries."""
    lookups_path = os.path.join(output_dir, "lookups-phase4.json")
    app_path = os.path.join(output_dir, "app_number_to_guid.json")

    with open(lookups_path, "r", encoding="utf-8") as f:
        lookups = json.load(f)

    with open(app_path, "r", encoding="utf-8") as f:
        app_lookup = json.load(f)

    return {
        "capabilities": lookups["business_capability_ids"],
        "organizations": lookups["organization_ids"],
        "processes": lookups["process_ids"],
        "value_streams": lookups["value_stream_ids"],
        "applications": app_lookup,
    }


def resolve_app(app_str: str, app_lookup: dict) -> str:
    """Resolve application string (like '1 - IFS ERP') to GUID."""
    app_str = safe_str(app_str)
    if not app_str:
        return None
    if app_str in app_lookup:
        return app_lookup[app_str]
    parts = app_str.split(" - ", 1)
    if parts[0].strip() in app_lookup:
        return app_lookup[parts[0].strip()]
    return None


def resolve_org(country_code: str, business_area: str, dept_team: str,
                org_lookup: dict) -> str:
    """
    Resolve organization from KamstrupData columns.
    Try most specific first, fall back to less specific.
    """
    country_code = safe_str(country_code)
    business_area = safe_str(business_area)
    dept_team = safe_str(dept_team)

    # Map country code to name
    country_name = COUNTRY_CODE_MAP.get(country_code, "")
    if not country_name:
        prefix = country_code[:2] if len(country_code) >= 2 else ""
        for code, name in COUNTRY_CODE_MAP.items():
            if code.startswith(prefix):
                country_name = name
                break
    if not country_name:
        return None

    # Try 3-part key with dept
    if dept_team:
        for key, guid in org_lookup.items():
            if key.startswith(f"{country_name}::") and key.endswith(f"::{dept_team}"):
                return guid

    # Try 3-part key with BA
    if business_area:
        for key, guid in org_lookup.items():
            if key.startswith(f"{country_name}::") and key.endswith(f"::{business_area}"):
                return guid

    # Try 2-part key
    if business_area:
        key2 = f"{country_name}::{business_area}"
        if key2 in org_lookup:
            return org_lookup[key2]

    # Fall back to country
    if country_name in org_lookup:
        return org_lookup[country_name]

    return None


def resolve_process(process_str: str, process_lookup: dict) -> str:
    """Resolve process string (like 'P01-Strategy--') to GUID."""
    process_str = safe_str(process_str)
    if not process_str:
        return None
    if process_str in process_lookup:
        return process_lookup[process_str]
    return None


def resolve_value_stream(vs_str: str, vs_lookup: dict) -> str:
    """Resolve value stream name to GUID."""
    vs_str = safe_str(vs_str)
    if not vs_str or vs_str.lower() == "n/a":
        return None
    if vs_str in vs_lookup:
        return vs_lookup[vs_str]
    return None


def map_time(value: str) -> int:
    """Map Gartner TIME string to StrategyEnum int."""
    v = safe_str(value).lower()
    return TIME_MAP.get(v, 0)  # 0 = Unmapped


def map_criticality(value: str) -> int:
    """Map Business Criticality string to CriticalityEnum int."""
    v = safe_str(value).lower()
    return CRITICALITY_MAP.get(v, 0)  # 0 = Unmapped


# ─── Main Import ─────────────────────────────────────────────────────────────

def import_context_mappings(excel_path: str, output_dir: str):
    """Parse KamstrupData sheet and create context mapping factsheets."""
    print("=" * 60)
    print("Phase 5: Application Context Mapping Import")
    print("=" * 60)

    # Load lookups
    print("\nLoading lookups...")
    lookups = load_lookups(output_dir)
    cap_lookup = lookups["capabilities"]
    org_lookup = lookups["organizations"]
    process_lookup = lookups["processes"]
    vs_lookup = lookups["value_streams"]
    app_lookup = lookups["applications"]

    print(f"  Capabilities: {len(cap_lookup)} entries")
    print(f"  Organizations: {len(org_lookup)} entries")
    print(f"  Processes: {len(process_lookup)} entries")
    print(f"  Value Streams: {len(vs_lookup)} entries")
    print(f"  Applications: {len(app_lookup)} entries")

    # Open Excel
    print(f"\nOpening workbook: {excel_path}")
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb["KamstrupData"]

    mappings = []
    warnings = {
        "unresolved_apps": set(),
        "unresolved_caps": set(),
        "unresolved_orgs": set(),
        "unresolved_processes": set(),
        "unresolved_value_streams": set(),
    }
    stats = {
        "total_rows": 0,
        "rows_skipped_no_app": 0,
        "rows_skipped_no_cap": 0,
        "time_mapped": 0,
        "criticality_mapped": 0,
        "orgs_resolved": 0,
        "processes_resolved": 0,
        "value_streams_resolved": 0,
    }

    print("\nProcessing KamstrupData rows...")
    for row in ws.iter_rows(min_row=5, values_only=True):
        stats["total_rows"] += 1

        # Column extraction (0-indexed)
        from_date_raw = row[1] if len(row) > 1 else None      # col B: Active from date
        end_date_raw = row[2] if len(row) > 2 else None        # col C: End date
        cap_key = safe_str(row[3] if len(row) > 3 else None)   # col D: IdLevel123
        cap_l1 = safe_str(row[4] if len(row) > 4 else None)    # col E: Capability L1
        cap_l2 = safe_str(row[5] if len(row) > 5 else None)    # col F: Capability L2
        cap_l3 = safe_str(row[6] if len(row) > 6 else None)    # col G: Capability L3
        # col H (index 7) is "Not used"
        cc = safe_str(row[8] if len(row) > 8 else None)        # col I: CountryCode
        ba = safe_str(row[9] if len(row) > 9 else None)        # col J: Business Area
        dept = safe_str(row[10] if len(row) > 10 else None)     # col K: DepartmentTeam
        app_str = safe_str(row[11] if len(row) > 11 else None)  # col L: NoApplication
        app_name = safe_str(row[12] if len(row) > 12 else None) # col M: Application Name
        time_str = safe_str(row[13] if len(row) > 13 else None) # col N: Gartner TIME
        crit_str = safe_str(row[14] if len(row) > 14 else None) # col O: Business Criticality
        proc_str = safe_str(row[15] if len(row) > 15 else None) # col P: NoProcess
        vs_str = safe_str(row[16] if len(row) > 16 else None)   # col Q: Value Stream
        vs_order = safe_int(row[17] if len(row) > 17 else None)  # col R: Value Stream Order
        projects = safe_str(row[18] if len(row) > 18 else None)  # col S: Projects
        comment = safe_str(row[19] if len(row) > 19 else None)   # col T: Comment

        # Skip empty rows
        if not cap_key and not app_str:
            continue

        # Resolve Application
        app_guid = resolve_app(app_str, app_lookup)
        if not app_guid:
            stats["rows_skipped_no_app"] += 1
            warnings["unresolved_apps"].add(app_str)
            continue

        # Resolve Business Capability
        cap_guid = cap_lookup.get(cap_key)
        if not cap_guid:
            stats["rows_skipped_no_cap"] += 1
            warnings["unresolved_caps"].add(cap_key)
            continue

        # Resolve Organization (optional)
        org_guid = None
        if cc:
            org_guid = resolve_org(cc, ba, dept, org_lookup)
            if org_guid:
                stats["orgs_resolved"] += 1
            else:
                warnings["unresolved_orgs"].add(f"{cc}|{ba}|{dept}")

        # Resolve Process (optional)
        proc_guid = None
        if proc_str:
            proc_guid = resolve_process(proc_str, process_lookup)
            if proc_guid:
                stats["processes_resolved"] += 1
            else:
                warnings["unresolved_processes"].add(proc_str)

        # Resolve Value Stream (optional)
        vs_guid = None
        if vs_str and vs_str.lower() != "n/a":
            vs_guid = resolve_value_stream(vs_str, vs_lookup)
            if vs_guid:
                stats["value_streams_resolved"] += 1
            else:
                warnings["unresolved_value_streams"].add(vs_str)

        # Map TIME and Criticality
        time_val = map_time(time_str)
        crit_val = map_criticality(crit_str)
        if time_val > 0:
            stats["time_mapped"] += 1
        if crit_val > 0:
            stats["criticality_mapped"] += 1

        # Parse dates
        valid_from = parse_date(from_date_raw)
        valid_to = parse_date(end_date_raw)

        # Generate deterministic GUID from composite key
        # Use app+cap+org+process+vs as the key to ensure uniqueness per context
        composite_key = f"{app_guid}|{cap_guid}|{org_guid or ''}|{proc_guid or ''}|{vs_guid or ''}"
        mapping_guid = deterministic_guid("ContextMapping", composite_key)

        # Build capability name for display
        cap_name_parts = [p for p in [cap_l1, cap_l2, cap_l3] if p and p != "0"]
        cap_display = " > ".join(cap_name_parts) if cap_name_parts else cap_key

        # Generate DisplayName
        display_name = f"{app_name or app_str} -> {cap_display}"
        if org_guid and cc:
            country_name = COUNTRY_CODE_MAP.get(cc, cc)
            display_name += f" ({country_name})"

        mapping = {
            "Id": mapping_guid,
            "DisplayName": display_name,
            "FactSheetType": "ApplicationContextMappingFactSheet",
            "ApplicationId": app_guid,
            "BusinessCapabilityId": cap_guid,
            "OrganizationId": org_guid,
            "ProcessId": proc_guid,
            "ValueStreamId": vs_guid,
            "ContextualTIME": time_val,
            "ContextualCriticality": crit_val,
            "ValidFrom": valid_from,
            "ValidTo": valid_to,
            "Projects": projects if projects else None,
            "Comment": comment if comment else None,
            "ValueStreamOrder": vs_order,
        }
        mappings.append(mapping)

    wb.close()

    # ─── Output ──────────────────────────────────────────────────────────

    output_path = os.path.join(output_dir, "context-mappings.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 60)
    print("CONTEXT MAPPING IMPORT SUMMARY")
    print("=" * 60)
    print(f"  Total rows processed:     {stats['total_rows']}")
    print(f"  Context mappings created:  {len(mappings)}")
    print(f"  Skipped (no app):         {stats['rows_skipped_no_app']}")
    print(f"  Skipped (no capability):  {stats['rows_skipped_no_cap']}")
    print(f"  TIME mapped:              {stats['time_mapped']}")
    print(f"  Criticality mapped:       {stats['criticality_mapped']}")
    print(f"  Organizations resolved:   {stats['orgs_resolved']}")
    print(f"  Processes resolved:       {stats['processes_resolved']}")
    print(f"  Value Streams resolved:   {stats['value_streams_resolved']}")

    if warnings["unresolved_apps"]:
        print(f"\n  [!] Unresolved apps ({len(warnings['unresolved_apps'])}): {sorted(list(warnings['unresolved_apps']))[:10]}")
    if warnings["unresolved_caps"]:
        print(f"  [!] Unresolved capabilities ({len(warnings['unresolved_caps'])}): {sorted(list(warnings['unresolved_caps']))[:10]}")
    if warnings["unresolved_orgs"]:
        print(f"  [!] Unresolved orgs ({len(warnings['unresolved_orgs'])}): {sorted(list(warnings['unresolved_orgs']))[:10]}")
    if warnings["unresolved_processes"]:
        print(f"  [!] Unresolved processes ({len(warnings['unresolved_processes'])}): {sorted(list(warnings['unresolved_processes']))[:10]}")
    if warnings["unresolved_value_streams"]:
        print(f"  [!] Unresolved value streams ({len(warnings['unresolved_value_streams'])}): {sorted(list(warnings['unresolved_value_streams']))[:10]}")

    print(f"\n  Output: {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print("=" * 60)

    # Save warnings for debugging
    warnings_out = {k: sorted(list(v)) for k, v in warnings.items()}
    warnings_path = os.path.join(output_dir, "context-mapping-warnings.json")
    with open(warnings_path, "w", encoding="utf-8") as f:
        json.dump(warnings_out, f, indent=2, ensure_ascii=False)

    return mappings


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 5: Kamstrup Context Mapping Import")
    parser.add_argument("--excel", default=EXCEL_PATH, help="Path to Kamstrup Excel file")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    mappings = import_context_mappings(args.excel, args.output_dir)
    print(f"\nDone. {len(mappings)} context mappings generated.")

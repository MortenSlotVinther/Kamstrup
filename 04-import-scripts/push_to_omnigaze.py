#!/usr/bin/env python3
"""
Kamstrup Phase 2 — Push to OmniGaze via MCP API
=================================================
Takes the JSON output from kamstrup_import.py and creates factsheets
in OmniGaze using the MCP client API.

Prerequisites:
  - OmniGaze running at internal.omnigaze.com with Phase 0+1 code deployed
  - MCP client script at the standard path
  - Output from kamstrup_import.py in ./output/

Usage:
    python push_to_omnigaze.py [--input DIR] [--dry-run]
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

MCP_CLIENT = r"F:\RootContext\OmniGazeEA\.claude\skills\omnigaze-internal\scripts\mcp_client.py"

# Map our FactSheetType names to MCP factSheetTypeName
TYPE_MAP = {
    "ValueStreamFactSheet": "ValueStream",
    "BusinessCapabilityFactSheet": "BusinessCapability",
    "OrganizationFactSheet": "Organization",
    "ProcessFactSheet": "Process",
    "ITComponentFactSheet": "ITComponent",
    "ProviderFactSheet": "Provider",
}


def call_mcp(tool: str, args_dict: dict, dry_run: bool = False) -> dict:
    """Call MCP client and return parsed JSON response."""
    args_json = json.dumps(args_dict)
    cmd = [
        sys.executable, MCP_CLIENT,
        "call", "-t", tool, "-a", args_json
    ]

    if dry_run:
        print(f"  [DRY-RUN] {tool}({args_json[:120]}...)")
        return {"success": True, "dryRun": True}

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr[:500]}
        return json.loads(result.stdout) if result.stdout.strip() else {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_factsheet(fs: dict, dry_run: bool) -> bool:
    """Create a single factsheet via MCP."""
    fs_type = TYPE_MAP.get(fs["FactSheetType"], fs["FactSheetType"])

    # Build creation args
    create_args = {
        "factSheetTypeName": fs_type,
        "displayName": fs["DisplayName"],
    }

    # Add optional fields
    if fs.get("RichDescription"):
        create_args["richDescription"] = fs["RichDescription"]
    if fs.get("Responsible"):
        create_args["responsible"] = fs["Responsible"]
    if fs.get("ShortDescription"):
        create_args["shortDescription"] = fs["ShortDescription"]

    # Organization-specific: OrgType, CountryCode
    if fs.get("OrgType"):
        # Normalize "BusinessUnit" → "Business Unit" to match configurable list
        org_type = fs["OrgType"]
        if org_type == "BusinessUnit":
            org_type = "Business Unit"
        create_args["orgType"] = org_type
    if fs.get("CountryCode"):
        create_args["countryCode"] = fs["CountryCode"]

    result = call_mcp("CreateFactSheet", create_args, dry_run)

    if not result.get("success", True) and not dry_run:
        print(f"  ✗ Failed to create {fs_type} '{fs['DisplayName']}': {result.get('error', 'unknown')}")
        return False

    return True


def set_hierarchy(parent_id: str, child_ids: list, dry_run: bool) -> bool:
    """Set hierarchy children via MCP."""
    args = {
        "factSheetId": parent_id,
        "childIds": child_ids,
    }
    result = call_mcp("ManageFactSheetHierarchyChildren", args, dry_run)
    return result.get("success", True)


def push_file(filepath: str, dry_run: bool) -> tuple:
    """Push all factsheets from a JSON file. Returns (created, failed)."""
    with open(filepath, "r", encoding="utf-8") as f:
        factsheets = json.load(f)

    created = 0
    failed = 0

    for fs in factsheets:
        if create_factsheet(fs, dry_run):
            created += 1
        else:
            failed += 1
        # Rate limit
        if not dry_run:
            time.sleep(0.1)

    return created, failed


def main():
    parser = argparse.ArgumentParser(description="Push Kamstrup data to OmniGaze via MCP")
    parser.add_argument("--input", default=r"F:\RootContext\Kamstrup\import-scripts\output", help="Input directory")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually create anything")
    args = parser.parse_args()

    print(f"Kamstrup Phase 2 — Push to OmniGaze")
    print(f"Input: {args.input}")
    print(f"Dry run: {args.dry_run}")
    print(f"MCP client: {MCP_CLIENT}")
    print("=" * 60)

    if not os.path.exists(MCP_CLIENT):
        print(f"ERROR: MCP client not found at {MCP_CLIENT}")
        print("NOTE: The MCP API must be running Phase 0+1 code for OrganizationFactSheet support.")
        sys.exit(1)

    # Import order matters: value streams first, then capabilities, etc.
    files = [
        ("01-value-streams.json", "Value Streams"),
        ("02-business-capabilities.json", "Business Capabilities"),
        ("03-organizations.json", "Organizations"),
        ("04-processes.json", "Processes"),
        ("05-platforms.json", "Platforms (ITComponent)"),
        ("06-providers.json", "Providers"),
    ]

    total_created = 0
    total_failed = 0

    for filename, label in files:
        filepath = os.path.join(args.input, filename)
        if not os.path.exists(filepath):
            print(f"\n⚠ Skipping {label} — file not found: {filepath}")
            continue

        print(f"\n{'─'*40}")
        print(f"Pushing {label}...")
        created, failed = push_file(filepath, args.dry_run)
        print(f"  {label}: {created} created, {failed} failed")
        total_created += created
        total_failed += failed

    # Now set hierarchy relationships
    print(f"\n{'─'*40}")
    print("Setting hierarchy relationships...")

    for filename, label in files:
        filepath = os.path.join(args.input, filename)
        if not os.path.exists(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            factsheets = json.load(f)

        for fs in factsheets:
            children = fs.get("HierarchyChildrenIds", [])
            if children:
                set_hierarchy(fs["Id"], children, args.dry_run)
                if not args.dry_run:
                    time.sleep(0.05)

    print(f"\n{'='*60}")
    print(f"PUSH COMPLETE")
    print(f"  Created: {total_created}")
    print(f"  Failed: {total_failed}")
    print(f"  Finished: {datetime.now().isoformat()}")

    if args.dry_run:
        print("\n  ℹ This was a dry run. No data was actually created.")
        print("  Run without --dry-run to push to OmniGaze.")


if __name__ == "__main__":
    main()

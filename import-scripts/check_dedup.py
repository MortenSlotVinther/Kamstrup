"""Check why L2=105 (vs expected 101) and L3=545 (vs expected 532)."""
import openpyxl
wb = openpyxl.load_workbook(
    r"F:\RootContext\Kamstrup\Kamstrup_Business-Capability-Map.xlsx",
    read_only=True, data_only=True
)
ws = wb["B-Business Capability"]

# Collect all L2 entries with their L0/L1 context
l2_entries = {}  # (l0, l1, l2) -> count
l2_by_name = {}  # l2_name -> set of (l0, l1) parents
l3_entries = {}  # (l0, l1, l2, l3) -> count

for row in ws.iter_rows(min_row=6, values_only=True):
    l0 = str(row[4] or "").strip() if len(row) > 4 else ""
    l1 = str(row[5] or "").strip() if len(row) > 5 else ""
    l2 = str(row[6] or "").strip() if len(row) > 6 else ""
    l3 = str(row[7] or "").strip() if len(row) > 7 else ""

    if l2:
        key = (l0, l1, l2)
        l2_entries[key] = l2_entries.get(key, 0) + 1
        if l2 not in l2_by_name:
            l2_by_name[l2] = set()
        l2_by_name[l2].add((l0, l1))

    if l3:
        key = (l0, l1, l2, l3)
        l3_entries[key] = l3_entries.get(key, 0) + 1

wb.close()

# L2: unique by (l0, l1, l2) = 105, but unique by just l2 name alone?
unique_l2_names = set()
for (l0, l1, l2) in l2_entries:
    unique_l2_names.add(l2)

print(f"Unique L2 by (L0,L1,L2): {len(l2_entries)}")
print(f"Unique L2 by name only: {len(unique_l2_names)}")

# Show L2 names that appear under multiple L1 parents
dups = {name: parents for name, parents in l2_by_name.items() if len(parents) > 1}
print(f"\nL2 names under multiple L1 parents: {len(dups)}")
for name, parents in sorted(dups.items()):
    print(f"  '{name}' appears under: {parents}")

# L3 analysis
unique_l3_names = set()
for (l0, l1, l2, l3) in l3_entries:
    unique_l3_names.add(l3)

print(f"\nUnique L3 by (L0,L1,L2,L3): {len(l3_entries)}")
print(f"Unique L3 by name only: {len(unique_l3_names)}")

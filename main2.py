import csv
from collections import defaultdict
import sys

def validate_org_hierarchy(csv_path):
    parent_map = defaultdict(set)
    errors = []

    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)

        for row_num, row in enumerate(reader, start=2):
            orgs = row[2:]  # Skip cloneUrl and branch
            for child, parent in zip(orgs, orgs[1:]):
                parent_map[child].add(parent)

                if len(parent_map[child]) > 1:
                    errors.append(
                        f"Conflict at row {row_num}: Org '{child}' has multiple parents: {parent_map[child]}"
                    )

    if errors:
        print("Validation failed:\n")
        for err in errors:
            print(err)
    else:
        print("Validation passed. No org has multiple parents.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_orgs.py <path_to_csv>")
    else:
        validate_org_hierarchy(sys.argv[1])
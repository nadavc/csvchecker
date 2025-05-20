import csv
import sys


def validate_org_hierarchy_revised(csv_file_path):
    """
    Validates that no single org is being parented by more than one parent.

    Args:
        csv_file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary where keys are orgs with multiple parents
              and values are sets of their conflicting parents.
              Returns an empty dictionary if no violations are found.
    """
    # This map will store child -> parent relationships
    # e.g., if orgB is child of orgA, it's stored as {'orgB': 'orgA'}
    child_to_parent_map = {}
    violations = {}  # Stores orgs (children) with multiple parents

    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Skip header row

        # Identify which columns are org columns based on their names
        org_cols_indices = [i for i, col_name in enumerate(header) if col_name.startswith('org')]

        if not org_cols_indices or len(org_cols_indices) < 2:
            print("Not enough 'org' columns (at least 2 required) found in the CSV header to define a hierarchy.")
            return {}

        for row_num, row in enumerate(reader, start=2):  # Start from row 2 (after header)
            current_row_org_values = []
            for i in org_cols_indices:
                if i < len(row) and row[i]: # Check if index is valid and value is not empty
                    current_row_org_values.append(row[i])
                else:
                    # Handle rows with fewer org columns than defined in header, or empty orgs
                    # This assumes the hierarchy chain breaks if an org is missing.
                    # If an org value is missing in the middle, subsequent orgs in that row
                    # won't form a parent-child pair with the missing one.
                    current_row_org_values.append(None) # Use None as a placeholder

            if len(current_row_org_values) < 2:
                continue

            # Iterate through the hierarchy in the current row
            # Assuming org_values[i] is parent of org_values[i+1]
            for i in range(len(current_row_org_values) - 1):
                child_org = current_row_org_values[i]
                parent_org = current_row_org_values[i+1]

                # Only process if both parent and child orgs are present
                if parent_org and child_org:
                    if child_org not in child_to_parent_map:
                        child_to_parent_map[child_org] = parent_org
                    elif child_to_parent_map[child_org] != parent_org:
                        # Violation found! This child_org has a different parent than previously recorded.
                        print(f"Violation on row {row_num}: Org '{child_org}' previously parented by '{child_to_parent_map[child_org]}', now by '{parent_org}'.")
                        if child_org not in violations:
                            violations[child_org] = {child_to_parent_map[child_org]}
                        violations[child_org].add(parent_org)

    if not violations:
        print("No hierarchical violations found. Each org (child) has a single, consistent parent.")
    else:
        print("\nViolations: ")
        for org, conflicting_parents in violations.items():
            print(f"- Org '{org}' is reported as a child of multiple parents: {', '.join(sorted(list(conflicting_parents)))}")

    return violations

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("usage: uv run main.py <repos_csv_file_path>")
        exit(1)

    file_path = sys.argv[1]
    found_violations = validate_org_hierarchy_revised(file_path)

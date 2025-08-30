# utils.py

import json
from pandera.errors import SchemaErrors

def parse_pandera_errors(exc: SchemaErrors) -> list:
    """
    Converts errors from a Pandera SchemaErrors exception into a clear, reliable,
    and de-duplicated format. It prioritizes errors to find the root cause for each
    column, preventing error cascades (e.g., a 'wrong_type' error also causing
    'out_of_range' errors).
    """
    range_checks = {
        "greater_than", "less_than", "greater_than_or_equal_to", 
        "less_than_or_equal_to", "in_range", "between"
    }
    
    # Define error priority (lower number is higher priority)
    error_priority = {
        "missing_field": 1,
        "extra_field": 1,
        "wrong_type": 2,
        "null_value": 3,
        "bad_format": 4,
        "mismatched_id": 4,
        "out_of_range": 5,
        "check_failed": 6, # Generic catch-all for other checks
        "unknown": 99
    }

    # This dictionary will hold the single highest-priority error for each column
    highest_priority_errors = {}

    for _, row in exc.failure_cases.iterrows():
        column = row.get("column")
        check = str(row.get("check", ""))
        failed_value = row.get("failure_case")
        
        reason = f"Validation failed for field '{column}' with value '{failed_value}'. Rule: {check}"
        output_failed_value = failed_value
        error_type = "unknown"

        # --- Classification Logic (same as before, but now used for prioritization) ---
        if check == "column_in_schema":
            column = failed_value
            reason = f"An extra field named '{column}' was found, which is not defined in the schema."
            output_failed_value = "N/A (Extra Field)"
            error_type = "extra_field"
        elif check == "column_in_dataframe":
            column = failed_value
            reason = f"The required field '{column}' was not found in the data."
            output_failed_value = "N/A (Missing Field)"
            error_type = "missing_field"
        elif check.startswith("not_nullable"):
            reason = f"The required field '{column}' cannot be null."
            error_type = "null_value"
        elif check.startswith("dtype"):
            expected_type = check.split("'")[1] if "'" in check else check
            actual_type = type(failed_value).__name__ if failed_value is not None else "None"
            reason = f"The data type of field '{column}' is incorrect. Expected: '{expected_type}', Got: '{actual_type}' with value '{failed_value}'."
            error_type = "wrong_type"
        elif any(range_check in check for range_check in range_checks):
            reason = f"The value '{failed_value}' in field '{column}' is outside the expected range. Rule: {check}"
            error_type = "out_of_range"
        elif check.startswith("equal_to"):
            reason = f"The value '{failed_value}' in field '{column}' is different from the expected value. Rule: {check}"
            error_type = "mismatched_id"
        elif check.startswith("str_matches"):
            reason = f"The value '{failed_value}' in field '{column}' does not match the expected format. Rule: {check}"
            error_type = "bad_format"
        else:
            # New generic fallback for any other pandera check (like isin, notin)
            # We extract the check name (e.g., 'isin') from the full check string (e.g., 'isin(["on", "off"])')
            check_name = check.split('(')[0]
            reason = f"The value '{failed_value}' in field '{column}' failed the '{check_name}' check. Rule: {check}"
            # Create a specific error type, e.g., 'check_failed:isin'
            error_type = f"check_failed:{check_name}"


        # --- Prioritization Logic ---
        current_error = {
            "column": column, "check": check, "reason": reason,
            "failed_value": output_failed_value, "error_type": error_type
        }
        
        # If we haven't seen an error for this column yet, or if this new error
        # has a higher priority, store it.
        if column not in highest_priority_errors or \
           error_priority.get(error_type, 99) < error_priority.get(highest_priority_errors[column]["error_type"], 99):
            highest_priority_errors[column] = current_error

    # Return only the highest-priority error for each column
    return list(highest_priority_errors.values())

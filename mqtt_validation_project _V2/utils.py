# utils.py

import json
from pandera.errors import SchemaErrors

def parse_pandera_errors(exc: SchemaErrors) -> list:
    """
    Converts errors from a Pandera SchemaErrors exception into a clear and reliable format
    by using the `failure_cases` DataFrame. This method is much more robust than parsing
    error strings.
    """
    parsed_errors = []
    
    # exc.failure_cases is a DataFrame containing structured information about the errors.
    for _, row in exc.failure_cases.iterrows():
        column = row.get("column")
        check = row.get("check")
        failed_value = row.get("failure_case")
        
        # Default values for error messages
        reason = f"The value '{failed_value}' in field '{column}' violated the rule: {check}"
        output_failed_value = failed_value
        error_type = "unknown" # Default error type

        # Create a specific and clear description for each error type
        if check == "column_in_schema":
            # Extra field error: The column name is in 'failure_case'.
            column = failed_value
            reason = f"An extra field named '{column}' was found, which is not defined in the schema."
            output_failed_value = "N/A (Extra Field)"
            error_type = "extra_field"
        
        elif check == "column_in_dataframe":
            # Missing field error: The column name is in 'failure_case'.
            column = failed_value
            reason = f"The required field '{column}' was not found in the data (missing)."
            output_failed_value = "N/A (Missing Field)"
            error_type = "missing_field"

        elif check and check.startswith("not_nullable"):
            reason = f"The required field '{column}' cannot be null."
            error_type = "null_value"
        
        elif check and check.startswith("dtype"):
            expected_type = check.split("'")[1] if "'" in check else check
            actual_type = type(failed_value).__name__ if failed_value is not None else "None"
            reason = f"The data type of field '{column}' is incorrect. Expected: '{expected_type}', Got: '{actual_type}'."
            error_type = "wrong_type"
        
        elif check and (check.startswith("between") or check.startswith("greater_than_or_equal_to")):
            reason = f"The value '{failed_value}' in field '{column}' is outside the expected range. Rule: {check}"
            error_type = "out_of_range"
        
        elif check and check.startswith("equal_to"):
            reason = f"The value '{failed_value}' in field '{column}' is different from the expected value. Rule: {check}"
            error_type = "mismatched_id"
        
        elif check and check.startswith("str_matches"):
            reason = f"The value '{failed_value}' in field '{column}' does not match the expected format. Rule: {check}"
            error_type = "bad_format"

        parsed_errors.append({
            "column": column,
            "check": check,
            "reason": reason,
            "failed_value": output_failed_value,
            "error_type": error_type
        })

    return parsed_errors

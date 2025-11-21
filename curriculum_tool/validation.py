from jsonschema import Draft7Validator


def validate_curriculum(data: dict, schema: dict) -> None:
    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda error: error.path)
    if errors:
        messages = [f"Error at {list(err.path)}: {err.message}" for err in errors]
        raise ValueError("Schema validation failed:\n" + "\n".join(messages))

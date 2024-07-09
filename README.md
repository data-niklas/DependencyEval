# Dataset format

JSONL file where each line contains the following JSON schema:

```json
{
	"task_id": "PackageEval_{int}",
	"task_name": "{string}_{int}",
	"test_code": "{string}",
	"import_statements": ["{string}"],
	"package_dependencies": ["{string}"],
	"context": "{string}",
	"function_signature": "{string}",
	"function_documentation": "{string}",
	"entry_point": "{string}",
	"solution": "{string}",
	"reason": "{string}",
	"kind": "{kind}",
	"date": "%Y-%m-%d",
	"code_kind": "{code_kind}",
	"modification_kind": "{modification_kind}",
	"changelog": "{url}",
	"python_version": "{string}"
}
```

## Kind

May be one of the following values:

- `modification`: The code snippet is rarely used as it was changed recently
- `uncommon`: The code snippet is assumed to be rarely used in general

## Code kind

May be one of the following values:

- `field`
- `parameter`
- `function`
- `method`
- `block`

## Modification kind

May be one of the following values:

- `addition`: Only addition of code
- `removal`: Only removal of code
- `deprecation`: Update of the code where the old snippet is available, but marked as deprecated
- `rename`

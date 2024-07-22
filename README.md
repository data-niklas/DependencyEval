# Dataset format

JSONL file where each line contains the JSON schema found in [schema](./data/schema.json)

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

## Security
- Uses Docker to reduce the risk of running untrusted code
- Limits the time the evaluated code may run
- For a more secure solution install gVisor
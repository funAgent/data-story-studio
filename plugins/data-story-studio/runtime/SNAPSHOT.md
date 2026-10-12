# Dashboard snapshot contract, version 1

`build --source INPUT.csv --spec SPEC.json --output NEW_DIRECTORY` produces a self-contained `index.html`, `snapshot.json`, `spec.json`, and `manifest.json`. The output directory's parent must exist. Open the HTML directly in a browser; no server or network is needed. `inspect --source INPUT` prints schema, provenance and five sample rows. `refresh --project DIRECTORY` explicitly rereads the original source and reads the editable `spec.json`. Edit that file to change chart configuration, then refresh. Do not edit the HTML or snapshot; refresh refuses changed artifacts. Unrelated files are preserved. Build refuses any existing directory. Symlink paths and outputs inside the runtime/plugin are rejected.

## Snapshot shape

- `schema_version`: integer `1`
- `title`: string
- `rows`: array of original row objects. Cells are strings, finite numbers, booleans or null. All rows have identical field keys. JSON integer identifiers outside ±9007199254740991 must be strings.
- `dimensions`: nonempty array of distinct field names
- `metrics`: array of `{ "field": "revenue", "aggregation": "sum", "id": "sum:revenue" }`. Stable IDs concatenate aggregation, colon, original field name. Aggregations are sum, mean, count. Count counts non-null values, including false and zero. Sum/mean require numeric-or-null cells and skip nulls; all-null aggregate groups return null. Count over an empty group is zero.
- `charts`: array of `{ "type": "bar", "dimension": "region", "metric": "sum:revenue" }`. Types: bar, line, table. Metric references use stable IDs. Chart categories follow source first-seen order; line charts do not infer date parsing or chronology. Display capped at 100 categories, filtering and metric summaries cover all rows.
- `provenance`: `{ "source_path": "/absolute/path/data.csv", "sha256": "64 lowercase hex characters", "captured_at": "UTC ISO timestamp", "row_count": 3 }`. SHA-256 hashes original source bytes, before parsing.

Spec uses title, dimensions, metrics (without id), and optional charts. Unknown spec keys are rejected. If charts are omitted, a bar chart of the first dimension and metric is used. The filter UI supports case-insensitive substring matches against any source field. Changing dimension or metric applies the selection to all chart panels; Reset restores each panel's configured definition.

## Parsing and privacy

Input is UTF-8 CSV with header or a JSON array of row objects, maximum 20 MiB / 100,000 rows / 200 columns. CSV whitespace is trimmed, empty cells become null, finite numbers are inferred, and leading-zero identifiers remain strings. JSON types are retained. Nested objects, arrays, duplicate column/key names, non-finite numbers, heterogeneous schemas and unsafe integers are rejected. No formulas, SQL, expressions or code run from source or spec. No network calls occur. Labels are embedded as HTML-safe JSON and displayed using textContent.

Snapshots and HTML contain the complete source rows and original local path. They are private local artifacts unless the user explicitly chooses to share them. A refresh overwrites the four project files after hash checks; it is not a source-file watcher and does not fetch network resources. Keep a copy if you need historical snapshots. Concurrent edits or refreshes of the same project are not supported.

Integer-valued numbers outside ±9007199254740991 are rejected, including decimal and exponent notation. CSV quoting does not declare a string type; represent large identifiers as JSON strings instead. Leading-zero CSV identifiers remain strings.

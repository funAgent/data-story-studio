# Local dashboard CLI

Requires Python 3.10+ standard library. No dependencies or network connection.

```sh
python /your/workspace/.data-story-runtime/dashboard.py inspect --source /your/workspace/data.csv
python /your/workspace/.data-story-runtime/dashboard.py build --source /your/workspace/data.csv --spec /your/workspace/examples/dashboard-spec.json --output /your/workspace/dashboard
python /your/workspace/.data-story-runtime/dashboard.py refresh --project /your/workspace/dashboard
```

Choose a NEW output directory outside the installed plugin or copied runtime. Its parent must exist. Open `dashboard/index.html` directly. Source files are never modified. `build` refuses an existing directory, including empty directories. `refresh` checks ownership and generated-file hashes, rereads the original local source and loads the editable project `spec.json`. Edit `spec.json`, then explicitly refresh to persist new chart definitions. Do not edit index.html or snapshot.json; refresh refuses to overwrite user changes to these files. Other project files are preserved. Manifest retains the last successful spec, original absolute source path, and artifact hashes.

Spec example:

```json
{
  "title": "Revenue overview",
  "dimensions": ["month", "region"],
  "metrics": [{"field": "revenue", "aggregation": "sum"}],
  "charts": [
    {"type": "bar", "dimension": "region", "metric": "sum:revenue"},
    {"type": "line", "dimension": "month", "metric": "sum:revenue"},
    {"type": "table", "dimension": "region", "metric": "sum:revenue"}
  ]
}
```

Metrics support sum, mean, count. IDs referenced by charts are `aggregation:field`. Count means non-null values. Sum/mean skip nulls and require numeric cells. Charts are bar, line, table; omit charts to create a default bar chart. Dimensions must be actual source fields. Unknown keys or expressions are rejected.

The HTML has dimension/metric selectors, a field selector and a case-insensitive text filter. Changing dimension/metric updates all panels for exploratory use; Reset restores the configured chart definitions. Browser exploration does not write to disk. Metric cards use all filtered rows, charts show at most 100 categories in first-seen order. Line charts do not automatically sort dates. Arrange source rows chronologically for time series.

Inputs: UTF-8 CSV with unique headers, or a JSON array of row objects with identical columns. Limits: 20 MiB, 100,000 rows, 200 fields, 100 metrics, 12 charts. No nested cells or non-finite numbers. Empty CSV cells become null, numeric-looking values are inferred, leading-zero identifiers remain text. Large integer IDs should be JSON strings. Repeated JSON keys and unsafe integers are rejected. Symlink paths are rejected. Concurrent writers to the same output directory are unsupported.

The output embeds every row and absolute source path, so treat it as private data. No data upload, network resource, remote analytics, SQL, code evaluation or automatic refresh occurs. Sharing or publishing requires a separate explicit user decision.

See `SNAPSHOT.md` for the versioned motion interoperability format and exact parsing semantics. Errors print a concise diagnostic to stderr and return exit status 2.

Integer-valued numbers outside ±9007199254740991 are rejected, including decimal and exponent notation. CSV quoting does not declare a string type; represent large identifiers as JSON strings instead. Leading-zero CSV identifiers remain strings.

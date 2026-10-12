#!/usr/bin/env python3
"""Offline, stdlib-only CSV/JSON dashboard builder. See SNAPSHOT.md for the contract."""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
from pathlib import Path
import sys
import tempfile

SCHEMA_VERSION = 1
MAX_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100000
RUNTIME_ROOT = Path(__file__).resolve().parent
PLUGIN_ROOT = RUNTIME_ROOT if RUNTIME_ROOT.name == '.data-story-runtime' else RUNTIME_ROOT.parent
FILES = ('index.html', 'snapshot.json', 'spec.json', 'manifest.json')

class DashboardError(ValueError):
    pass

def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def no_symlinks(path):
    if '..' in Path(str(path)).parts:
        raise DashboardError('Parent-directory traversal is not allowed')
    path = Path(os.path.abspath(os.path.expanduser(str(path))))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise DashboardError('Symlink paths are not allowed: ' + str(part))
    return path

def load_json(data):
    def bad_constant(value):
        raise DashboardError('Non-finite JSON number: ' + value)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise DashboardError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(data, parse_constant=bad_constant, object_pairs_hook=pairs)

def read_small(path):
    path = no_symlinks(path)
    if not path.is_file():
        raise DashboardError('Expected a regular file: ' + str(path))
    if path.stat().st_size > MAX_BYTES:
        raise DashboardError('Input exceeds 20 MiB limit')
    with path.open('rb') as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise DashboardError('Input exceeds 20 MiB limit')
    return path, data

def scalar(value):
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise DashboardError('Every cell must be a finite JSON scalar (no arrays or objects)')

def csv_scalar(value):
    if value is None:
        raise DashboardError('CSV row has missing columns')
    value = value.strip()
    if not value:
        return None
    try:
        number = float(value)
    except ValueError:
        return value
    if not math.isfinite(number):
        raise DashboardError('CSV contains a non-finite number')
    # Preserve numeric-looking identifiers with leading zeros.
    if len(value) > 1 and value[0] == '0' and value[1].isdigit():
        return value
    if re.fullmatch(r'[+-]?\d+', value):
        integer = int(value)
        if abs(integer) > 9007199254740991:
            raise DashboardError('CSV integer outside JavaScript safe range; use JSON string identifiers')
        return integer
    if number.is_integer() and abs(number) > 9007199254740991:
        raise DashboardError('CSV integer-valued number outside JavaScript safe range; use JSON string identifiers')
    return int(number) if number.is_integer() else number

def source_data(source):
    path, raw = read_small(source)
    text = raw.decode('utf-8-sig')
    if path.suffix.lower() == '.csv':
        reader = csv.DictReader(io.StringIO(text))
        fields = reader.fieldnames
        if not fields or len(set(fields)) != len(fields):
            raise DashboardError('CSV requires unique column names')
        rows = []
        for row in reader:
            if None in row:
                raise DashboardError('CSV row has extra columns')
            rows.append({key: csv_scalar(value) for key, value in row.items()})
            if len(rows) > MAX_ROWS:
                raise DashboardError('Source exceeds 100000 rows')
    elif path.suffix.lower() == '.json':
        rows = load_json(text)
        if not isinstance(rows, list):
            raise DashboardError('JSON source must be an array of row objects')
        fields = list(rows[0]) if rows and isinstance(rows[0], dict) else []
    else:
        raise DashboardError('Source must have .csv or .json extension')
    if not rows or len(rows) > MAX_ROWS or not fields:
        raise DashboardError('Source must contain 1–100000 rows and at least one column')
    if len(fields) > 200 or any(not isinstance(f, str) or not f.strip() or len(f) > 200 for f in fields):
        raise DashboardError('Use 1–200 nonempty column names, each at most 200 characters')
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(fields):
            raise DashboardError('All rows must have the same columns')
        for value in row.values():
            scalar(value)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and abs(value) > 9007199254740991 and (isinstance(value, int) or value.is_integer()):
                raise DashboardError('Integer outside JavaScript safe range; encode identifiers as strings')
    return rows, fields, {'source_path': str(path), 'sha256': digest(raw), 'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'row_count': len(rows)}

def validate_spec(spec, rows, fields):
    if not isinstance(spec, dict) or set(spec) - {'title', 'dimensions', 'metrics', 'charts'}:
        raise DashboardError('Spec accepts only title, dimensions, metrics, charts')
    title = spec.get('title', 'Data story')
    dimensions, metrics = spec.get('dimensions'), spec.get('metrics')
    if not isinstance(title, str) or not title.strip() or len(title) > 300:
        raise DashboardError('Title must be a nonempty string, at most 300 characters')
    if not isinstance(dimensions, list) or not dimensions or any(not isinstance(x, str) or x not in fields for x in dimensions) or len(set(dimensions)) != len(dimensions):
        raise DashboardError('dimensions must be a nonempty list of unique source fields')
    if not isinstance(metrics, list) or not metrics or len(metrics) > 100:
        raise DashboardError('metrics must be a nonempty list, maximum 100')
    normalized = []
    for metric in metrics:
        if not isinstance(metric, dict) or set(metric) != {'field', 'aggregation'}:
            raise DashboardError('Each metric needs exactly field and aggregation')
        field, agg = metric['field'], metric['aggregation']
        if not isinstance(field, str) or field not in fields or agg not in ('sum', 'mean', 'count'):
            raise DashboardError('Metric requires a source field and sum, mean, or count aggregation')
        if agg != 'count':
            values = [row[field] for row in rows if row[field] is not None]
            if not values or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in values):
                raise DashboardError('sum/mean metrics require numeric or null cells: ' + field)
            try:
                finite_total = math.isfinite(math.fsum(abs(value) for value in values))
            except OverflowError:
                finite_total = False
            if not finite_total:
                raise DashboardError('Metric magnitudes can overflow aggregation: ' + field)
        normalized.append(dict(metric, id=agg + ':' + field))
    ids = [m['id'] for m in normalized]
    if len(set(ids)) != len(ids):
        raise DashboardError('Duplicate metrics are not allowed')
    charts = spec.get('charts', [{'type': 'bar', 'dimension': dimensions[0], 'metric': ids[0]}])
    if not isinstance(charts, list) or not charts or len(charts) > 12:
        raise DashboardError('charts requires 1–12 charts')
    for chart in charts:
        if not isinstance(chart, dict) or set(chart) != {'type', 'dimension', 'metric'}:
            raise DashboardError('Each chart needs exactly type, dimension, metric')
        if chart['type'] not in ('bar', 'line', 'table') or chart['dimension'] not in dimensions or chart['metric'] not in ids:
            raise DashboardError('Unknown chart type, dimension, or metric ID')
    return {'title': title, 'dimensions': dimensions, 'metrics': normalized, 'charts': charts}

def render(snapshot):
    template = (Path(__file__).with_name('dashboard.html')).read_text(encoding='utf-8')
    # A JSON script element is still an HTML parsing context. Escape all delimiters.
    embedded = dumps(snapshot).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return template.replace('__SNAPSHOT_JSON__', embedded)

def safe_target(output, exists=False):
    path = no_symlinks(output)
    if path == PLUGIN_ROOT or PLUGIN_ROOT in path.parents:
        raise DashboardError('Output must be outside the installed plugin')
    if path == Path(path.anchor) or path == Path.home():
        raise DashboardError('Refusing unsafe output directory')
    if exists:
        if not path.is_dir():
            raise DashboardError('Project must be an existing directory')
    elif path.exists():
        raise DashboardError('Output already exists; choose a new directory or use refresh')
    if not path.parent.is_dir():
        raise DashboardError('Output parent directory must already exist')
    return path

def generate(source, spec):
    rows, fields, provenance = source_data(source)
    validated = validate_spec(spec, rows, fields)
    snapshot = dict(schema_version=SCHEMA_VERSION, rows=rows, provenance=provenance, **validated)
    payloads = {'snapshot.json': dumps(snapshot).encode('utf-8'), 'index.html': render(snapshot).encode('utf-8')}
    manifest = {'generator': 'data-story-studio', 'schema_version': SCHEMA_VERSION, 'source_path': provenance['source_path'], 'spec': spec, 'files': {name: digest(data) for name, data in payloads.items()}}
    payloads['manifest.json'] = dumps(manifest).encode('utf-8')
    payloads['spec.json'] = dumps(spec).encode('utf-8')
    return payloads

def write_new(output, payloads):
    # mkdir is exclusive: a concurrent writer cannot silently claim the target.
    output.mkdir(mode=0o700)
    try:
        for name, data in payloads.items():
            with (output / name).open('xb') as handle:
                handle.write(data)
    except Exception:
        # Do not remove a directory recursively: unrelated concurrent files survive.
        for name in payloads:
            file = output / name
            if file.is_file() and not file.is_symlink():
                file.unlink()
        try:
            output.rmdir()
        except OSError:
            pass
        raise

def build(source, spec_file, output):
    output = safe_target(output)
    _, raw = read_small(spec_file)
    payloads = generate(source, load_json(raw.decode('utf-8-sig')))
    write_new(output, payloads)
    return output

def refresh(project):
    project = safe_target(project, exists=True)
    _, raw = read_small(project / 'manifest.json')
    manifest = load_json(raw.decode('utf-8'))
    if not isinstance(manifest, dict) or manifest.get('generator') != 'data-story-studio' or manifest.get('schema_version') != SCHEMA_VERSION or not isinstance(manifest.get('files'), dict) or set(manifest['files']) != {'index.html', 'snapshot.json'}:
        raise DashboardError('Not a supported generated dashboard project')
    for name, expected in manifest['files'].items():
        _, data = read_small(project / name)
        if digest(data) != expected:
            raise DashboardError('Generated file was edited; refusing to overwrite: ' + name)
    # Unknown files are preserved. Source changes are read only for explicit refresh.
    _, spec_raw = read_small(project / 'spec.json')
    payloads = generate(manifest['source_path'], load_json(spec_raw.decode('utf-8-sig')))
    with tempfile.TemporaryDirectory(prefix='.dashboard-refresh-', dir=project.parent) as temporary:
        temporary = Path(temporary)
        for name, data in payloads.items():
            (temporary / name).write_bytes(data)
        for name in FILES:
            no_symlinks(project / name)
            os.replace(temporary / name, project / name)
    return project

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect', help='Read local CSV/JSON and describe its schema')
    inspect.add_argument('--source', required=True)
    create = commands.add_parser('build', help='Build into a NEW directory outside the plugin')
    create.add_argument('--source', required=True)
    create.add_argument('--spec', required=True)
    create.add_argument('--output', required=True)
    renew = commands.add_parser('refresh', help='Explicitly reread the recorded original source')
    renew.add_argument('--project', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect':
            rows, fields, provenance = source_data(args.source)
            result = {'provenance': provenance, 'fields': [{'name': field, 'numeric': all(value is None or (isinstance(value, (int, float)) and not isinstance(value, bool)) for value in (row[field] for row in rows)), 'null_count': sum(row[field] is None for row in rows)} for field in fields], 'sample': rows[:5]}
        else:
            output = build(args.source, args.spec, args.output) if args.command == 'build' else refresh(args.project)
            result = {'project': str(output), 'dashboard': str(output / 'index.html'), 'snapshot': str(output / 'snapshot.json')}
        print(dumps(result))
        return 0
    except (DashboardError, OSError, ValueError, TypeError, KeyError, OverflowError) as error:
        print('dashboard: ' + str(error), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())

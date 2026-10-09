"""Recompute the supplied BudgetGraph audit offline; no repository code is downloaded or run."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import platform
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'results')
    args = parser.parse_args()
    notebook_path = Path(__file__).parent / 'budgetgraph-reproducible-retrieval-audit.ipynb'
    notebook = json.loads(notebook_path.read_text())
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    previous = Path.cwd()
    os.chdir(output)
    started = time.perf_counter()
    namespace = {'__name__': 'budgetgraph_offline_reproduction'}
    try:
        # Published implementation, checksum-checked inputs, rankings, aggregation,
        # expected results, six correctness tests, and post hoc diagnostics.
        for cell_id in [2, 4, 6, 7, 10, 14, 16]:
            cell = notebook['cells'][cell_id]
            if cell['cell_type'] != 'code':
                raise ValueError(f'Expected code cell {cell_id}')
            exec(compile(''.join(cell['source']), f'{notebook_path.name}:cell{cell_id}', 'exec'), namespace)
        report = namespace['report']
        (output / 'summary.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        with (output / 'per_task.jsonl').open('w') as stream:
            for task in namespace['tasks']:
                record = {key: task[key] for key in ['instance_id', 'repo', 'base_commit', 'gold', 'missing_gold', 'metrics']}
                stream.write(json.dumps(record, sort_keys=True) + '\n')
        columns = ['condition', 'method', 'macro_hit5', 'macro_delta_hit5', 'ci_lower', 'ci_upper']
        with (output / 'comparison.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            for row in report['results']:
                writer.writerow({**{k: row[k] for k in columns[:4]},
                                 'ci_lower': row['delta_ci95'][0], 'ci_upper': row['delta_ci95'][1]})
        metadata = {'python': sys.version, 'platform': platform.platform(),
                    'numpy': namespace['np'].__version__,
                    'notebook_sha256': hashlib.sha256(notebook_path.read_bytes()).hexdigest(),
                    'payload_sha256': hashlib.sha256(namespace['raw']).hexdigest(),
                    'elapsed_seconds': time.perf_counter() - started,
                    'verification_scope': 'Frozen-input reproduction; no independent source reconstruction or model repair run.',
                    'aggregate_checks': 20, 'correctness_tests': namespace['result'].testsRun}
        (output / 'reproduction_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print('Saved recomputed audit:', output)
    finally:
        os.chdir(previous)


if __name__ == '__main__':
    main()

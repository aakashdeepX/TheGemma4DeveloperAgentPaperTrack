# GraphProbe-SWE v0.2

A measured BudgetGraph retrieval audit and a proposed framework for budget-aware graph trust.

On 143 public SWE-bench Lite issues from 12 repositories, clean import-graph fusion achieves **60.25% macro Hit@5 versus BM25's 67.61%**. The paired difference is −7.37 percentage points, with a within-repository task-bootstrap 95% interval [−12.25, −3.13]. At five files, fusion loses 12 lexical hits and recovers none.

Counterfactual graph trust is proposed and unvalidated. The legacy graphprobe.py implements an earlier synthetic heuristic; it is not a calibrated gate or a trained Gemma agent.

## Files

- [Updated Kaggle paper draft](KAGGLE_WRITEUP_V01.md) — content version 0.2, filename retained.
- [Evaluation plan](EVALUATION_PLAN.md) — untouched confirmation, exact token budgets, and separate Gemma repair study.
- [Audit summary](budgetgraph/results/summary.json) — verified primary results and corpus coverage.
- [Paired task outcomes](budgetgraph/results/per_task.jsonl.gz) — all condition/seed/method metrics and top-20 rankings, compressed with gzip.
- [Offline runner](budgetgraph/reproduce.py) — executes the original notebook's computational cells and tests.
- [Change log](CHANGELOG.md).

## Reproduce the audit

The original supplied notebook is required: budgetgraph-reproducible-retrieval-audit.ipynb. Place it in the budgetgraph directory alongside reproduce.py. **The notebook itself has not yet been mirrored in this repository:** an execution-environment outage interrupted its upload. The paired outcomes were recovered and published successfully. This missing input is a reproducibility packaging limitation, not an omitted benchmark failure.

Tested computational reproduction used Python 3.12 and NumPy 2.3.5. No GPU, model, credentials, network access, or execution of upstream repository code is needed after installing NumPy and providing the notebook.

~~~bash
python -m pip install -r budgetgraph/requirements-offline.txt
python budgetgraph/reproduce.py --output /tmp/budgetgraph-reproduction
~~~

The runner recomputes all rankings, metrics, intervals, and post hoc diagnostics; verifies 20 expected aggregate comparisons and six correctness tests; and writes summary JSON, task JSONL, comparison CSV, and environment metadata. These checks passed before the environment outage. It excludes source-download and plotting cells. The full notebook additionally uses pandas and matplotlib for visualization.

Frozen-input reproduction does not independently rebuild source indexes or evaluate patch correctness. Optional source-reconstruction instructions are in the original notebook.

## Original GraphProbe smoke tests

~~~bash
python graphprobe.py
python -m unittest discover -s tests -v
~~~

All six legacy prototype tests also passed during this update. The starter notebook remains a synthetic demonstration. Its organizer-data reader uses approximate module-to-file labels; do not describe these as exact symbol localization or combine its scores with BudgetGraph.

## Scope and licensing

The graph-trust intervention has not been implemented or validated. File budgets are not token budgets. Degree-promotion diagnostics are post hoc and do not establish causality. The 143 tasks informed the proposed method; new confirmation data is required.

The existing root Apache-2.0 license is retained. This corrects the previous README's unsupported MIT description. SWE-bench and upstream material retain their original attribution and terms. BudgetGraph is a derived fixture, not a new issue collection.

The revised Markdown writeup and GitHub publication do not constitute a saved or submitted Kaggle entry.

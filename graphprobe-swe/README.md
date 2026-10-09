# GraphProbe-SWE v0.1

**Status: exploratory research prototype, not a trained Gemma 4 agent.**

This package contains a first Kaggle writeup draft and a deterministic Python code-graph retrieval benchmarking scaffold. It DOES NOT demonstrate state-of-the-art performance or a deployed patching agent.

## Files

- `KAGGLE_WRITEUP_V01.md`: paste into Kaggle New Writeup (edit name and results before submission).
- `graphprobe.py`: lexical baseline, fixed graph scoring, edge-perturbation stability diagnostic, and cost-sensitive retrieval.
- `GraphProbe_SWE_Kaggle_Starter.ipynb`: self-contained Kaggle-compatible notebook; uses a toy fixture when no competition dataset is attached.
- `fixture_output.json`: reproducible output of one hand-authored fixture, **not research results**.
- `EVALUATION_PLAN.md`: detailed research workplan, data-handling cautions, publication requirements.

## Local smoke test

```bash
python graphprobe.py
python -m unittest discover -s tests -v
```

## Kaggle benchmark

Attach the **Google Gemma 4 Developer Agent Competition** input data to the starter notebook, or use the script with the root folder containing `tasks.jsonl` and `graphs/`:

```python
from graphprobe import evaluate_folder, summarize
rows = evaluate_folder('/kaggle/input/YOUR_COMPETITION_INPUT', max_tasks=129)
print(summarize(rows))
```

Do not call the above result symbol-level localization: the path matcher is approximate. The code uses the organizer's reference patches strictly for retrospective evaluation; patch text is not supplied to retrieval. No dataset is bundled with this zip.

## Attribution and sharing

Review the competition rules before publishing competition-derived material. Prefer a publicly visible Kaggle Notebook for competition-related code. The source code created in this package is made available under the MIT license; third-party datasets and models retain their own terms. 
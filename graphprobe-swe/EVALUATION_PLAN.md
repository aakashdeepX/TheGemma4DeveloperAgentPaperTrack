# Research execution plan (GraphProbe-SWE)

## Checkpoints

1. **First demo (complete):** deterministic Python source + toy fixture + smoke test. No model and no public-data results.
2. **Public development benchmark:** mount organizers' data on Kaggle; test all 129 tasks; record missing graphs and unresolvable issues; save per-task JSONL.
3. **Gold-label integrity:** extract AST spans from source snapshot and overlap exact reference patch hunks. Create a module-to-file map independently of the patch to avoid optimistic prefix matches.
4. **Fair baseline comparison:** exact tokenizer match, equal inspected tokens, add native embedding search and BM25, same candidate universe, reproducible seed and edge perturbation.
5. **Ablations:** lexical only; fixed graph; graph with trust gate; adaptive with/without redundancy/cost; edge-drop 10/25/50%; graph injection and missing symbols.
6. **Gemma 4 integration:** official model and harness tools only; run identical agent configuration and deterministic seeds if possible; patch validation via tests.
7. **Paper revision:** publish per-task data, clustered confidence intervals, failures, limitations, and explicit measured hardware and runtime. Do not claim best-paper readiness until this exists.

## Data-leakage guardrail

Only issue text and pre-fix repo state are available to candidate selection. `patch` and `test_patch` are used to form labels and post hoc evaluation only; do not concatenate them into prompts, index their content, or use labels from held-out repositories during tuning.

## High-value hypotheses

- H1: Under matched budgets, adaptive retrieval has higher gold-symbol Recall@Budget than the lexical baseline.
- H2: As structural edges are removed, stability gating reduces degradation versus fixed graph fusion.
- H3: An offline Gemma 4 coding agent with adaptive retrieval improves issue resolution per second or per token.

Null hypotheses are equally important; report if H1–H3 fail.

## Suggested experiments: preregister settings

- k: 5, 10, 20 symbols
- Context budgets: 512, 1024, 2048, 4096 exact Gemma tokens
- Edge-corruption rates: 0, 0.10, 0.25, 0.50
- Seeds: 13, 17, 23, 29, 41
- Holdouts: leave-one-repository-out, group repeated snapshots by base_commit
- Scoring: paired bootstrap (with cluster structure where practical), overall and per-repository point estimates
- Reporting: all failures, data exclusions, compute/memory costs, hyperparameters, tool calls and model settings

## Potential Chinese open-source methodology inspiration

DeepSeekMath/DeepSeek-R1 uses group-relative optimization; for a future approach, treat evidence selection as a policy and construct verifiable rewards from fault localization, test success, and cost. This is only a possible extension once strong non-RL baselines exist. Cite methods and abide by model, license, and Kaggle restrictions. Do not substitute unapproved foundation models for the companion main-track agent, where the specific Gemma 4 variant is mandated.

## Final deadline

Paper Track: November 12, 2026 23:59 UTC (November 13, 2026 05:29 IST). After writing the draft in Kaggle, click its actual **Submit** action. A draft writeup alone is not an entry.
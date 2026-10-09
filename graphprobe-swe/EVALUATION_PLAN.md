# GraphProbe-SWE evaluation plan — v0.2

Updated October 9, 2026. Audit outcomes are known; the intervention is prospective.

## Completed evidence

- BudgetGraph frozen-input audit: 143 SWE-bench Lite tasks, 12 repositories.
- Primary macro repository Hit@5: BM25 0.6761437908496734; clean fusion 0.6024509803921568.
- Paired difference −0.07369281045751634; within-repository task-bootstrap 95% interval [−0.1224673202614379, −0.03127450980392166].
- Offline reconstruction of rankings and metrics passes all 20 expected aggregate comparisons and six correctness tests.
- Post hoc diagnostics and paired task outcomes are released in budgetgraph/results.
- This reproduces frozen retrieval features, not original source indexing, and does not evaluate repair.

## Next checkpoints

1. Independently rebuild all audit indexes from original SWE-bench issues and exact base commits. Compare query/corpus hashes, paths, BM25 arrays, edges, parse failures, and gold coverage. Report all failures; do not silently omit them.
2. Freeze an untouched confirmation set. The 143 audit tasks have informed the proposal; evaluations on these tasks remain exploratory. Use repository-disjoint confirmation where possible, group repeated commits, and deduplicate against competition tasks.
3. Correct the legacy GraphProbe module-prefix proxy before quantitative competition claims. Build source-based file maps and align patch hunks to AST spans at the base commit. Keep unavailable/added files in denominators; report unresolved symbols separately rather than quietly dropping difficult tasks.
4. Implement the proposed counterfactual gate using only pre-fix query/index features. The original graphprobe.py is a heuristic, not this gate.
5. Conduct exact-token localization comparisons, followed by a separate controlled Gemma repair study.

## Prospective protocol to freeze before running

- Primary localization endpoint: macro file Recall@2,048 exact tokens.
- Secondary budgets: 512, 1,024, and 4,096 tokens; Hit@k, reciprocal rank, harm/recovery counts, coverage, latency, tool calls, memory.
- Comparators: BM25; original audit fixed fusion/protected fusion; degree-normalized expansion; query-supported one-hop expansion; compatible semantic retrieval; legacy GraphProbe; proposed counterfactual gate.
- Use the same candidate universe, source snapshots, source snippets, tokenizer, and context assembly for every method.
- Separate outer repository evaluation folds from inner training/calibration folds. No threshold, cost weight, scaler, or model can be fit on the outer fold.
- Group issues sharing base commits within splits. Hash and publish manifests and settings before accessing held-out outcomes.
- Select one primary gate configuration inside training folds. Treat graph conditions, alternate budgets, and ablations as secondary; report all results.
- Paired uncertainty must respect commit grouping; report repository-specific estimates and explain what population each interval covers. A small repository count limits repository-level inference.

## Gate inputs and targets

Permitted inputs: issue text, pre-fix identifiers, lexical margins, top-k displacement, degree concentration, edge-type features, graph-perturbation sensitivity, candidate support relative to rewired controls, exact context cost, and compatible independent semantic/query evidence.

Training-fold targets may use patch-derived localization outcomes. Held-out patch/test labels may be used only by evaluation. They must never be retrieval features, choose the graph action for that issue, or enter the agent prompt.

Stability is not calibrated correctness. A hub may be stably irrelevant. The gate should abstain unless independent support and training-fold calibration justify lexical displacement. Its decision record is an audit trail, not a patch correctness certificate.

## Ablations

Remove counterfactual topology evidence, independent query support, hub penalties, and abstention independently. Compare edge deletion, injection, rewiring, and empty controls. Measure both recovered misses and lost lexical successes. Track gate coverage and harm as a function of threshold; do not report only its most favorable operating point.

## Gemma repair study (not yet executed)

Keep checkpoint, prompt, tool definitions, token/runtime budgets, trial count, seeds, and test environment identical. Vary retrieval only. Score patches with the official or separately frozen public harness. Report resolved tasks, failures, latency, memory, inspected tokens, and costs for failed runs too. Never provide reference fixes or held-out tests to the agent during inference.

SWE-bench audit results and competition development results must stay separate. Verify current competition checkpoint/data/rules before integration rather than relying on historical task counts.

## Related methodology

RepoGraph and GREPO are required structural comparisons/prior art; CS-RAG is relevant to structural sufficiency and fallback. GRPO from DeepSeekMath is a possible later training strategy, not an implemented method. Start with strong non-RL baselines and demonstrate a gate benefit before adding training complexity.

## Publication status

The v0.2 writeup reports measured audit outcomes and clearly marks proposed work. It is below the supplied 3,000-word limit. GitHub publication and a saved Markdown draft do not constitute a Kaggle submission. The previously supplied deadline is November 12, 2026, 23:59 UTC (November 13, 2026, 05:29 IST); verify it on Kaggle before submitting.

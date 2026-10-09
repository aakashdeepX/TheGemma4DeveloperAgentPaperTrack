# GraphProbe-SWE: When Code Graphs Hurt

**Subtitle:** A reproducible retrieval audit and a proposed framework for budget-aware graph trust

**Author:** Aakashdeep Srivastava  
**Track:** Google — The Gemma 4 Developer Agent Paper Track  
**Version:** 0.2 empirical audit and research proposal, October 9, 2026

## Abstract

Repository graphs can guide coding agents, but structural relevance need not match issue relevance. We present BudgetGraph, an offline reproducible audit of file retrieval on 143 public SWE-bench Lite issues from 12 repositories. Using frozen issue-conditioned BM25 scores and source-derived undirected import graphs, we compare lexical retrieval, personalized PageRank, fixed lexical–graph fusion, and fusion that preserves two lexical candidates under five graph conditions. At five retrieved files, macro repository Hit@5 is 67.61% for BM25 and 60.25% for clean-graph fusion: a difference of −7.37 percentage points, with a paired within-repository bootstrap 95% interval of [−12.25, −3.13]. Fusion harms 12 issues and recovers none at this budget. Post hoc diagnostics show that promoted files have much higher degree than displaced files, while correct edges yield only a small advantage over degree-preserving rewiring. These observations motivate GraphProbe-SWE, a proposed policy that tests structural evidence against counterfactual graphs and abstains when predicted benefit does not justify displacement or inspection cost. The audit is measured; the new policy and Gemma repair evaluation remain unvalidated. We release a checksum-verified notebook, offline runner, paired task outcomes, and a prospective evaluation plan.

## 1. Introduction

A local coding agent must identify relevant code before generating a fix. Its limited context makes retrieval errors consequential: a graph-promoted utility module can displace the faulty file even when both appear related to the issue. The question is not simply whether code graphs are useful, but when a particular structural signal should change a lexical ranking.

SWE-bench evaluates repository-level issue resolution [1], and RepoGraph shows that richer repository graphs can assist software engineering systems [2]. We study a narrower component: whether straightforward import-graph diffusion improves file localization at a fixed file budget. This is relevant to agent evidence acquisition, but it does not measure agent behavior or patch correctness.

Our present contributions are an executable retrieval audit, paired topology perturbations, and transparent characterization of graph-induced displacement. BudgetGraph is a derived reproducibility fixture from an existing benchmark, not a new collection of software issues. GraphProbe-SWE is the intervention motivated by the audit; it has not earned an improvement claim.

## 2. Data and Frozen Audit Protocol

The notebook records an exploratory protocol dated October 9, 2026, described there as fixed before retrieval experiments. This is an internal protocol record, not an independently timestamped preregistration. We preserve its settings rather than optimize them after observing results.

From the 300-task SWE-bench Lite test split [3], the protocol takes up to 20 issues per repository in SHA-256 instance-ID order. The artifact contains 143 tasks spanning 12 repositories, with three to 20 tasks per repository. This deterministic capped sample is not representative of all software projects.

Only `problem_statement` is used as the retrieval query; the corpus is Python source at each task's `base_commit`. The filter excludes tests, documentation, examples, benchmarks, setup scripts, and conftest files. Internal import edges are extracted with Python AST, resolving relative imports and common src/lib layouts, then made undirected. This graph omits many semantic and runtime dependencies.

Reference patches supply evaluation file paths after retrieval features are frozen. Patch contents, hints, test patches, and post-fix source are excluded from ranking. The scorer extracts production Python paths from `+++ b/` lines; added files remain in the denominator even when unavailable at the base commit. Deletion-only paths are not represented by this extractor. In the fixture every task has one gold path, and all 143 gold paths are present in the corpus.

The artifact represents 49,893 task-specific file instances and 232,084 undirected edges. Corpus size ranges from 21 to 862 files, with a median of 251. Fifteen AST parse-failure entries are recorded across task snapshots; these need not be distinct files. No eligible frozen task is excluded for missing gold coverage.

## 3. Methods, Controls, and Metrics

**BM25:** tokenize file paths and complete source with deterministic identifier splitting, using k1=1.5 and b=0.75. Break ties by file path.

**Personalized PageRank:** normalize nonnegative BM25 scores into personalization, using a uniform distribution when scores are all zero. Use restart probability 0.15 and 40 iterations, redistributing dangling mass through personalization. Convergence is not independently established.

**Fixed fusion:** separately normalize lexical and PageRank scores by their maxima, then rank by 0.7 × lexical + 0.3 × graph.

**Protected fusion:** preserve the first two BM25 files and fill subsequent positions from the fused ranking. This is a displacement safeguard, not a learned trust policy.

Pair all methods under five graph conditions: extracted edges; independent 50% edge deletion; random edge addition targeting twice the original count, subject to graph capacity; degree-preserving rewiring; and an empty graph. Random conditions use seeds 11, 23, 37, 53, and 71. Clean and empty conditions are deterministic. Rewiring uses a bounded swap procedure rather than guaranteed independent graph samples. All conditions share the corpus and lexical scores.

Report Hit@1/3/5/10/20, gold-file recall, all-gold coverage, and reciprocal rank, with both task-weighted and macro repository averages. With one gold file per task, Hit@k and gold-file Recall@k coincide numerically; this need not hold on multi-file issues. A file budget does not equal a token budget.

The recorded primary endpoint is clean-fusion minus BM25 macro repository Hit@5. Its paired bootstrap resamples tasks within the fixed repositories for 2,000 replicates, using seed 20261009. The interval describes this repository set, not new repositories; shared-commit correlations are not separately modeled. Secondary comparisons are exploratory without multiplicity correction.

## 4. Results

| Clean-graph method | Macro Hit@5 | Difference from BM25 |
|---|---:|---:|
| BM25 | 67.61% | 0.00 pp |
| Protected fusion | 61.15% | −6.46 pp |
| Fixed fusion | 60.25% | −7.37 pp |
| Personalized PageRank | 16.18% | −51.43 pp |

The primary difference has a 95% interval of [−12.25, −3.13] percentage points. Fusion loses 12 individual BM25 hits and gains zero; protecting two lexical files reduces the loss to 10 tasks without gaining a hit. These are unweighted counts, whereas headline percentages weight repositories equally. PageRank alone harms 76 tasks and improves two.

| Graph condition | Fusion macro Hit@5 | Difference from BM25 |
|---|---:|---:|
| Extracted edges | 60.25% | −7.37 pp |
| 50% edge deletion | 61.66% | −5.95 pp |
| Random edge addition | 61.65% | −5.97 pp |
| Degree-preserving rewiring | 59.58% | −8.04 pp |
| Empty graph | 67.61% | 0.00 pp |

The empty graph restores lexical ordering for all methods, providing an implementation control. Corrupted graphs do not consistently perform worse than extracted edges: edge deletion slightly improves fusion while leaving it below BM25. Graph completeness should not be equated with retrieval usefulness.

**Post hoc diagnostics:** fusion changes the top-five set on 120 tasks. Across these tasks, the median task-level mean degree is 94.5 for promoted files and 10.0 for displaced files. Promoted mean degree exceeds displaced mean degree in every changed task. This is descriptive evidence consistent with high-degree promotion, not proof that degree causes retrieval loss.

Extracted edges outperform degree-preserving rewiring by +0.67 percentage points in macro Hit@5, with a paired bootstrap interval of [0.00, 1.67]. Rewired graphs retain some original edges, and randomization is incomplete; this is not a pure estimate of semantic topology value. Both variants underperform BM25. All condition/method outcomes and repository breakdowns are released, including unfavorable results.

## 5. Proposed Intervention: Counterfactual Graph Trust

The audit motivates a different rule: a structural signal should justify the lexical evidence it displaces. Stability alone is insufficient because a consistently irrelevant hub can remain stable under edge deletion.

The proposed GraphProbe policy has four stages:

1. Form lexical candidates and structural expansions from pre-fix evidence.
2. Contrast support under extracted, edge-deleted, and degree-preserving rewired graphs. Measure ranking stability, hub concentration, and displacement of strong lexical candidates.
3. Combine these diagnostics with independent query evidence, such as explicit issue identifiers or compatible semantic retrieval, to estimate whether a structural change will help.
4. Accept the change only when predicted benefit exceeds displacement risk and inspection cost; otherwise preserve BM25.

A learned gate would estimate the held-out probability that changing context improves localization. Thresholds, feature scaling, and cost weights must be selected entirely within training folds. Reference-patch labels can supervise training-fold targets and score held-out decisions, but cannot become inference features or select the action on that same evaluation issue.

The proposed evidence record exposes promoted and displaced files, lexical scores, structural support, null-graph sensitivity, estimated cost, and the accept/abstain decision. It makes retrieval auditable; it does not certify patch correctness.

The existing `graphprobe.py` implements an earlier synthetic heuristic with degree normalization, edge-drop stability, and approximate context costs. It does not implement a calibrated counterfactual gate. Neither the prototype nor the proposal has demonstrated gains on this audit or competition development tasks. The implementation and proposal remain distinct.

## 6. Prospective Evaluation

The 143 audit tasks have already informed this proposal. Reusing them is exploratory even with repository holdouts; untouched tasks are needed for confirmation. Freeze a new evaluation manifest, partition repositories before inspecting labels, group repeated commits, and lock parameters in inner training folds.

Compare BM25, fixed and protected fusion, degree-normalized expansion, query-supported one-hop expansion, compatible semantic retrieval, the original GraphProbe heuristic, and the proposed gate. Match candidate universes and exact model-tokenizer budgets, recording tool and runtime costs. Ablate counterfactual topology evidence, independent query support, hub penalties, and abstention. Report harm and recovery rates alongside recall.

The prospective localization primary endpoint is macro file Recall@2,048 exact tokens, with paired outcomes, repository breakdowns, and uncertainty respecting commit grouping. Other budgets, perturbations, and efficiency curves are secondary. This endpoint has not been evaluated in this release.

A separate Gemma repair study will hold checkpoint, prompt, tools, seeds, runtime, and validation environment constant while varying evidence selection. Report resolved issues, failures, inspected tokens, wall time, and memory. Competition development data and SWE-bench Lite remain separate datasets with separate scores. No model inference, fine-tuning, or repair evaluation is completed here.

## 7. Related Work and Limitations

Agentless separates localization, repair, and validation [4]. RepoGraph evaluates richer repository navigation [2], while GREPO provides a larger benchmark for graph-based bug localization [5]. This small import-diffusion audit neither reproduces nor contradicts those systems. Its contribution is a controlled study of displacement and topology sensitivity in one configuration; broader novelty claims require stronger comparisons.

CS-RAG studies retrieval drift in imperfect knowledge graphs and uses sufficiency checks and textual recovery [6]. Its question-answering setting differs from code localization but provides relevant prior art for structural abstention. DeepSeekMath's GRPO [7] is an optional future inspiration for learning an evidence policy with verifiable rewards. No reinforcement learning or DeepSeek reproduction is implemented.

Limitations include public benchmark exposure, modest and uneven repository counts, artificial perturbations, incomplete imports, imperfect patch-file labels, and whole-file budgets. Independent reconstruction of all original source indexes remains outstanding. The negative result cautions against this fusion design; it does not reject all code graphs. The proposed intervention might fail or cost more than its benefit; either outcome must be reported.

## 8. Reproducibility and Availability

The self-contained BudgetGraph notebook embeds frozen retrieval inputs with compressed-payload SHA-256 `b3776bdfec1256911d1e329749095587eed5e36c4041fe88267d1bf6f6bc7bc0`. The offline Python/NumPy runner recomputes all rankings, 20 aggregate comparisons, paired intervals, diagnostics, and six correctness tests. All checks pass in this revision. Machine-readable task outcomes and execution metadata accompany the report. Optional notebook cells describe exact-commit source reconstruction, which was not performed in this update.

Project code follows the repository's Apache-2.0 license; benchmark and upstream material retain their original attribution and terms. AI assistance was used in research design, implementation, and writing; numerical claims come from executed computations. This Markdown file is a Kaggle-ready draft, not evidence of a saved or submitted Kaggle entry.

## References

[1] Jimenez, C. E., et al. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR. https://arxiv.org/abs/2310.06770

[2] Ouyang, S., et al. (2025). *RepoGraph: Enhancing AI Software Engineering with Repository-level Code Graph.* ICLR. https://arxiv.org/abs/2410.14684

[3] Princeton NLP. *SWE-bench Lite*, public test split. https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite

[4] Xia, C. S., et al. (2024). *Agentless: Demystifying LLM-based Software Engineering Agents.* https://arxiv.org/abs/2407.01489

[5] Wang, J., et al. (2026). *GREPO: A Benchmark for Graph Neural Networks on Repository-Level Bug Localization.* https://arxiv.org/abs/2602.13921

[6] Ma, Y., et al. (2026). *Toward Robust GraphRAG: Mitigating Retrieval Drift and Hallucination from Imperfect Knowledge Graphs.* https://arxiv.org/abs/2603.14828

[7] Shao, Z., et al. (2024). *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models.* https://arxiv.org/abs/2402.03300

Project: https://github.com/aakashdeepX/TheGemma4DeveloperAgentPaperTrack/tree/research/graphprobe-swe-v0.1/graphprobe-swe

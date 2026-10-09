# GraphProbe-SWE: Adaptive Evidence Acquisition for Offline Repository-Level Coding Agents

**Subtitle:** A graph-stability-aware retrieval policy and reproducible benchmark for reasoning under constrained context budgets

**Author:** Aakashdeep Srivastava  
**Track:** Google — The Gemma 4 Developer Agent Paper Track  
**Version:** 0.1 research prototype, October 9, 2026

## Abstract

Repository-level software repair requires deciding which code to inspect before attempting a patch. Under local-model inference constraints, indiscriminate retrieval consumes scarce context and can amplify errors in incomplete dependency graphs. We introduce **GraphProbe-SWE**, a proposed approach to budget-aware evidence acquisition for offline coding agents. The method combines issue-conditioned lexical retrieval, structural graph propagation, graph-edge perturbation diagnostics, and cost-sensitive context selection. Its key hypothesis is that choosing evidence according to diagnostic value and estimated graph reliability can outperform fixed top-*k* retrieval when the context budget is constrained. We also introduce the **GraphProbe-Bench protocol**, which evaluates fault-localization recall under matched inspection budgets and controlled graph corruption. A standalone standard-library prototype implements the baseline and graph-stability-aware ranking policies and passes a hand-authored smoke test. **No claim of superiority on Kaggle development tasks, hidden tasks, or Gemma 4 patch resolution is made in this version.** The accompanying protocol defines the experiments needed to test these claims rigorously.

## 1. Motivation and Research Question

The ability of an autonomous coding agent to generate a correct fix depends partly on retrieving the relevant code. For repository-scale issues, selecting insufficient context omits critical dependencies, while selecting too much context wastes compute and may distract a limited-capacity model. In the Gemma 4 Developer Agent competition, participating agents can inspect repository call/dependency graphs and use graph-backed code-search tools. The released development data contains 129 tasks from four Python repositories, associated AST graphs and 256-dimensional per-symbol embeddings [1,2].

The missing capability we investigate is **adaptive evidence acquisition**: instead of fixing the number of retrieved code symbols, can an agent estimate which observation to acquire next and when to stop? In particular, can it avoid over-trusting incomplete static graphs? The main falsifiable hypothesis is:

> Under equal context and tool budgets, a graph-reliability-aware evidence selection policy improves fault-location recall and/or end-to-end repair success over a lexical baseline and a fixed graph-expansion policy.

## 2. Proposed Method: GraphProbe-SWE

Let an issue be a text query *q* and a repository graph be *G=(V,E)*, whose vertices denote code symbols and whose typed edges denote static relationships. Each candidate code observation *v* has a retrieval score, an approximate inspection cost, and a graph-support score.

**Step A — Semantic and lexical seeds.** A deterministic BM25-style scorer ranks symbols using issue terms, qualified symbol names, and bounded source snippets. In the full experimental system, the competition's precomputed embeddings or graph-search service will supply a separately evaluated semantic retrieval signal. The v0.1 standalone prototype uses lexical scoring only; it does not fabricate query vectors to match existing symbol embeddings.

**Step B — Degree-normalized structural support.** Candidate ranking incorporates neighboring symbols' issue relevance while penalizing high-degree nodes. This tests whether structural associations contribute information beyond the lexical seed rankings.

**Step C — Graph trust assessment.** Recompute ranked candidates after several seeded random edge deletions, then measure the agreement of candidate sets with the original ranking using top-*k* Jaccard overlap. This agreement is a *heuristic sensitivity diagnostic*, not a probabilistically calibrated confidence value and not a proof of causality. A sensitive ranking receives less structural weight. The exact v0.1 policy uses five perturbation trials with a 25% edge-deletion rate and graph contribution bounded by 0.30; these are initial settings, not tuned findings.

**Step D — Budgeted evidence selection.** Select symbols greedily under a common approximate token budget. Candidate utility rewards issue relevance, penalizes redundant source text, and discounts large inspection costs. In a later stage, this heuristic will be replaced or complemented by a learned estimate of an observation's marginal contribution to localization. Any learned policy must be trained exclusively on training folds.

**Step E — Local repair and verification (planned).** Give a compact evidence package to the competition-compliant Gemma 4 agent, generate a candidate patch, and run available verification tests. The local agent must never see reference fixes or private evaluation tests during inference. A future evidence certificate will record inspected symbols and verifiable dependency links; it will not claim those links prove the patch correct.

The v0.1 source code implements A–D. Step E is **not** implemented, and this release is therefore a retrieval research prototype, not an end-to-end coding agent.

## 3. GraphProbe-Bench: A Reproducible Evaluation Protocol

We define a benchmark protocol with four independent dimensions:

1. **Localization under budget:** For each task, compare whether the retrieved symbol set contains a location associated with the reference patch while matching inspection-token and candidate-count budgets across methods.
2. **Context efficiency:** Record localization recall at increasing evidence budgets (e.g., 512, 1,024, 2,048, and 4,096 approximate tokens). Report area under the recall–budget curve instead of only one favorable operating point.
3. **Structural robustness:** Perturb 10%, 25%, and 50% of graph edges using fixed, published random seeds. Re-evaluate ranking and measure performance degradation. Distinguish missing-edge robustness from adversarially inserted misleading edges.
4. **Agent outcome:** With the same Gemma 4 checkpoint, prompt, number of trials, runtime limits, and patch-validation environment, compare success rates after feeding context selected by each method. Report runtime, tool calls, tokens, and test-pass rates.

The source `graphprobe.py` reads the published `tasks.jsonl` and task-named NetworkX JSON graphs. It uses reference patches **solely to derive evaluation labels**. Because its initial label matcher infers module paths from qualified symbol names, the emitted `hit_file` variable is only a **proxy**; it can give false positives for ambiguous modules. Publication-quality results must instead map patch hunks to AST symbol spans at each frozen repository commit. The benchmark must also reject tasks with unresolvable ground truth rather than quietly scoring them as failures or successes.

## 4. Experimental Design and Pre-Registration

We will test three primary methods: **L** (lexical issue-to-symbol retrieval), **G** (fixed 70/30 lexical/graph fusion), and **P** (GraphProbe, dynamically down-weighting graph support based on edge-deletion stability and choosing cost-sensitive, less-redundant context). All methods receive the same input issue and graph, and will be compared under equivalent context limits. A fourth baseline, competition-native embedding retrieval, will be added when run in the official Kaggle environment.

To avoid tuning to the four public repositories, conduct leave-one-repository-out evaluation: train or select parameters on three repositories and report results on the fourth. Group multiple issues from the same base commit in the same split. Never use `patch`, `test_patch`, or any generated ground-truth label as a retrieval feature. Hyperparameters and pre-processing decisions must be fixed before inspecting held-out outcomes.

**Primary metrics:** file-level Recall@Budget, symbol-level Recall@Budget, and patch resolution rate. **Secondary metrics:** mean reciprocal rank, inspection tokens, wall-clock time, graph-stability scores, and degradation under structural perturbation. Calculate 95% uncertainty intervals via paired bootstrap resampling clustered by repository or commit where feasible; report raw paired outcomes and per-repository breakdowns. A strong negative result—lexical search outperforming graph-based methods—will be reported rather than hidden.

**Ablations:** remove graph support, remove graph-stability gating, remove redundancy discounting, remove cost normalization, and vary the perturbation rate and context budget. Compare against a simple random-edge baseline to establish whether additional complexity is warranted. If an LLM is added, hold model and tool budget constant and vary only the retrieval policy.

## 5. Prototype Status and Reproducibility

As of October 9, 2026, the reproducible v0.1 package contains a pure-Python retrieval/reranking implementation, a hand-authored fixture, an optional reader for the organizer's task and graph files, and machine-readable evaluation outputs. The smoke test exercises all three policies and checks that each retrieves a relevant file in one deliberately small fixture. This is an **implementation sanity check only**: it demonstrates that the code executes but says nothing about real-world effectiveness or statistical significance. The provided script can run on CPU without a model download or network connection.

We have **not** run the 129 real development tasks in this version, **not** measured confidence calibration, **not** trained Gemma 4, and **not** submitted patches to the main competition. We therefore report no performance percentages or improvement claims. Results and a corrected AST-aligned benchmark will be added after real-data evaluation.

## 6. Relation to Prior Work

SWE-bench provides a repository-level issue-resolution evaluation framework [3]. Agentless established that careful localization, repair, and validation can be effective without elaborate general-purpose agency [4]. SWE-Gym studies executable software-engineering tasks and model/verification training [5]. DeepSeekMath introduced group relative policy optimization (GRPO), a possible *future* strategy for learning evidence-selection policies from relative task outcomes [6]. We cite GRPO as an inspiration, **not** as an implemented training algorithm or a claim to have reproduced DeepSeek. Related open coding-agent work, including Qwen3-Coder, motivates research on cost-effective tool use [7].

Our proposed distinction is the **controlled study of when structural graph evidence is worth acquiring** under a fixed inspection budget, with explicit graph-corruption diagnostics and no dependence on proprietary model APIs. This combination must still be evaluated against contemporary graph-localization papers before it can be considered a novel empirical contribution.

## 7. Limitations, Risks, and Next Steps

Static edge deletion only models one kind of graph defect; realistic missing call targets, dynamic dispatch, misleading edges, tests, and cross-language dependencies require separate experiments. Approximate tokens are not model-tokenizer measurements, and the v0.1 ranking heuristics are not calibrated probabilities. The four-repository development dataset is narrow, and hidden-set outcomes cannot be inferred from it. Some task families may be better served by lexical retrieval alone. GraphProbe could also be slower than a simpler baseline, making efficiency claims particularly important to test.

The next milestone is to execute the public-data benchmark, replace approximate file labels with AST-aligned ground truth, publish paired per-task results and ablations, and integrate a Gemma 4 agent using the officially permitted tools and checkpoint. This submission is an explicit early research report, not a claim of achieved state of the art.

## References

[1] Markowitz, E., et al. (2026). *Google — The Gemma 4 Developer Agent Paper Track*. Kaggle. https://www.kaggle.com/competitions/gemma-4-developer-agent-paper

[2] Holbrook, R. (2026). *Getting Started — Gemma 4 Developer Agent*. Kaggle. https://www.kaggle.com/code/ryanholbrook/getting-started-gemma-4-developer-agent

[3] Jimenez, C. E., et al. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR. https://arxiv.org/abs/2310.06770

[4] Xia, C. S., Deng, Y., Dunn, S., and Zhang, L. (2024). *Agentless: Demystifying LLM-based Software Engineering Agents*. https://arxiv.org/abs/2407.01489

[5] Pan, J., et al. (2025). *Training Software Engineering Agents and Verifiers with SWE-Gym*. ICML. https://proceedings.mlr.press/v267/pan25g.html

[6] Shao, Z., et al. (2024). *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models*. https://arxiv.org/abs/2402.03300

[7] Qwen Team. (2025). *Qwen3-Coder: Agentic Coding in the World*. https://qwenlm.github.io/blog/qwen3-coder/
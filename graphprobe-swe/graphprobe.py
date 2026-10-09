"""GraphProbe-SWE v0.1: reproducible research scaffold (stdlib only).

IMPORTANT: This is a deterministic heuristic prototype, NOT a trained Gemma-4 agent.
Reference patches are used strictly inside evaluation functions.
"""
from __future__ import annotations
import collections
import json
import math
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

STOP = set('the a an to for of in from on at by and or with is are was were be been as it this that can cannot when then not no does do using use into should i you we code bug issue function file class expected actual error fix return returns new old after before every all each where why what how which could'.split())


def tokenize(s: str) -> list[str]:
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', s)
    return [w for w in re.findall(r'[A-Za-z_][A-Za-z_0-9]*', s.lower().replace('_', ' ')) if len(w) > 2 and w not in STOP]


def normalize(values: Mapping[str, float]) -> dict[str, float]:
    vmax = max(values.values(), default=0.0)
    return {k: (v / vmax if vmax > 1e-12 else 0.0) for k, v in values.items()}


@dataclass
class Graph:
    nodes: dict[str, str]
    edges: list[tuple[str, str, str]]

    @classmethod
    def from_json(cls, path: str | Path) -> 'Graph':
        raw = json.loads(Path(path).read_text(encoding='utf-8'))
        return cls(
            nodes={str(n['id']): str(n.get('text', '') or '') for n in raw['nodes']},
            edges=[(str(e['source']), str(e['target']), str(e.get('type', 'unknown'))) for e in raw['edges']]
        )


def bm25(issue: str, graph: Graph) -> dict[str, float]:
    """Issue-conditioned BM25-style lexical baseline, no external embeddings."""
    q = collections.Counter(tokenize(issue))
    docs = {n: collections.Counter(tokenize(n.replace('.', ' ') + ' ' + text[:1600]))
            for n, text in graph.nodes.items()}
    N = len(docs)
    if not N:
        return {}
    df = collections.Counter()
    for d in docs.values():
        df.update(d.keys())
    avg_len = max(1, sum(sum(d.values()) for d in docs.values()) / N)
    results = {}
    for node, doc in docs.items():
        dl = sum(doc.values())
        score = 0.0
        for term, qtf in q.items():
            freq = doc.get(term, 0)
            if freq:
                idf = math.log(1 + (N - df[term] + 0.5) / (df[term] + 0.5))
                score += min(qtf, 2) * idf * (freq * 2.2) / (freq + 1.2 * (0.25 + 0.75 * dl / avg_len))
        results[node] = score
    return normalize(results)


def graph_support(seeds: Mapping[str, float], graph: Graph, *, drop: float = 0, seed: int = 13) -> dict[str, float]:
    """Undirected one-step contextual support with degree normalization."""
    rng = random.Random(seed)
    kept = [(u, v) for u, v, typ in graph.edges
            if u in seeds and v in seeds and rng.random() >= drop]
    degrees = collections.Counter()
    for u, v in kept:
        degrees[u] += 1
        degrees[v] += 1
    support = collections.defaultdict(float)
    for u, v in kept:
        # Penalize hubs, so frequently referenced utility nodes do not dominate.
        support[v] += seeds[u] / math.sqrt(max(1, degrees[u] * degrees[v]))
        support[u] += seeds[v] / math.sqrt(max(1, degrees[u] * degrees[v]))
    return normalize({node: support[node] for node in seeds})


def rank_methods(issue: str, graph: Graph, *, n_probe: int = 5, seed: int = 17):
    """Three policies: lexical, fixed graph mixing, stability-gated graph mixing."""
    lex = bm25(issue, graph)
    full_graph = graph_support(lex, graph)
    combined = {n: 0.7 * lex[n] + 0.3 * full_graph[n] for n in lex}
    top_n = min(20, max(1, len(lex)))
    top_full = {n for n, _ in sorted(combined.items(), key=lambda x: (-x[1], x[0]))[:top_n]}
    similarities = []
    for trial in range(n_probe):
        perturbed = graph_support(lex, graph, drop=0.25, seed=seed + trial)
        test_scores = {n: 0.7 * lex[n] + 0.3 * perturbed[n] for n in lex}
        top_other = {n for n, _ in sorted(test_scores.items(), key=lambda x: (-x[1], x[0]))[:top_n]}
        similarities.append(len(top_full & top_other) / max(1, len(top_full | top_other)))
    stability = sum(similarities) / max(1, len(similarities))
    # Stability here is a diagnostic heuristic, not a calibrated probability.
    graph_weight = 0.3 * stability
    adaptive = {n: (1 - graph_weight) * lex[n] + graph_weight * full_graph[n] for n in lex}
    return {'lexical': lex, 'fixed_graph': combined, 'adaptive_graph': adaptive}, stability


def cost_estimate(text: str) -> int:
    """Approximate token count. Replace with exact tokenizer in main experiments."""
    return max(12, int(len(text) / 4))


def pick_context(scores: Mapping[str, float], graph: Graph, *, max_tokens: int = 1800,
                 k: int = 10, diversity: bool = True) -> list[str]:
    selected = []
    spent = 0
    candidates = sorted(scores, key=lambda n: (-scores[n], n))[:max(60, k * 12)]
    while len(selected) < k:
        best_node, best_priority, best_cost = None, -1.0, 0
        for node in candidates:
            if node in selected:
                continue
            c = min(450, cost_estimate(graph.nodes[node]))
            if spent + c > max_tokens:
                continue
            current_tokens = set(tokenize(node + ' ' + graph.nodes[node][:800]))
            redundancy = max((len(current_tokens & set(tokenize(s + ' ' + graph.nodes[s][:800]))) /
                              max(1, len(current_tokens | set(tokenize(s + ' ' + graph.nodes[s][:800]))))
                              for s in selected), default=0.0)
            value = max(0.0, scores[node] - (0.16 * redundancy if diversity else 0.0))
            priority = value / math.sqrt(c)
            if priority > best_priority:
                best_node, best_priority, best_cost = node, priority, c
        if best_node is None:
            break
        selected.append(best_node)
        spent += best_cost
    return selected


def patch_paths(patch: str) -> set[str]:
    """EXCLUSIVE EVALUATION: read reference patch file paths; never call from rank_methods."""
    paths = set()
    for line in patch.splitlines():
        if line.startswith('+++ b/'):
            path = line[6:]
            if path.endswith('.py') and not ('/test' in path or path.startswith('test')):
                paths.add(path.replace('\\', '/'))
    return paths


def possible_paths(node: str) -> set[str]:
    parts = node.split('.')
    return {'/'.join(parts[:i]) + '.py' for i in range(1, len(parts) + 1)} | {
        '/'.join(parts[:i]) + '/__init__.py' for i in range(1, len(parts) + 1)}


def evaluate_task(issue: str, graph: Graph, reference_patch: str, *, budget: int = 1800):
    """Only a proxy file-level metric; for definitive symbol-level metrics use AST spans."""
    gold = patch_paths(reference_patch)
    policies, stability = rank_methods(issue, graph)
    result = {'graph_stability': round(stability, 4), 'gold_paths': sorted(gold)}
    for name, scores in policies.items():
        chosen = pick_context(scores, graph, max_tokens=budget, diversity=(name == 'adaptive_graph'))
        matched = sorted(gold & set().union(*(possible_paths(n) for n in chosen))) if chosen else []
        result[name] = {'selected': chosen, 'hit_file': bool(matched), 'matched_paths': matched,
                        'approx_tokens': sum(min(450, cost_estimate(graph.nodes[n])) for n in chosen)}
    return result


def evaluate_folder(root: str | Path, *, max_tasks: int = 129, budget: int = 1800):
    """Read Kaggle's public 129-task data if mounted locally; no data redistribution."""
    root = Path(root)
    tasks = root / 'tasks.jsonl'
    graphs = root / 'graphs'
    if not tasks.exists() or not graphs.exists():
        raise FileNotFoundError(f'Expect tasks.jsonl and graphs/ under {root}')
    output = []
    with tasks.open(encoding='utf-8') as fp:
        for line in fp:
            if len(output) >= max_tasks:
                break
            record = json.loads(line)
            if not record.get('patch'):
                continue
            path = graphs / (record['instance_id'] + '.json')
            if not path.exists():
                continue
            data = evaluate_task(record['problem_statement'], Graph.from_json(path), record['patch'], budget=budget)
            output.append({'instance_id': record['instance_id'], 'repo': record['repo'], **data})
    return output


def summarize(rows: Sequence[dict]):
    valid = [r for r in rows if r['gold_paths']]
    return {name: {'hit_at_budget': round(sum(r[name]['hit_file'] for r in valid) / len(valid), 4)
                if valid else None, 'n': len(valid)}
            for name in ('lexical', 'fixed_graph', 'adaptive_graph')}


def fixture():
    """Hand-authored fixture demonstrates API behavior; it is NOT scientific evaluation."""
    graph = Graph(nodes={
        'shop.cart.checkout': 'def checkout(cart): return invoice_total(cart.items)',
        'shop.cart.invoice_total': 'def invoice_total(items): return sum(item.price * item.quantity for item in items)',
        'shop.cart.format_receipt': 'def format_receipt(order): return str(order)',
        'shop.users.login': 'def login(user): return validate_password(user)',
        'shop.users.validate_password': 'def validate_password(user): return True',
        'shop.reports.monthly_report': 'def monthly_report(items): return invoice_total(items)',
    }, edges=[
        ('shop.cart.checkout', 'shop.cart.invoice_total', 'calls'),
        ('shop.reports.monthly_report', 'shop.cart.invoice_total', 'calls'),
        ('shop.users.login', 'shop.users.validate_password', 'calls')
    ])
    issue = 'Invoice total for checkout is wrong when line item quantity increases.'
    patch = 'diff --git a/shop/cart.py b/shop/cart.py\n--- a/shop/cart.py\n+++ b/shop/cart.py\n@@ -1 +1 @@\n-old\n+new'
    return issue, graph, patch


if __name__ == '__main__':
    issue, graph, patch = fixture()
    result = evaluate_task(issue, graph, patch)
    print(json.dumps({'fixture_only': True, 'policies': result, 'warning':
        'Demonstration fixture only; not a Gemma-4 result and not a real task benchmark.'}, indent=2))

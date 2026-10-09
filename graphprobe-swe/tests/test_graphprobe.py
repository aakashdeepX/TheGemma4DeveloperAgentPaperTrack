import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from graphprobe import Graph, bm25, graph_support, rank_methods, pick_context, patch_paths, fixture, evaluate_task

class TestGraphProbe(unittest.TestCase):
    def test_bm25_retrieval(self):
        issue, graph, _ = fixture()
        scores = bm25(issue, graph)
        self.assertEqual(len(scores), len(graph.nodes))
        self.assertGreater(scores['shop.cart.invoice_total'], scores['shop.users.login'])

    def test_determinism(self):
        issue, graph, _ = fixture()
        a = rank_methods(issue, graph)
        b = rank_methods(issue, graph)
        self.assertEqual(a,b)

    def test_context_budget(self):
        issue, graph, _ = fixture()
        scores = bm25(issue, graph)
        self.assertLessEqual(len(pick_context(scores, graph, max_tokens=100,k=2)),2)

    def test_patch_parser(self):
        _, _, patch = fixture()
        self.assertEqual(patch_paths(patch), {'shop/cart.py'})

    def test_no_patch_in_retrieval(self):
        issue, graph, patch = fixture()
        a = evaluate_task(issue, graph, patch)
        b = evaluate_task(issue, graph,patch.replace('shop/cart.py','other/path.py'))
        for method in ('lexical','fixed_graph','adaptive_graph'):
            self.assertEqual(a[method]['selected'],b[method]['selected'])

    def test_graph_support_handles_missing_edges(self):
        _, graph, _ = fixture()
        scores = {n:1.0 for n in graph.nodes}
        self.assertTrue(all(v == 0.0 for v in graph_support(scores,Graph(graph.nodes,[])).values()))

if __name__=='__main__':
    unittest.main()

import unittest
from engine.policy_engine import get_rule, evaluate_percentage, evaluate_first_goods_receipt


class PolicyEngineTests(unittest.TestCase):
    def setUp(self):
        self.olist = get_rule("olist", "OL-DEL-001", "2026-10-27")
        self.bpi = get_rule("bpi", "BP-GR-001", "2026-10-27")

    def test_olist_historical_illustration(self):
        r = evaluate_percentage(self.olist, 89936, 96470)
        self.assertEqual(r["decision"], "below_target")
        self.assertAlmostEqual(r["observed"], 93.2269, places=3)

    def test_exact_target(self):
        self.assertEqual(evaluate_percentage(self.olist, 97, 100)["decision"], "meets_target")

    def test_no_denominator(self):
        self.assertEqual(evaluate_percentage(self.olist, 0, 0)["decision"], "insufficient_data")

    def test_invalid_numerator(self):
        self.assertEqual(evaluate_percentage(self.olist, 2, 1)["decision"], "insufficient_data")

    def test_category_is_required(self):
        self.assertEqual(evaluate_first_goods_receipt(self.bpi, None, "2026-03-01", "2026-03-04")["decision"], "insufficient_data")

    def test_other_category_not_applicable(self):
        self.assertEqual(evaluate_first_goods_receipt(self.bpi, "SERVICE", "2026-03-01", "2026-03-31")["decision"], "not_applicable")

    def test_twelve_day_boundary(self):
        self.assertEqual(evaluate_first_goods_receipt(self.bpi, "STD_MATERIAL", "2026-03-01", "2026-03-13")["decision"], "meets_target")

    def test_thirteen_days(self):
        self.assertEqual(evaluate_first_goods_receipt(self.bpi, "STD_MATERIAL", "2026-03-01", "2026-03-14")["decision"], "below_target")

    def test_wrong_event_sequence(self):
        self.assertEqual(evaluate_first_goods_receipt(self.bpi, "STD_MATERIAL", "2026-03-14", "2026-03-01")["decision"], "insufficient_data")

    def test_cross_domain_lookup_rejected(self):
        with self.assertRaises(ValueError):
            get_rule("olist", "BP-GR-001", "2026-10-27")

    def test_before_effective_date_rejected(self):
        with self.assertRaises(ValueError):
            get_rule("olist", "OL-DEL-001", "2025-01-01")


if __name__ == "__main__":
    unittest.main()

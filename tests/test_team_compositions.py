import json
import unittest
from collections import Counter
from itertools import combinations

import pandas as pd

from Config import Config
from services.mining_service import MiningService
from src.data.preprocessing import DataPreprocessor
from src.mining.apriori_miner import AprioriMiner
from src.mining.fpgrowth_miner import FPGrowthMiner


class TeamCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = pd.read_csv(Config.RAW_DATA_PATH)
        cls.service = MiningService()

    def test_transactions_preserve_one_team_and_one_result_per_row(self):
        transactions, processed = DataPreprocessor().process_transactions()
        self.assertEqual(len(transactions), len(self.raw))
        self.assertEqual(len(transactions), 462)
        self.assertTrue(all(sum(item.startswith("HERO::") for item in tx) == 5 for tx in transactions))
        self.assertTrue(all(sum(item.startswith("RESULT::") for item in tx) == 1 for tx in transactions))
        for _, game in processed.groupby("game_id"):
            self.assertEqual(len(game), 2)
            self.assertEqual(game["team_id"].nunique(), 2)
            self.assertEqual(int(game["is_winner"].sum()), 1)

    def test_lookup_counts_match_raw_data_for_team_sizes_two_to_five(self):
        first_heroes = json.loads(self.raw.iloc[0]["hero_ids"])
        for size in range(2, 6):
            selected = first_heroes[:size]
            result = self.service.get_team_compositions(min_matches=1, selected_heroes=selected)["selected"]
            matches = wins = 0
            for _, row in self.raw.iterrows():
                heroes = set(json.loads(row["hero_ids"]))
                if set(selected).issubset(heroes):
                    matches += 1
                    wins += bool(row["is_winner"])
            self.assertTrue(result["found"])
            self.assertEqual(result["matches"], matches)
            self.assertEqual(result["wins"], wins)
            self.assertEqual(result["losses"], matches - wins)
            self.assertAlmostEqual(result["win_rate"], wins / matches)
            self.assertAlmostEqual(result["support"], matches / len(self.raw))
            self.assertAlmostEqual(result["confidence"], wins / matches)

    def test_absent_and_low_sample_combinations_are_labeled(self):
        appearances = Counter()
        hero_ids = set()
        for raw_heroes in self.raw["hero_ids"]:
            heroes = json.loads(raw_heroes)
            hero_ids.update(heroes)
            appearances.update(combinations(sorted(heroes), 2))
        absent = next(pair for pair in combinations(sorted(hero_ids), 2) if pair not in appearances)
        missing = self.service.get_team_compositions(min_matches=1, selected_heroes=absent)["selected"]
        self.assertFalse(missing["found"])
        low_sample = next(pair for pair, count in appearances.items() if count < 10)
        lookup = self.service.get_team_compositions(min_matches=1, selected_heroes=low_sample)["selected"]
        self.assertEqual(lookup["rating"], "insufficient")
        self.assertLess(MiningService._wilson_lower_bound(2, 2), MiningService._wilson_lower_bound(80, 100))

    def test_apriori_and_fp_growth_find_identical_itemsets_on_real_data(self):
        transactions = DataPreprocessor().process_transactions()[0]
        for max_heroes in range(2, 6):
            params = {"min_support": 0.1, "min_confidence": 0.5, "min_lift": 0.0, "max_heroes": max_heroes}
            apriori_sets, _ = AprioriMiner(**params).run_mining(transactions)
            fpgrowth_sets, _ = FPGrowthMiner(**params).run_mining(transactions)
            apriori_values = {frozenset(row) for row in apriori_sets["itemsets"]}
            fpgrowth_values = {frozenset(row) for row in fpgrowth_sets["itemsets"]}
            self.assertEqual(apriori_values, fpgrowth_values)
            self.assertTrue(all(sum(str(item).startswith("HERO::") for item in row) <= max_heroes for row in apriori_values))


if __name__ == "__main__":
    unittest.main()

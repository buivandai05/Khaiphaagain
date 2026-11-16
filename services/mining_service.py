import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.data.preprocessing import DataPreprocessor
from src.mining.apriori_miner import AprioriMiner
from src.mining.fpgrowth_miner import FPGrowthMiner
from src.mining.comparison import AlgorithmComparer

class MiningService:
    def __init__(self):
        self.preprocessor = DataPreprocessor()

    def get_dashboard_stats(self):
        """Lấy các chỉ số thống kê tổng quan cho Dashboard"""
        try:
            transactions, df_proc = self.preprocessor.process_transactions()
            total_transactions = len(transactions)
            win_count = int(df_proc['is_winner'].sum())
            lose_count = total_transactions - win_count
            
            # Đếm số lượng hero duy nhất xuất hiện
            all_items = [item for tx in transactions for item in tx if item.startswith("HERO::")]
            unique_heroes = len(set(all_items))

            return {
                'total_games': total_transactions // 2,
                'total_teams': total_transactions,
                'unique_heroes': unique_heroes,
                'total_transactions': total_transactions,
                'win_count': win_count,
                'lose_count': lose_count
            }
        except Exception as e:
            return {'error': str(e)}

    def run_apriori(self, min_support=0.03, min_confidence=0.5, min_lift=1.0):
        """Chạy Apriori và định dạng kết quả trả về"""
        transactions, _ = self.preprocessor.process_transactions()
        miner = AprioriMiner(min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)
        itemsets, rules = miner.run_mining(transactions)
        win_rules = miner.filter_win_rules(rules)

        return {
            'execution_time': round(miner.execution_time, 4),
            'itemsets_count': len(itemsets),
            'rules_count': len(rules),
            'win_rules_count': len(win_rules),
            'rules': rules.to_dict(orient='records') if not rules.empty else []
        }

    def run_fpgrowth(self, min_support=0.03, min_confidence=0.5, min_lift=1.0):
        """Chạy FP-Growth và định dạng kết quả trả về"""
        transactions, _ = self.preprocessor.process_transactions()
        miner = FPGrowthMiner(min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)
        itemsets, rules = miner.run_mining(transactions)
        win_rules = miner.filter_win_rules(rules)

        return {
            'execution_time': round(miner.execution_time, 4),
            'itemsets_count': len(itemsets),
            'rules_count': len(rules),
            'win_rules_count': len(win_rules),
            'rules': rules.to_dict(orient='records') if not rules.empty else []
        }

    def run_comparison(self, min_support=0.03, min_confidence=0.5, min_lift=1.0):
        """Chạy so sánh 2 thuật toán"""
        transactions, _ = self.preprocessor.process_transactions()
        comparer = AlgorithmComparer(min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)
        result_dict, _ = comparer.compare(transactions)
        return result_dict
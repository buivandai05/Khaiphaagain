import os
import sys
import pandas as pd

# Thêm thư mục gốc dự án vào sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.data.preprocessing import DataPreprocessor
from src.mining.apriori_miner import AprioriMiner
from src.mining.fpgrowth_miner import FPGrowthMiner

class AlgorithmComparer:
    def __init__(self, min_support=0.03, min_confidence=0.5, min_lift=1.0):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift

    def compare(self, transactions):
        """
        Chạy cả 2 thuật toán trên cùng tập transactions và thu thập thông số so sánh
        """
        # 1. Chạy Apriori
        apriori_miner = AprioriMiner(
            min_support=self.min_support, 
            min_confidence=self.min_confidence, 
            min_lift=self.min_lift
        )
        ap_itemsets, ap_rules = apriori_miner.run_mining(transactions)
        ap_win_rules = apriori_miner.filter_win_rules(ap_rules)

        # 2. Chạy FP-Growth
        fpgrowth_miner = FPGrowthMiner(
            min_support=self.min_support, 
            min_confidence=self.min_confidence, 
            min_lift=self.min_lift
        )
        fp_itemsets, fp_rules = fpgrowth_miner.run_mining(transactions)
        fp_win_rules = fpgrowth_miner.filter_win_rules(fp_rules)

        # 3. Tổng hợp kết quả so sánh
        comparison_result = {
            'parameters': {
                'min_support': self.min_support,
                'min_confidence': self.min_confidence,
                'min_lift': self.min_lift,
                'total_transactions': len(transactions)
            },
            'apriori': {
                'execution_time_sec': round(apriori_miner.execution_time, 4),
                'frequent_itemsets_count': len(ap_itemsets),
                'total_rules_count': len(ap_rules),
                'win_rules_count': len(ap_win_rules)
            },
            'fpgrowth': {
                'execution_time_sec': round(fpgrowth_miner.execution_time, 4),
                'frequent_itemsets_count': len(fp_itemsets),
                'total_rules_count': len(fp_rules),
                'win_rules_count': len(fp_win_rules)
            }
        }

        # 4. Tạo DataFrame để hiển thị dạng bảng
        summary_df = pd.DataFrame([
            {
                'Thuật toán': 'Apriori',
                'Thời gian chạy (giây)': comparison_result['apriori']['execution_time_sec'],
                'Số tập phổ biến': comparison_result['apriori']['frequent_itemsets_count'],
                'Số luật kết hợp': comparison_result['apriori']['total_rules_count'],
                'Số luật Win': comparison_result['apriori']['win_rules_count']
            },
            {
                'Thuật toán': 'FP-Growth',
                'Thời gian chạy (giây)': comparison_result['fpgrowth']['execution_time_sec'],
                'Số tập phổ biến': comparison_result['fpgrowth']['frequent_itemsets_count'],
                'Số luật kết hợp': comparison_result['fpgrowth']['total_rules_count'],
                'Số luật Win': comparison_result['fpgrowth']['win_rules_count']
            }
        ])

        return comparison_result, summary_df

if __name__ == '__main__':
    # Nạp dữ liệu đã xử lý
    preprocessor = DataPreprocessor()
    transactions, _ = preprocessor.process_transactions()

    # Khởi tạo bộ so sánh
    comparer = AlgorithmComparer(min_support=0.03, min_confidence=0.5, min_lift=1.0)
    result_dict, summary_table = comparer.compare(transactions)

    print("\n" + "=" * 60)
    print("      KẾT QUẢ SO SÁNH HIỆU NĂNG THUẬT TOÁN")
    print("=" * 60)
    print(summary_table.to_string(index=False))
    print("=" * 60)
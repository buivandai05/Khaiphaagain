import os
import sys
import time
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# Thêm thư mục gốc dự án vào sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.data.preprocessing import DataPreprocessor

class FPGrowthMiner:
    def __init__(self, min_support=0.03, min_confidence=0.5, min_lift=1.0):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.execution_time = 0.0

    def encode_transactions(self, transactions):
        """Chuyển danh sách transactions thành bảng One-Hot (True/False)"""
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        return df_encoded

    def run_mining(self, transactions):
        """
        Chạy thuật toán FP-Growth và khai phá luật kết hợp:
        - Đo thời gian thực thi.
        - Xây dựng FP-Tree và tìm frequent itemsets.
        - Sinh association rules.
        """
        start_time = time.time()

        # 1. Mã hóa dữ liệu thành mảng One-Hot
        df_encoded = self.encode_transactions(transactions)

        # 2. Chạy thuật toán FP-Growth
        frequent_itemsets = fpgrowth(
            df_encoded, 
            min_support=self.min_support, 
            use_colnames=True
        )

        self.execution_time = time.time() - start_time

        if frequent_itemsets.empty:
            print("⚠️ FP-Growth không tìm thấy tập phổ biến nào với ngưỡng Support đã cho.")
            return frequent_itemsets, pd.DataFrame()

        # 3. Tạo Association Rules
        rules = association_rules(
            frequent_itemsets, 
            metric="confidence", 
            min_threshold=self.min_confidence
        )

        # Lọc luật theo min_lift
        if not rules.empty and self.min_lift > 0:
            rules = rules[rules['lift'] >= self.min_lift]

        print(f"✅ FP-Growth chạy xong trong: {self.execution_time:.4f} giây")
        print(f"📊 Tìm thấy {len(frequent_itemsets)} tập phổ biến và {len(rules)} luật kết hợp.")

        return frequent_itemsets, rules

    def filter_win_rules(self, rules):
        """Lọc các luật có vế sau (consequents) dẫn tới RESULT::WIN"""
        if rules.empty:
            return pd.DataFrame()

        def is_win_rule(consequents):
            return "RESULT::WIN" in consequents

        win_rules = rules[rules['consequents'].apply(is_win_rule)].copy()
        return win_rules

if __name__ == '__main__':
    # Đọc dữ liệu đã tiền xử lý
    preprocessor = DataPreprocessor()
    transactions, _ = preprocessor.process_transactions()

    # Thử nghiệm khai phá với cùng tham số cấu hình như Apriori
    miner = FPGrowthMiner(min_support=0.03, min_confidence=0.5, min_lift=1.0)
    itemsets, rules = miner.run_mining(transactions)

    # In mẫu kết quả tập phổ biến
    print("\n📝 Mẫu 5 Tập Phổ Biến Đầu Tiên (FP-Growth):")
    if not itemsets.empty:
        print(itemsets.head().to_string())

    # In mẫu các luật dẫn tới chiến thắng
    win_rules = miner.filter_win_rules(rules)
    print(f"\n🏆 Mẫu 5 Luật Dẫn Đến CHIẾN THẮNG (FP-Growth) [Tổng số luật WIN: {len(win_rules)}]:")
    if not win_rules.empty:
        print(win_rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head().to_string())
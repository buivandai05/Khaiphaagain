import os
import sys
import json
import pandas as pd

# Thêm thư mục gốc dự án vào sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from Config import Config

class DataPreprocessor:
    def __init__(self, raw_data_path=None, processed_data_path=None):
        self.raw_data_path = raw_data_path or Config.RAW_DATA_PATH
        self.processed_data_path = processed_data_path or Config.PROCESSED_DATA_PATH

    def load_raw_data(self):
        """Đọc file CSV dữ liệu thô"""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu thô tại: {self.raw_data_path}")
        return pd.read_csv(self.raw_data_path)

    def process_transactions(self):
        """
        Tiền xử lý dữ liệu:
        1. Parse JSON hero_ids -> Python list
        2. Gắn tiền tố 'HERO::' cho tướng và 'RESULT::WIN'/'RESULT::LOSE' cho kết quả
        3. Tạo danh sách các transactions hoàn chỉnh
        """
        df = self.load_raw_data()
        
        transactions = []
        processed_rows = []

        for idx, row in df.iterrows():
            # 1. Parse hero_ids
            raw_heroes = row['hero_ids']
            if isinstance(raw_heroes, str):
                try:
                    hero_list = json.loads(raw_heroes)
                except Exception:
                    continue
            elif isinstance(raw_heroes, list):
                hero_list = raw_heroes
            else:
                continue

            # 2. Xử lý kết quả WIN/LOSE
            is_win = bool(row['is_winner'])
            result_tag = "RESULT::WIN" if is_win else "RESULT::LOSE"

            # 3. Định dạng item: HERO::<ID/Name>
            hero_items = [f"HERO::{hero}" for hero in hero_list]
            
            # 4. Gộp thành transaction hoàn chỉnh cho 1 đội
            full_transaction = hero_items + [result_tag]
            transactions.append(full_transaction)

            # Lưu dòng dạng chuỗi phân cách bởi dấu phẩy để ghi ra CSV
            processed_rows.append({
                'game_id': row.get('game_id', idx),
                'team_id': row.get('team_id', ''),
                'is_winner': is_win,
                'hero_count': len(hero_list),
                'items_str': ",".join(full_transaction)
            })

        # Chuyển thành DataFrame và lưu file CSV đã xử lý
        processed_df = pd.DataFrame(processed_rows)
        
        # Đảm bảo thư mục lưu tồn tại
        os.makedirs(os.path.dirname(self.processed_data_path), exist_ok=True)
        processed_df.to_csv(self.processed_data_path, index=False, encoding='utf-8')
        
        print(f"✅ Tiền xử lý thành công {len(transactions)} transactions!")
        print(f"📁 Dữ liệu đã lưu tại: {self.processed_data_path}")
        
        return transactions, processed_df

if __name__ == '__main__':
    preprocessor = DataPreprocessor()
    txs, df_proc = preprocessor.process_transactions()
    
    print("\n📝 Mẫu 3 Transactions đầu tiên sau tiền xử lý:")
    for i, t in enumerate(txs[:3], 1):
        print(f"Transaction {i}: {t}")
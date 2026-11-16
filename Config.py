import os

# Đường dẫn thư mục gốc của project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Đường dẫn tới các thư mục dữ liệu
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# Tự động tạo thư mục nếu chưa có
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class Config:
    SECRET_KEY = 'lienquan-analytics-secret-key'
    RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, 'association_train.csv')
    PROCESSED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, 'processed_transactions.csv')
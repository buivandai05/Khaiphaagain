# AoG Analytics

> Ứng dụng phân tích dữ liệu đội hình Honor of Kings (Arena of Glory) bằng khai phá tập phổ biến và luật kết hợp.

AoG Analytics đọc dữ liệu đội hình và kết quả trận đấu, chuyển mỗi đội thành một transaction, sau đó dùng **Apriori** và **FP-Growth** để tìm các tập tướng thường xuất hiện cùng nhau và các mối liên hệ thống kê giữa đội hình với kết quả thắng/thua. Ứng dụng cung cấp giao diện web bằng Flask để xem dữ liệu, chạy thuật toán, so sánh kết quả và tải báo cáo CSV.

> Các luật và chỉ số mô tả dữ liệu quan sát được; chúng không chứng minh một đội hình là nguyên nhân trực tiếp tạo ra chiến thắng.

## Mục lục

- [Chức năng](#chức-năng)
- [Công nghệ](#công-nghệ)
- [Cài đặt và chạy](#cài-đặt-và-chạy)
- [Dữ liệu đầu vào](#dữ-liệu-đầu-vào)
- [Quy trình xử lý](#quy-trình-xử-lý)
- [Các chỉ số](#các-chỉ-số)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [API](#api)
- [Lưu ý](#lưu-ý)

## Chức năng

- **Dashboard:** thống kê số trận, số transaction đội, số tướng và kết quả thắng/thua.
- **Data Management:** xem các tệp dữ liệu, số dòng/cột và trạng thái kiểm tra schema.
- **Preprocessing:** xem các transaction sau tiền xử lý và cách UUID được ánh xạ thành tên tướng.
- **Apriori và FP-Growth:** khai thác frequent itemsets và association rules theo các ngưỡng do người dùng chọn.
- **Association Rules:** tổng hợp luật giữa combo từ 2 đến 5 tướng và kết quả Thắng/Thua; có tìm kiếm, lọc, sắp xếp và phân trang.
- **Comparison:** chạy hai thuật toán trên cùng dữ liệu và bộ tham số để so sánh kết quả.
- **Team compositions:** xem thống kê đội hình đã xuất hiện, lọc theo tướng/kích thước và ngưỡng số trận.
- **Reports:** tải báo cáo itemsets, rules và bảng so sánh ở định dạng CSV UTF-8-SIG.

## Công nghệ

- Python, Flask
- pandas, NumPy
- mlxtend (Apriori, FP-Growth và association rules)
- Bootstrap, Chart.js và JavaScript phía trình duyệt

## Cài đặt và chạy

### Yêu cầu

- Python 3.10 trở lên
- pip

### Thiết lập môi trường

Mở terminal tại thư mục `lienquan_rules`:

```bash
python -m venv .venv
```

Kích hoạt môi trường ảo:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Cài các thư viện:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Khởi động ứng dụng

```bash
python app.py
```

Mở <http://127.0.0.1:5000> trong trình duyệt. Chế độ hiện tại chạy Flask với `debug=True`, phù hợp cho phát triển cục bộ; không dùng cấu hình này làm máy chủ production.

## Dữ liệu đầu vào

Ứng dụng khai phá association rules lấy dữ liệu từ:

- `data/raw/association_train.csv` — dữ liệu huấn luyện, mỗi dòng đại diện cho một đội trong một trận.
- `data/raw/heroes.csv` — ánh xạ `hero_id` sang tên để hiển thị. Việc khai phá vẫn sử dụng UUID gốc.

`association_train.csv` cần có các cột:

| Cột | Ý nghĩa | Yêu cầu |
| --- | --- | --- |
| `game_id` | Mã trận | Mỗi trận có đúng hai dòng, tương ứng hai đội |
| `team_id` | Mã đội | Hai đội trong cùng trận phải khác nhau |
| `hero_ids` | Danh sách ID tướng | Chuỗi JSON gồm đúng 5 UUID khác nhau |
| `is_winner` | Đội có thắng trận không | Nhận `true`/`false`, `1`/`0`, `win`/`lose` hoặc các giá trị tương đương được bộ tiền xử lý hỗ trợ |

`heroes.csv` cần có `hero_id` và `name`. Nếu một ID chưa có trong tệp ánh xạ, giao diện sẽ hiển thị ID đó thay cho tên tướng.

Ví dụ một dòng dữ liệu:

```csv
game_id,team_id,hero_ids,is_winner
game-001,team-a,"[""hero-uuid-1"",""hero-uuid-2"",""hero-uuid-3"",""hero-uuid-4"",""hero-uuid-5""]",true
```

Khi đọc dữ liệu, ứng dụng kiểm tra mỗi trận có đúng hai đội và đúng một đội thắng. Transaction đã tiền xử lý được ghi vào `data/processed/processed_transactions.csv`.

## Quy trình xử lý

1. Đọc từng dòng từ `association_train.csv`.
2. Phân tích danh sách `hero_ids` dạng JSON và giữ nguyên UUID.
3. Tạo transaction gồm năm item `HERO::<uuid>` và một item kết quả `RESULT::WIN` hoặc `RESULT::LOSE`.
4. Chạy Apriori hoặc FP-Growth trên cùng tập transaction.
5. Tạo luật kết hợp và lọc theo Support, Confidence, Lift. Trang Association Rules chỉ hiển thị luật có từ 2 đến 5 tướng ở vế trước và kết quả Thắng/Thua ở vế sau.

Ví dụ cấu trúc transaction:

```text
HERO::id_A, HERO::id_B, HERO::id_C, HERO::id_D, HERO::id_E, RESULT::WIN
```

Một luật `Tướng A + Tướng B → Kết quả: Thắng` diễn tả mối liên hệ thống kê trong dữ liệu giữa việc một đội sử dụng hai tướng đó và kết quả thắng.

## Các chỉ số

- **Support:** tỷ lệ transaction có chứa đồng thời các item của luật. Mẫu số là số transaction đội, không phải số trận.
- **Confidence:** trong các transaction chứa vế trước, tỷ lệ cũng chứa vế sau.
- **Lift:** Confidence chia cho Support của vế sau. Lift lớn hơn 1 biểu thị kết quả xuất hiện cùng vế trước nhiều hơn mức nền trong dữ liệu.
- **Minimum Support / Confidence / Lift:** ngưỡng lọc luật; ngưỡng được cấu hình mặc định trong `Config.py` và có thể thay đổi trên giao diện.

Apriori và FP-Growth có thể trả về cùng một luật; trang tổng hợp liệt kê kết quả của từng thuật toán riêng, vì vậy một luật có thể xuất hiện hai lần.

## Cấu trúc dự án

```text
lienquan_rules/
├── app.py                         # Tạo Flask app và đăng ký routes
├── Config.py                      # Đường dẫn dữ liệu và ngưỡng mặc định
├── requirements.txt               # Thư viện Python
├── routes/
│   └── main_routes.py             # Trang web và API
├── services/
│   ├── mining_service.py          # Điều phối tiền xử lý, khai phá và báo cáo
│   └── hero_mapping_service.py    # Ánh xạ UUID tướng sang tên
├── src/
│   ├── data/
│   │   └── preprocessing.py       # Kiểm tra và tạo transactions
│   └── mining/
│       ├── apriori_miner.py       # Khai phá Apriori
│       ├── fpgrowth_miner.py      # Khai phá FP-Growth
│       └── comparison.py          # So sánh hai thuật toán
├── templates/                     # Giao diện Jinja2
├── static/                        # CSS và JavaScript
├── data/
│   ├── raw/                       # CSV đầu vào
│   └── processed/                 # CSV sau tiền xử lý
└── tests/                         # Các kiểm thử hiện có
```

## API

Các endpoint JSON chính:

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| `GET` | `/api/stats` | Thống kê tổng quan |
| `GET` | `/api/preprocessing` | Xem transaction đã xử lý, hỗ trợ `page` và `per_page` |
| `GET` | `/api/data-management` | Trạng thái các tệp dữ liệu |
| `POST` | `/api/mining/<algorithm>` | Chạy `apriori` hoặc `fpgrowth` |
| `POST` | `/api/compare` | So sánh Apriori và FP-Growth |
| `POST` | `/api/association-rules` | Tổng hợp luật cho trang Association Rules |
| `GET` | `/api/team-compositions` | Thống kê các tổ hợp tướng |
| `GET` | `/api/reports/<report_type>.csv` | Tải báo cáo đã được tạo từ lần chạy tương ứng |

Các endpoint nhận tham số khai phá qua JSON gồm `min_support`, `min_confidence`, `min_lift`; trang khai phá đơn lẻ và so sánh cũng hỗ trợ `max_heroes` từ 2 đến 5. Tải báo cáo yêu cầu đã chạy thuật toán với đúng bộ tham số trước đó trong cùng phiên chạy ứng dụng.

## Lưu ý

- Nên kiểm tra tính đại diện, chất lượng và nguồn gốc dữ liệu trước khi diễn giải kết quả.
- Support thấp có thể tạo ra luật ít quan sát; Confidence cao không đồng nghĩa với quan hệ nhân quả.
- Thời gian và số luật có thể thay đổi theo dữ liệu cũng như ngưỡng khai phá.
- Các tệp `train.csv`, `test.csv`, `validation.csv`, `games.csv`, `hero_statistics.csv` và `association_transactions.csv` có trong `data/raw`; luồng khai phá đang cấu hình trực tiếp `association_train.csv` và `heroes.csv`.
- Các thư viện Bootstrap, Font Awesome và Chart.js được tải từ CDN khi mở giao diện.

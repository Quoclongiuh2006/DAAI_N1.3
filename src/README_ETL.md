# 📊 ETL Pipeline: Bronze → Silver Layer

## 🎯 Tổng quan

Pipeline xử lý dữ liệu thương mại điện tử từ tầng **Bronze** (raw data) lên tầng **Silver** (cleaned & standardized data) sử dụng Python và Pandas.

---

## 📁 Cấu trúc thư mục

```
DAAI_N1.3/
├── data/                  # 🥉 Bronze Layer (Dữ liệu thô)
│   ├── products.csv
│   ├── inventory.csv
│   └── promotions.csv
│
├── data_silver/          # 🥈 Silver Layer (Dữ liệu đã xử lý)
│   ├── product.csv
│   ├── inventory.csv
│   └── promotions.csv
│
└── src/                  # 💻 Source Code
    ├── process_products.py
    ├── process_inventory.py
    ├── process_promotions.py
    └── README_ETL.md (file này)
```

---

## 🚀 Cách chạy

### Yêu cầu:
```bash
pip install pandas
```

### Chạy từng module:
```bash
cd d:\IUH\2025-2026\DAAI\DAAI_N1.3

# Xử lý Products (chạy đầu tiên)
python src/process_products.py

# Xử lý Inventory (chạy sau Products)
python src/process_inventory.py

# Xử lý Promotions
python src/process_promotions.py
```

**Lưu ý:** Chạy `process_products.py` trước `process_inventory.py` để đảm bảo kiểm tra referential integrity.

---

## 📋 Xử lý chi tiết

### 1️⃣ **Products** → `product.csv`

**Input:** `data/products.csv` (2,412 records)  
**Output:** `data_silver/product.csv` (10 cột)

**Xử lý:**
- Làm tròn `price` và `cogs` → 2 chữ số thập phân
- Tính `gross_profit = price - cogs`
- Tính `margin_rate = (price - cogs) / price` (4 chữ số)
- Chuẩn hóa text:
  - `category`, `segment`: Title Case
  - `size`: UPPER
  - `color`: lower

**Data Quality:** 6 assertions (khóa chính, độ chính xác, business logic)

---

### 2️⃣ **Inventory** → `inventory.csv`

**Input:** `data/inventory.csv` (60,247 records)  
**Output:** `data_silver/inventory.csv` (17 cột)

**Xử lý:**
- Ép kiểu `snapshot_date` → datetime
- Tái lập `reorder_flag`:
  ```
  reorder_flag = 1 nếu (stockout_days > 0) HOẶC (days_of_supply < 15)
  ```
- Làm tròn `sell_through_rate` → 4 chữ số

**Data Quality:** 7 assertions (khóa chính, datetime, **referential integrity** với Products)

---

### 3️⃣ **Promotions** → `promotions.csv`

**Input:** `data/promotions.csv` (50 records)  
**Output:** `data_silver/promotions.csv` (11 cột)

**Xử lý:**
- Điền `applicable_category` null → `'All'`
- Ép kiểu `start_date`, `end_date` → datetime
- Tính `campaign_duration_days = end_date - start_date`
- Chuẩn hóa `promo_type`, `promo_channel` → lowercase

**Data Quality:** 8 assertions (khóa chính, datetime, business logic)

---

## 🔍 Data Quality Checks

Tổng cộng **21 assertions** tự động:

| Loại | Kiểm tra |
|------|----------|
| **Primary Key** | Không null, không trùng lặp |
| **Data Type** | Datetime, numeric đúng định dạng |
| **Referential Integrity** | `product_id` trong Inventory có trong Products |
| **Business Logic** | price ≥ cogs, end_date ≥ start_date |
| **Completeness** | Cột bắt buộc không null |

Pipeline dừng ngay khi phát hiện lỗi với message chi tiết.

---

## 📊 Kết quả mẫu

### Products (Before → After):
```csv
# Before (Bronze)
product_id,price,cogs,category,size,color
536,11059.6543278,9704.84287532,streetwear,s,GREEN

# After (Silver)
product_id,price,cogs,gross_profit,margin_rate,category,size,color
536,11059.65,9704.84,1354.81,0.1225,Streetwear,S,green
```

### Inventory (Highlight):
- `snapshot_date`: string → **datetime**
- `reorder_flag`: Tái lập → **+40,571 sản phẩm cần reorder**

### Promotions (Highlight):
- `applicable_category`: 40 null → **'All'**
- `campaign_duration_days`: Tính toán mới (trung bình **33.5 ngày**)

---

## 💡 Lưu ý

1. **Thứ tự chạy:** Products → Inventory → Promotions
2. **Dependencies:** `pip install pandas`
3. **Lỗi:** Đọc assertion message để biết nguyên nhân

---

## 📞 Liên hệ

**Nhóm DAAI_N1.3**  
- 24701081 - Trần Quốc Long
- 24726501 - Nguyễn Trọng Hiếu
- 24683221 - Lê Gia Bảo
- 24668051 - Nguyễn Ngọc Thùy Dương

---

**IUH University - 2026**

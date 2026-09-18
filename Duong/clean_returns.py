# -*- coding: utf-8 -*-
"""
clean_returns.py
Làm sạch dữ liệu RETURNS (yêu cầu đổi trả hàng)
Nguồn: returns.csv -> Đích: returns.csv

Nguyên tắc áp dụng :
  - KHÔNG xóa dữ liệu vì lỗi/bất thường -> chỉ ĐÁNH DẤU (flag)
  - CHỈ xóa dòng khi: (a) rỗng hoàn toàn, hoặc (b) thiếu khóa bắt buộc (return_id, order_id, product_id)
  - Thiếu dữ liệu SỐ -> điền median
  - Thiếu return_reason -> điền 'Unknown' (không xóa, không tự suy diễn lý do cụ thể)
  - Đối chiếu khóa ngoại chéo với orders_enriched.csv, products.csv (nếu có file)
"""

import pandas as pd

print("=" * 60)
print("LÀM SẠCH returns.csv")
print("=" * 60)

df = pd.read_csv("returns.csv")
df.info()
print(df.isna().sum())

# --- Xóa dòng rỗng hoàn toàn ---
n_before = len(df)
df = df.dropna(how="all")
print(f"Dòng rỗng hoàn toàn (đã xóa): {n_before - len(df)}")

# --- Xóa dòng trùng lặp toàn bộ ---
n_before = len(df)
df = df.drop_duplicates()
print(f"Dòng trùng lặp toàn bộ (đã xóa): {n_before - len(df)}")

# --- return_id, order_id, product_id là khóa bắt buộc -> thiếu thì phải bỏ ---
n_before = len(df)
df = df.dropna(subset=["return_id", "order_id", "product_id"])
print(f"Dòng bị xóa do thiếu return_id/order_id/product_id: {n_before - len(df)}")

df = df.reset_index(drop=True)

# --- Ép order_id, product_id về kiểu số nguyên (đã đảm bảo không còn NaN sau dropna ở trên) ---
df["order_id"] = df["order_id"].astype("int64")
df["product_id"] = df["product_id"].astype("int64")

# --- return_date: không bịa ngày, chỉ chuẩn hóa kiểu và ghi nhận thiếu ---
df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")
n_missing_date = df["return_date"].isna().sum()
if n_missing_date > 0:
    print(f"return_date thiếu {n_missing_date} giá trị -> giữ NaT")

# --- return_quantity, refund_amount: điền median ---
for col in ["return_quantity", "refund_amount"]:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"{col} thiếu {n_missing} giá trị -> đã lấp bằng median ({median_val:.2f})")

# return_quantity là dữ liệu đếm -> làm tròn về số nguyên (median có thể ra số lẻ)
df["return_quantity"] = df["return_quantity"].round().astype("Int64")

# --- return_reason: thiếu -> điền 'Unknown' (không xóa, không tự suy diễn lý do cụ thể) ---
n_missing_reason = df["return_reason"].isna().sum()
if n_missing_reason > 0:
    df["return_reason"] = df["return_reason"].fillna("Unknown")
    print(f"return_reason thiếu {n_missing_reason} giá trị -> đã điền 'Unknown'")

# --- Đánh dấu (KHÔNG XÓA) giá trị bất thường ---
df["flag_quantity_bat_thuong"] = df["return_quantity"] <= 0
df["flag_refund_am_bat_thuong"] = df["refund_amount"] < 0

for flag_col in ["flag_quantity_bat_thuong", "flag_refund_am_bat_thuong"]:
    n_flag = df[flag_col].sum()
    if n_flag > 0:
        print(f"{flag_col}: {n_flag} dòng được đánh dấu bất thường (KHÔNG xóa)")

# --- Đối chiếu chéo với orders_enriched và products (nếu có file) ---
try:
    df_orders_ref = pd.read_csv("orders_enriched.csv")
    n_orphan_order = (~df["order_id"].isin(df_orders_ref["order_id"])).sum()
    print(f"order_id không tồn tại trong orders_enriched: {n_orphan_order}")
except FileNotFoundError:
    print("Không tìm thấy orders_enriched.csv, bỏ qua đối chiếu order_id")

try:
    df_products_ref = pd.read_csv("products.csv")
    n_orphan_product = (~df["product_id"].isin(df_products_ref["product_id"])).sum()
    print(f"product_id không tồn tại trong products: {n_orphan_product}")
except FileNotFoundError:
    print("Không tìm thấy products.csv, bỏ qua đối chiếu product_id")

# --- Kiểm tra cuối ---
print("=" * 50)
print("KIỂM TRA CUỐI CÙNG - RETURNS")
print("=" * 50)
print(df.isna().sum())
print(f"Tổng số dòng: {len(df)}")

# --- Xuất file CSV ---
df.to_csv("returns.csv", index=False)
print("\nĐã xuất: returns.csv")

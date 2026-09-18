# -*- coding: utf-8 -*-
"""
clean_shipments.py
Làm sạch dữ liệu SHIPMENTS (giao dịch vận chuyển từng đơn hàng)
Nguồn: shipments_realistic.csv -> Đích: shipments.csv

Nguyên tắc áp dụng:
  - KHÔNG xóa dữ liệu vì lỗi/bất thường -> chỉ ĐÁNH DẤU (flag)
  - CHỈ xóa dòng khi: (a) rỗng hoàn toàn, hoặc (b) thiếu khóa bắt buộc (order_id, shipper_id)
  - Thiếu dữ liệu SỐ -> điền median
  - Đối chiếu khóa ngoại chéo với orders_enriched.csv (nếu có file)
"""

import pandas as pd

print("=" * 60)
print("LÀM SẠCH shipments_realistic.csv -> shipments.csv")
print("=" * 60)

df = pd.read_csv("shipments_realistic.csv")
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

# --- order_id, shipper_id là khóa bắt buộc (PK/FK) -> thiếu thì phải bỏ ---
n_before = len(df)
df = df.dropna(subset=["order_id", "shipper_id"])
print(f"Dòng bị xóa do thiếu order_id/shipper_id: {n_before - len(df)}")

df = df.reset_index(drop=True)

# --- Ép order_id về kiểu số nguyên (đã đảm bảo không còn NaN sau dropna ở trên) ---
# Tránh lỗi ".0" dư thừa (vd 1001.0 thay vì 1001) và lệch kiểu dữ liệu khi JOIN với bảng khác
df["order_id"] = df["order_id"].astype("int64")

# --- Chuẩn hóa kiểu ngày (KHÔNG bịa ngày nếu thiếu) ---
for col in ["ship_date", "delivery_date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        print(f"{col}: thiếu {n_missing} giá trị -> giữ NaT (không bịa ngày)")

# --- Điền dữ liệu thiếu cho các cột SỐ bằng median ---
numeric_cols = ["shipping_fee", "delivery_success_rate", "average_delivery_time"]
for col in numeric_cols:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"{col} thiếu {n_missing} giá trị -> đã lấp bằng median ({median_val:.2f})")

# --- Đánh dấu (KHÔNG XÓA) các giá trị số bất thường ---
df["flag_shipping_fee_bat_thuong"] = df["shipping_fee"] <= 0
df["flag_success_rate_bat_thuong"] = ~df["delivery_success_rate"].between(0, 100)
df["flag_delivery_time_bat_thuong"] = df["average_delivery_time"] <= 0

for flag_col in [c for c in df.columns if c.startswith("flag_")]:
    n_flag = df[flag_col].sum()
    if n_flag > 0:
        print(f"{flag_col}: {n_flag} dòng được đánh dấu bất thường (KHÔNG xóa)")

# --- Đối chiếu chéo order_id với orders_enriched (nếu có file) ---
try:
    df_orders_ref = pd.read_csv("orders_enriched.csv")
    n_orphan = (~df["order_id"].isin(df_orders_ref["order_id"])).sum()
    print(f"order_id không tồn tại trong orders_enriched: {n_orphan}")
except FileNotFoundError:
    print("Không tìm thấy orders_enriched.csv, bỏ qua đối chiếu order_id")

# ------------------------------------------------------------
# TÁCH BẢNG: chỉ giữ lại các cột giao dịch (không lặp lại thông tin tĩnh của shipper)
# ------------------------------------------------------------
shipment_cols = ["order_id", "shipper_id", "ship_date", "delivery_date", "shipping_fee",
                  "delivery_success_rate", "average_delivery_time",
                  "flag_shipping_fee_bat_thuong", "flag_success_rate_bat_thuong",
                  "flag_delivery_time_bat_thuong"]
df_shipments = df[shipment_cols].reset_index(drop=True)

print("=" * 50)
print("KIỂM TRA CUỐI CÙNG - SHIPMENTS")
print("=" * 50)
print(df_shipments.isna().sum())
print(f"Tổng số dòng shipments (giao dịch): {len(df_shipments)}")

# --- Xuất file CSV ---
df_shipments.to_csv("shipments.csv", index=False)
print("\nĐã xuất: shipments.csv")

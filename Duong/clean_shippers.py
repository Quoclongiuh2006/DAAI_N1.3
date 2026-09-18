# -*- coding: utf-8 -*-
"""
clean_shippers.py
Làm sạch dữ liệu SHIPPER (thông tin tĩnh của người giao hàng)
Nguồn: shipments_realistic.csv -> Đích: shippers.csv

Nguyên tắc áp dụng :
  - KHÔNG xóa dữ liệu vì lỗi/bất thường -> chỉ ĐÁNH DẤU (flag)
  - CHỈ xóa dòng khi: (a) rỗng hoàn toàn, hoặc (b) thiếu khóa bắt buộc (order_id, shipper_id)
  - Thiếu dữ liệu SỐ -> điền median
  - Thiếu dữ liệu CHỮ -> tùy vai trò cột (định danh cá nhân giữ NaN, vận hành điền mode)

Giả định: mỗi shipper_id có thông tin cá nhân/vận hành ổn định, không đổi theo từng đơn.
NẾU giả định này sai với dữ liệu thật của nhóm, cần điều chỉnh lại danh sách shipper_cols bên dưới.
"""

import pandas as pd

print("=" * 60)
print("LÀM SẠCH shipments_realistic.csv -> shippers.csv")
print("=" * 60)

# Ép shipper_phone đọc dạng chuỗi ngay từ đầu, tránh pandas tự suy luận
# nhầm sang kiểu số (làm mất số 0 ở đầu SĐT, vd "0900..." -> 900...0)
df = pd.read_csv("shipments_realistic.csv", dtype={"shipper_phone": str})
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

# --- Chuẩn hóa kiểu ngày (KHÔNG bịa ngày nếu thiếu) ---
df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
n_missing = df["join_date"].isna().sum()
if n_missing > 0:
    print(f"join_date: thiếu {n_missing} giá trị -> giữ NaT (không bịa ngày)")

# --- Điền dữ liệu thiếu cho cột SỐ bằng median; riêng cột đếm (tuổi, số năm KN) làm tròn về nguyên ---
numeric_cols = ["shipper_experience_years", "shipper_rating", "shipper_age"]
integer_count_cols = {"shipper_experience_years", "shipper_age"}
for col in numeric_cols:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        median_val = df[col].median()
        df[col] = df[col].fillna(median_val)
        print(f"{col} thiếu {n_missing} giá trị -> đã lấp bằng median ({median_val:.2f})")
    if col in integer_count_cols:
        df[col] = df[col].round().astype("Int64")

# --- Đánh dấu (KHÔNG XÓA) giá trị số bất thường ---
df["flag_rating_bat_thuong"] = ~df["shipper_rating"].between(0, 5)
df["flag_age_bat_thuong"] = ~df["shipper_age"].between(16, 80)
for flag_col in ["flag_rating_bat_thuong", "flag_age_bat_thuong"]:
    n_flag = df[flag_col].sum()
    if n_flag > 0:
        print(f"{flag_col}: {n_flag} dòng được đánh dấu bất thường (KHÔNG xóa)")

# --- Cột định danh cá nhân: KHÔNG bịa dữ liệu, chỉ giữ NaN và ghi nhận ---
identity_cols = ["shipper_name", "shipper_phone"]
for col in identity_cols:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        print(f"{col} thiếu {n_missing} giá trị -> giữ nguyên NaN (không bịa thông tin cá nhân)")

# --- Cột phân loại vận hành: điền bằng mode (giá trị phổ biến nhất) ---
operational_cat_cols = ["shipper_gender", "shipper_marital_status", "shipper_education",
                         "shipper_vehicle", "shipper_company", "working_shift",
                         "city", "region", "district"]
for col in operational_cat_cols:
    n_missing = df[col].isna().sum()
    if n_missing > 0:
        mode_series = df[col].mode(dropna=True)
        if len(mode_series) > 0:
            df[col] = df[col].fillna(mode_series.iloc[0])
            print(f"{col} thiếu {n_missing} giá trị -> đã lấp bằng mode ('{mode_series.iloc[0]}')")

# ------------------------------------------------------------
# TÁCH BẢNG: giữ lại thông tin tĩnh của shipper, mỗi shipper_id 1 dòng duy nhất
# ------------------------------------------------------------
shipper_cols = ["shipper_id", "shipper_name", "shipper_phone", "shipper_gender",
                 "shipper_age", "shipper_marital_status", "shipper_education",
                 "shipper_company", "shipper_vehicle", "shipper_experience_years",
                 "shipper_rating", "join_date", "working_shift",
                 "city", "region", "district"]

df_shippers = df[shipper_cols].drop_duplicates(subset=["shipper_id"]).reset_index(drop=True)

# Cảnh báo nếu 1 shipper_id có nhiều dòng dữ liệu KHÔNG khớp nhau (dữ liệu không nhất quán)
check_cols = [c for c in shipper_cols if c != "shipper_id"]
n_inconsistent = df.groupby("shipper_id")[check_cols].nunique().gt(1).any(axis=1).sum()
if n_inconsistent > 0:
    print(f"CẢNH BÁO: {n_inconsistent} shipper_id có thông tin KHÔNG nhất quán giữa các dòng "
          f"(đã lấy giá trị xuất hiện đầu tiên khi tách bảng)")

print("=" * 50)
print("KIỂM TRA CUỐI CÙNG - SHIPPERS")
print("=" * 50)
print(df_shippers.isna().sum())
print(f"Tổng số shipper duy nhất: {len(df_shippers)}")

# --- Xuất file CSV ---
df_shippers.to_csv("shippers.csv", index=False)
print("\nĐã xuất: shippers.csv")

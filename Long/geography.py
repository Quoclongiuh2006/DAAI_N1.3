import pandas as pd
import numpy as np

# ============================================================
# 1. ĐỌC DỮ LIỆU
# ============================================================
df_geography = pd.read_csv("geography.csv")

print("Kích thước ban đầu:", df_geography.shape)
print("\nSố lượng giá trị null:")
print(df_geography.isnull().sum())


# ============================================================
# 2. XÓA DÒNG NULL HOÀN TOÀN
# ============================================================
before = len(df_geography)

df_geography = df_geography.dropna(how="all").copy()

print("\nSố dòng null hoàn toàn đã xóa:",
      before - len(df_geography))


# ============================================================
# 3. LÀM SẠCH TEXT
# ============================================================
text_columns = [
    "city",
    "region",
    "district"
]

for col in text_columns:
    df_geography[col] = (
        df_geography[col]
        .astype("string")
        .str.strip()
    )


# ============================================================
# 4. CHUẨN HÓA ZIP
# ============================================================
df_geography["zip"] = pd.to_numeric(
    df_geography["zip"],
    errors="coerce"
)

# Giữ ZIP dưới dạng chuỗi 5 ký tự
df_geography["zip"] = (
    df_geography["zip"]
    .astype("Int64")
    .astype("string")
    .str.zfill(5)
)


# ============================================================
# 5. CHUẨN HÓA REGION
# ============================================================
valid_regions = [
    "East",
    "Central",
    "West"
]

invalid_region = ~df_geography["region"].isin(
    valid_regions
) & df_geography["region"].notna()

print("Region không hợp lệ:",
      invalid_region.sum())

region_mode = df_geography.loc[
    df_geography["region"].isin(valid_regions),
    "region"
].mode()

if len(region_mode) > 0:
    df_geography.loc[
        invalid_region,
        "region"
    ] = region_mode.iloc[0]

    df_geography["region"] = (
        df_geography["region"]
        .fillna(region_mode.iloc[0])
    )


# ============================================================
# 6. XỬ LÝ CITY VÀ DISTRICT BỊ THIẾU
# ============================================================
for col in ["city", "district"]:

    mode_value = df_geography[col].mode()

    if len(mode_value) > 0:
        df_geography[col] = df_geography[col].fillna(
            mode_value.iloc[0]
        )


# ============================================================
# 7. KIỂM TRA ZIP BỊ THIẾU
# ============================================================
missing_zip = df_geography["zip"].isna().sum()

print("ZIP bị thiếu:", missing_zip)

# Không xóa dòng.
# Nếu ZIP thiếu nhưng có thể suy ra từ CITY thì có thể bổ sung
# bằng ZIP phổ biến nhất của CITY.

if missing_zip > 0:

    zip_by_city = (
        df_geography.dropna(subset=["zip"])
        .groupby("city")["zip"]
        .agg(lambda x: x.mode().iloc[0]
             if len(x.mode()) > 0 else pd.NA)
    )

    mask = df_geography["zip"].isna()

    df_geography.loc[mask, "zip"] = (
        df_geography.loc[mask, "city"]
        .map(zip_by_city)
    )

    # Nếu vẫn thiếu thì giữ lại,
    # không tự tạo ZIP không có căn cứ.


# ============================================================
# 8. KIỂM TRA CUỐI
# ============================================================
print("\n===== KIỂM TRA GEOGRAPHY SAU KHI LÀM SẠCH =====")
print("Kích thước:", df_geography.shape)

print("\nNull:")
print(df_geography.isnull().sum())

print("\nDuplicate:", df_geography.duplicated().sum())
print("Duplicate ZIP:",
      df_geography["zip"].duplicated().sum())


# ============================================================
# 9. XUẤT FILE CSV
# ============================================================
df_geography.to_csv(
    "geography_silver.csv",
    index=False
)

print("\nĐã xuất: geography_silver.csv")
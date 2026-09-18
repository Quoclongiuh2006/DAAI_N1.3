import pandas as pd
import numpy as np

# ============================================================
# 1. ĐỌC DỮ LIỆU
# ============================================================
df_reviews = pd.read_csv("reviews.csv")

print("Kích thước ban đầu:", df_reviews.shape)
print("\nSố lượng giá trị null:")
print(df_reviews.isnull().sum())


# ============================================================
# 2. XÓA DÒNG NULL HOÀN TOÀN
# ============================================================
before = len(df_reviews)

df_reviews = df_reviews.dropna(how="all").copy()

print("\nSố dòng null hoàn toàn đã xóa:",
      before - len(df_reviews))


# ============================================================
# 3. LÀM SẠCH TEXT
# ============================================================
df_reviews["review_id"] = (
    df_reviews["review_id"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df_reviews["review_title"] = (
    df_reviews["review_title"]
    .astype("string")
    .str.strip()
)


# ============================================================
# 4. CHUẨN HÓA ID
# ============================================================
for col in [
    "order_id",
    "product_id",
    "customer_id"
]:
    df_reviews[col] = pd.to_numeric(
        df_reviews[col],
        errors="coerce"
    )


# ============================================================
# 5. KIỂM TRA REVIEW_ID
# ============================================================
valid_review_id = df_reviews["review_id"].str.match(
    r"^REV-\d{7}$",
    na=False
)

invalid_review_id = (
    ~valid_review_id &
    df_reviews["review_id"].notna()
)

print("\nReview ID không đúng định dạng:",
      invalid_review_id.sum())

# Không xóa review.
# Nếu ID sai định dạng thì giữ lại để tránh mất dữ liệu.
# Chỉ chuẩn hóa khoảng trắng/chữ hoa.


# ============================================================
# 6. CHUẨN HÓA REVIEW_DATE
# ============================================================
df_reviews["review_date"] = pd.to_datetime(
    df_reviews["review_date"],
    errors="coerce"
)

valid_dates = df_reviews["review_date"].dropna()

if len(valid_dates) > 0:

    median_date = (
        valid_dates
        .sort_values()
        .iloc[len(valid_dates) // 2]
    )

    df_reviews["review_date"] = (
        df_reviews["review_date"]
        .fillna(median_date)
    )


# ============================================================
# 7. CHUẨN HÓA RATING
# ============================================================
df_reviews["rating"] = pd.to_numeric(
    df_reviews["rating"],
    errors="coerce"
)

invalid_rating = (
    (df_reviews["rating"] < 1) |
    (df_reviews["rating"] > 5)
) & df_reviews["rating"].notna()

print("Rating không hợp lệ:",
      invalid_rating.sum())

# Không xóa rating lỗi.
# Thay bằng median rating hợp lệ.

valid_rating = df_reviews.loc[
    ~invalid_rating,
    "rating"
].dropna()

if len(valid_rating) > 0:

    rating_median = valid_rating.median()

    df_reviews.loc[
        invalid_rating,
        "rating"
    ] = rating_median

    df_reviews["rating"] = (
        df_reviews["rating"]
        .fillna(rating_median)
    )


# ============================================================
# 8. XỬ LÝ REVIEW_TITLE
# ============================================================
title_mode = df_reviews["review_title"].mode()

if len(title_mode) > 0:

    df_reviews["review_title"] = (
        df_reviews["review_title"]
        .fillna(title_mode.iloc[0])
    )


# ============================================================
# 9. KIỂM TRA CUỐI
# ============================================================
print("\n===== KIỂM TRA REVIEWS SAU KHI LÀM SẠCH =====")
print("Kích thước:", df_reviews.shape)

print("\nNull:")
print(df_reviews.isnull().sum())

print("\nDuplicate:", df_reviews.duplicated().sum())

print(
    "Duplicate review_id:",
    df_reviews["review_id"].duplicated().sum()
)

print(
    "\nKhoảng rating:",
    df_reviews["rating"].min(),
    "->",
    df_reviews["rating"].max()
)


# ============================================================
# 10. XUẤT FILE CSV
# ============================================================
df_reviews.to_csv(
    "reviews_silver.csv",
    index=False
)

print("\nĐã xuất: reviews_silver.csv")
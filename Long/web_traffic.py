
import pandas as pd
import numpy as np


# ============================================================
# 1. ĐỌC DỮ LIỆU GỐC
# ============================================================

df_web = pd.read_csv("web_traffic.csv")

print("\n===== DỮ LIỆU BAN ĐẦU =====")
print("Kích thước:", df_web.shape)

print("\nThông tin dữ liệu:")
df_web.info()

print("\nSố lượng giá trị null:")
print(df_web.isnull().sum())


# ============================================================
# 2. XÓA DÒNG NULL HOÀN TOÀN
# ============================================================

before = len(df_web)

df_web = df_web.dropna(how="all").copy()

removed_rows = before - len(df_web)

print("\nSố dòng null hoàn toàn đã xóa:", removed_rows)


# ============================================================
# 3. LÀM SẠCH TRAFFIC_SOURCE
# ============================================================

df_web["traffic_source"] = (
    df_web["traffic_source"]
    .astype("string")
    .str.strip()
)


# ============================================================
# 4. CHUẨN HÓA DATE
# ============================================================

df_web["date"] = pd.to_datetime(
    df_web["date"],
    errors="coerce"
)

invalid_date = df_web["date"].isna().sum()

print("\nNgày không hợp lệ:", invalid_date)

if invalid_date > 0:

    valid_dates = df_web["date"].dropna()

    median_date = (
        valid_dates
        .sort_values()
        .iloc[len(valid_dates) // 2]
    )

    df_web["date"] = df_web["date"].fillna(
        median_date
    )


# ============================================================
# 5. CHUẨN HÓA KIỂU DỮ LIỆU SỐ
# ============================================================

count_columns = [
    "sessions",
    "unique_visitors",
    "page_views"
]

float_columns = [
    "bounce_rate",
    "avg_session_duration_sec"
]

for col in count_columns:

    df_web[col] = pd.to_numeric(
        df_web[col],
        errors="coerce"
    )

for col in float_columns:

    df_web[col] = pd.to_numeric(
        df_web[col],
        errors="coerce"
    )


# ============================================================
# 6. XỬ LÝ GIÁ TRỊ NULL BẰNG MEDIAN
# ============================================================

print("\n===== XỬ LÝ GIÁ TRỊ NULL =====")

for col in count_columns + float_columns:

    missing = df_web[col].isna().sum()

    print(f"{col}: {missing} giá trị null")

    if missing > 0:

        median_value = df_web[col].median()

        # Các cột đếm phải là số nguyên
        if col in count_columns:
            median_value = int(round(median_value))

        df_web[col] = df_web[col].fillna(
            median_value
        )


# ============================================================
# 7. KIỂM TRA SESSIONS
# ============================================================

invalid_sessions = (
    df_web["sessions"] <= 0
)

print(
    "\nSessions <= 0:",
    invalid_sessions.sum()
)

if invalid_sessions.sum() > 0:

    median_sessions = int(
        round(df_web["sessions"].median())
    )

    df_web.loc[
        invalid_sessions,
        "sessions"
    ] = median_sessions


# ============================================================
# 8. KIỂM TRA UNIQUE_VISITORS
# ============================================================

invalid_visitors = (
    df_web["unique_visitors"] <= 0
)

print(
    "Unique visitors <= 0:",
    invalid_visitors.sum()
)

if invalid_visitors.sum() > 0:

    median_visitors = int(
        round(df_web["unique_visitors"].median())
    )

    df_web.loc[
        invalid_visitors,
        "unique_visitors"
    ] = median_visitors


# ============================================================
# 9. KIỂM TRA PAGE_VIEWS
# ============================================================

invalid_page_views = (
    df_web["page_views"] <= 0
)

print(
    "Page views <= 0:",
    invalid_page_views.sum()
)

if invalid_page_views.sum() > 0:

    median_page_views = int(
        round(df_web["page_views"].median())
    )

    df_web.loc[
        invalid_page_views,
        "page_views"
    ] = median_page_views


# ============================================================
# 10. KIỂM TRA BOUNCE_RATE
# ============================================================

invalid_bounce = (
    (df_web["bounce_rate"] < 0) |
    (df_web["bounce_rate"] > 1)
)

print(
    "Bounce rate ngoài khoảng 0-1:",
    invalid_bounce.sum()
)

if invalid_bounce.sum() > 0:

    median_bounce = (
        df_web.loc[
            ~invalid_bounce,
            "bounce_rate"
        ].median()
    )

    df_web.loc[
        invalid_bounce,
        "bounce_rate"
    ] = median_bounce


# ============================================================
# 11. KIỂM TRA AVG_SESSION_DURATION_SEC
# ============================================================

invalid_duration = (
    df_web["avg_session_duration_sec"] <= 0
)

print(
    "Session duration <= 0:",
    invalid_duration.sum()
)

if invalid_duration.sum() > 0:

    median_duration = (
        df_web.loc[
            ~invalid_duration,
            "avg_session_duration_sec"
        ].median()
    )

    df_web.loc[
        invalid_duration,
        "avg_session_duration_sec"
    ] = median_duration


# ============================================================
# 12. CHUẨN HÓA TRAFFIC_SOURCE
# ============================================================

valid_sources = [
    "organic_search",
    "paid_search",
    "social_media",
    "email_campaign",
    "referral",
    "direct"
]

invalid_source = (
    ~df_web["traffic_source"].isin(valid_sources)
)

print(
    "Traffic source không hợp lệ:",
    invalid_source.sum()
)

valid_source_mode = df_web.loc[
    df_web["traffic_source"].isin(valid_sources),
    "traffic_source"
].mode()

if len(valid_source_mode) > 0:

    source_mode = valid_source_mode.iloc[0]

    # Thay giá trị không hợp lệ
    df_web.loc[
        invalid_source,
        "traffic_source"
    ] = source_mode

    # Điền giá trị null
    df_web["traffic_source"] = (
        df_web["traffic_source"]
        .fillna(source_mode)
    )


# ============================================================
# 13. KIỂM TRA LOGIC UNIQUE_VISITORS <= SESSIONS
# ============================================================

invalid_visitors_logic = (
    df_web["unique_visitors"] >
    df_web["sessions"]
)

print(
    "\nUnique visitors > sessions:",
    invalid_visitors_logic.sum()
)

if invalid_visitors_logic.sum() > 0:

    # Không xóa dữ liệu
    df_web.loc[
        invalid_visitors_logic,
        "unique_visitors"
    ] = df_web.loc[
        invalid_visitors_logic,
        "sessions"
    ]


# ============================================================
# 14. KIỂM TRA LOGIC PAGE_VIEWS >= SESSIONS
# ============================================================

invalid_page_logic = (
    df_web["page_views"] <
    df_web["sessions"]
)

print(
    "Page views < sessions:",
    invalid_page_logic.sum()
)

if invalid_page_logic.sum() > 0:

    # Không xóa dữ liệu
    df_web.loc[
        invalid_page_logic,
        "page_views"
    ] = df_web.loc[
        invalid_page_logic,
        "sessions"
    ]


# ============================================================
# 15. ĐẢM BẢO CÁC CỘT ĐẾM LÀ SỐ NGUYÊN
# ============================================================

for col in count_columns:

    df_web[col] = (
        df_web[col]
        .round()
        .astype("int64")
    )


# ============================================================
# 16. ĐỊNH DẠNG NGÀY
# ============================================================

df_web["date"] = (
    pd.to_datetime(df_web["date"])
    .dt.strftime("%Y-%m-%d")
)


# ============================================================
# 17. KIỂM TRA CUỐI
# ============================================================

print("\n========================================")
print(" KIỂM TRA SAU KHI LÀM SẠCH")
print("========================================")

print("\nKích thước:", df_web.shape)

print("\nKiểu dữ liệu:")
print(df_web.dtypes)

print("\nSố lượng NULL:")
print(df_web.isnull().sum())

print(
    "\nDuplicate toàn bộ:",
    df_web.duplicated().sum()
)

print(
    "Unique visitors > sessions:",
    (
        df_web["unique_visitors"] >
        df_web["sessions"]
    ).sum()
)

print(
    "Page views < sessions:",
    (
        df_web["page_views"] <
        df_web["sessions"]
    ).sum()
)

print(
    "Bounce rate ngoài 0-1:",
    (
        (df_web["bounce_rate"] < 0) |
        (df_web["bounce_rate"] > 1)
    ).sum()
)

print(
    "Sessions <= 0:",
    (df_web["sessions"] <= 0).sum()
)

print(
    "Unique visitors <= 0:",
    (df_web["unique_visitors"] <= 0).sum()
)

print(
    "Page views <= 0:",
    (df_web["page_views"] <= 0).sum()
)

print(
    "Session duration <= 0:",
    (df_web["avg_session_duration_sec"] <= 0).sum()
)


# ============================================================
# 18. XUẤT FILE SILVER
# ============================================================

df_web.to_csv(
    "web_traffic_silver.csv",
    index=False
)

print("\n========================================")
print("ĐÃ LÀM SẠCH VÀ XUẤT FILE THÀNH CÔNG")
print("========================================")
print("File: web_traffic_silver.csv")
print("Số dòng:", len(df_web))
print("Số cột:", len(df_web.columns))
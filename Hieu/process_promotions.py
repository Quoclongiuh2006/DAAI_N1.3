"""
=============================================================================
MODULE: PROMOTIONS - BRONZE TO SILVER TRANSFORMATION
=============================================================================
Tác giả: Senior Data Analyst & Engineer
Mô tả: Chuẩn hóa dữ liệu khuyến mãi từ tầng Bronze lên Silver với các bước:
    - Điền giá trị null trong applicable_category thành 'All'
    - Ép kiểu start_date và end_date sang datetime
    - Tính toán campaign_duration_days
    - Chuẩn hóa text về lowercase
=============================================================================
"""

import pandas as pd
import os
from pathlib import Path


def validate_promotions_quality(df: pd.DataFrame) -> None:
    """
    Kiểm tra chất lượng dữ liệu promotions theo các assertions
    
    Args:
        df: DataFrame chứa dữ liệu promotions đã xử lý
        
    Raises:
        AssertionError: Nếu dữ liệu không đạt tiêu chuẩn chất lượng
    """
    print("\n🔍 KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU PROMOTIONS...")
    
    # 1. Kiểm tra khóa chính không null
    assert df['promo_id'].notna().all(), \
        f"❌ FAILED: Có {df['promo_id'].isna().sum()} giá trị NULL trong promo_id (khóa chính)"
    print("✅ PASSED: Khóa chính promo_id không có giá trị NULL")
    
    # 2. Kiểm tra khóa chính không trùng lặp
    assert not df['promo_id'].duplicated().any(), \
        f"❌ FAILED: Có {df['promo_id'].duplicated().sum()} giá trị trùng lặp trong promo_id"
    print("✅ PASSED: Khóa chính promo_id không có giá trị trùng lặp")
    
    # 3. Kiểm tra applicable_category không còn NULL (đã điền 'All')
    assert df['applicable_category'].notna().all(), \
        f"❌ FAILED: Vẫn còn {df['applicable_category'].isna().sum()} giá trị NULL trong applicable_category"
    print("✅ PASSED: applicable_category đã được điền đầy đủ (không còn NULL)")
    
    # 4. Kiểm tra start_date và end_date đúng định dạng datetime
    assert pd.api.types.is_datetime64_any_dtype(df['start_date']), \
        "❌ FAILED: start_date chưa được chuyển sang datetime"
    print("✅ PASSED: start_date đã được chuyển sang datetime")
    
    assert pd.api.types.is_datetime64_any_dtype(df['end_date']), \
        "❌ FAILED: end_date chưa được chuyển sang datetime"
    print("✅ PASSED: end_date đã được chuyển sang datetime")
    
    # 5. Kiểm tra logic nghiệp vụ: end_date >= start_date
    invalid_dates = df[df['end_date'] < df['start_date']]
    assert len(invalid_dates) == 0, \
        f"❌ FAILED: Có {len(invalid_dates)} chiến dịch có end_date < start_date (không hợp lý)"
    print("✅ PASSED: Tất cả chiến dịch có end_date >= start_date")
    
    # 6. Kiểm tra campaign_duration_days đã được tính toán
    assert 'campaign_duration_days' in df.columns, \
        "❌ FAILED: Cột campaign_duration_days chưa được tạo"
    assert df['campaign_duration_days'].notna().all(), \
        f"❌ FAILED: Có {df['campaign_duration_days'].isna().sum()} giá trị NULL trong campaign_duration_days"
    print("✅ PASSED: campaign_duration_days đã được tính toán đầy đủ")
    
    # 7. Kiểm tra campaign_duration_days >= 0
    assert (df['campaign_duration_days'] >= 0).all(), \
        f"❌ FAILED: Có {(df['campaign_duration_days'] < 0).sum()} chiến dịch có duration âm"
    print("✅ PASSED: campaign_duration_days không có giá trị âm")
    
    # 8. Kiểm tra discount_value > 0
    assert (df['discount_value'] > 0).all(), \
        f"❌ FAILED: Có {(df['discount_value'] <= 0).sum()} khuyến mãi có discount_value <= 0"
    print("✅ PASSED: discount_value luôn lớn hơn 0")
    
    print(f"\n🎉 TẤT CẢ {8} KIỂM THỬ ĐÃ PASS! Dữ liệu promotions đạt chất lượng Silver.")


def process_promotions_to_silver() -> pd.DataFrame:
    """
    Xử lý dữ liệu promotions từ Bronze lên Silver
    
    Returns:
        DataFrame đã được xử lý và chuẩn hóa
    """
    # Lấy đường dẫn gốc của project
    project_root = Path(__file__).parent.parent
    
    # Đường dẫn input và output
    input_path = project_root / 'data' / 'promotions.csv'
    output_dir = project_root / 'data_silver'
    output_path = output_dir / 'promotions.csv'
    
    print(f"\n{'='*80}")
    print("🚀 BẮT ĐẦU XỬ LÝ: PROMOTIONS (Bronze → Silver)")
    print(f"{'='*80}")
    
    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(output_dir, exist_ok=True)
    print(f"📁 Thư mục đích: {output_dir}")
    
    # =========================================================================
    # BƯỚC 1: ĐỌC DỮ LIỆU TỪ BRONZE LAYER
    # =========================================================================
    print(f"\n📖 Đọc dữ liệu từ: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   ├─ Số dòng: {len(df):,}")
    print(f"   └─ Số cột: {len(df.columns)}")
    
    # =========================================================================
    # BƯỚC 2: ĐIỀN GIÁ TRỊ TRỐNG TRONG APPLICABLE_CATEGORY
    # =========================================================================
    print(f"\n🔧 Xử lý giá trị null trong applicable_category...")
    null_count_before = df['applicable_category'].isna().sum()
    print(f"   ├─ Số giá trị NULL trước: {null_count_before:,}")
    
    # Điền 'All' vào các giá trị null (khuyến mãi áp dụng toàn sàn)
    df['applicable_category'] = df['applicable_category'].fillna('All')
    
    null_count_after = df['applicable_category'].isna().sum()
    print(f"   ├─ Số giá trị NULL sau: {null_count_after:,}")
    print(f"   └─ Ý nghĩa: 'All' = Khuyến mãi áp dụng cho toàn bộ danh mục")
    
    # =========================================================================
    # BƯỚC 3: ÉP KIỂU START_DATE VÀ END_DATE SANG DATETIME
    # =========================================================================
    print(f"\n📅 Chuyển đổi start_date và end_date sang datetime...")
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    print(f"   ├─ start_date: {df['start_date'].dtype}")
    print(f"   └─ end_date: {df['end_date'].dtype}")
    
    # =========================================================================
    # BƯỚC 4: TÍNH TOÁN CAMPAIGN_DURATION_DAYS
    # =========================================================================
    print(f"\n⏱️  Tính toán campaign_duration_days...")
    df['campaign_duration_days'] = (df['end_date'] - df['start_date']).dt.days
    print(f"   └─ campaign_duration_days = end_date - start_date (đơn vị: ngày)")
    
    # Thống kê
    print(f"\n   📊 Thống kê thời gian chiến dịch:")
    print(f"      ├─ Trung bình: {df['campaign_duration_days'].mean():.1f} ngày")
    print(f"      ├─ Ngắn nhất: {df['campaign_duration_days'].min()} ngày")
    print(f"      └─ Dài nhất: {df['campaign_duration_days'].max()} ngày")
    
    # =========================================================================
    # BƯỚC 5: CHUẨN HÓA TEXT VỀ LOWERCASE
    # =========================================================================
    print(f"\n🔤 Chuẩn hóa text về lowercase...")
    
    # promo_type: percentage, fixed
    df['promo_type'] = df['promo_type'].str.lower()
    print(f"   ├─ promo_type: lowercase")
    
    # promo_channel: email, online, social_media, in_store, all_channels
    df['promo_channel'] = df['promo_channel'].str.lower()
    print(f"   └─ promo_channel: lowercase")
    
    # =========================================================================
    # BƯỚC 6: KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU
    # =========================================================================
    validate_promotions_quality(df)
    
    # =========================================================================
    # BƯỚC 7: XUẤT DỮ LIỆU RA SILVER LAYER
    # =========================================================================
    print(f"\n💾 Xuất dữ liệu ra: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"   └─ Đã ghi {len(df):,} dòng thành công")
    
    print(f"\n{'='*80}")
    print("✅ HOÀN THÀNH: PROMOTIONS (Bronze → Silver)")
    print(f"{'='*80}\n")
    
    return df


# ============================================================================
# CHẠY MODULE NẾU ĐƯỢC THỰC THI TRỰC TIẾP
# ============================================================================
if __name__ == "__main__":
    df_promotions = process_promotions_to_silver()
    
    # Hiển thị mẫu dữ liệu
    print("\n📋 PREVIEW 5 DÒNG ĐẦU TIÊN:")
    print(df_promotions.head())
    
    print("\n📊 PHÂN PHỐI PROMO_TYPE:")
    print(df_promotions['promo_type'].value_counts())
    
    print("\n📊 PHÂN PHỐI PROMO_CHANNEL:")
    print(df_promotions['promo_channel'].value_counts())
    
    print("\n📊 PHÂN PHỐI APPLICABLE_CATEGORY:")
    print(df_promotions['applicable_category'].value_counts())

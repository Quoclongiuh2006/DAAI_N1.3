"""
=============================================================================
MODULE: PRODUCTS - BRONZE TO SILVER TRANSFORMATION
=============================================================================
Tác giả: Senior Data Analyst & Engineer
Mô tả: Chuẩn hóa dữ liệu sản phẩm từ tầng Bronze lên Silver với các bước:
    - Làm tròn price và cogs về DECIMAL(12,2)
    - Tính toán gross_profit và margin_rate
    - Chuẩn hóa text theo business rules
    - Kiểm thử data quality
=============================================================================
"""

import pandas as pd
import os
from pathlib import Path


def validate_products_quality(df: pd.DataFrame) -> None:
    """
    Kiểm tra chất lượng dữ liệu products theo các assertions
    
    Args:
        df: DataFrame chứa dữ liệu products đã xử lý
        
    Raises:
        AssertionError: Nếu dữ liệu không đạt tiêu chuẩn chất lượng
    """
    print("\n🔍 KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU PRODUCTS...")
    
    # 1. Kiểm tra khóa chính không null
    assert df['product_id'].notna().all(), \
        f"❌ FAILED: Có {df['product_id'].isna().sum()} giá trị NULL trong product_id (khóa chính)"
    print("✅ PASSED: Khóa chính product_id không có giá trị NULL")
    
    # 2. Kiểm tra khóa chính không trùng lặp
    assert not df['product_id'].duplicated().any(), \
        f"❌ FAILED: Có {df['product_id'].duplicated().sum()} giá trị trùng lặp trong product_id"
    print("✅ PASSED: Khóa chính product_id không có giá trị trùng lặp")
    
    # 3. Kiểm tra price và cogs đã làm tròn đúng
    assert all(df['price'].apply(lambda x: len(str(x).split('.')[-1]) <= 2)), \
        "❌ FAILED: Cột price chưa được làm tròn đúng 2 chữ số thập phân"
    print("✅ PASSED: Cột price đã làm tròn đúng 2 chữ số thập phân")
    
    assert all(df['cogs'].apply(lambda x: len(str(x).split('.')[-1]) <= 2)), \
        "❌ FAILED: Cột cogs chưa được làm tròn đúng 2 chữ số thập phân"
    print("✅ PASSED: Cột cogs đã làm tròn đúng 2 chữ số thập phân")
    
    # 4. Kiểm tra logic nghiệp vụ: price >= cogs
    assert (df['price'] >= df['cogs']).all(), \
        f"❌ FAILED: Có {(df['price'] < df['cogs']).sum()} sản phẩm có price < cogs (không hợp lý)"
    print("✅ PASSED: Tất cả sản phẩm có price >= cogs")
    
    # 5. Kiểm tra margin_rate hợp lệ (0 <= margin_rate <= 1)
    assert (df['margin_rate'] >= 0).all() and (df['margin_rate'] <= 1).all(), \
        "❌ FAILED: margin_rate phải nằm trong khoảng [0, 1]"
    print("✅ PASSED: margin_rate nằm trong khoảng hợp lệ [0, 1]")
    
    # 6. Kiểm tra cột bắt buộc không null
    required_columns = ['product_name', 'category', 'segment', 'size', 'color']
    for col in required_columns:
        assert df[col].notna().all(), \
            f"❌ FAILED: Cột {col} có {df[col].isna().sum()} giá trị NULL"
    print(f"✅ PASSED: Các cột bắt buộc {required_columns} không có NULL")
    
    print(f"\n🎉 TẤT CẢ {6} KIỂM THỬ ĐÃ PASS! Dữ liệu products đạt chất lượng Silver.")


def process_products_to_silver() -> pd.DataFrame:
    """
    Xử lý dữ liệu products từ Bronze lên Silver
    
    Returns:
        DataFrame đã được xử lý và chuẩn hóa
    """
    # Lấy đường dẫn gốc của project
    project_root = Path(__file__).parent.parent
    
    # Đường dẫn input và output
    input_path = project_root / 'data' / 'products.csv'
    output_dir = project_root / 'data_silver'
    output_path = output_dir / 'product.csv'
    
    print(f"\n{'='*80}")
    print("🚀 BẮT ĐẦU XỬ LÝ: PRODUCTS (Bronze → Silver)")
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
    # BƯỚC 2: LÀM TRÒN GIÁ TRỊ TÀI CHÍNH (DECIMAL 12,2)
    # =========================================================================
    print(f"\n💰 Làm tròn giá trị tài chính...")
    df['price'] = df['price'].round(2)
    df['cogs'] = df['cogs'].round(2)
    print(f"   ├─ price: làm tròn 2 chữ số thập phân")
    print(f"   └─ cogs: làm tròn 2 chữ số thập phân")
    
    # =========================================================================
    # BƯỚC 3: TÍNH TOÁN CÁC CỘT PHÁI SINH (DERIVED COLUMNS)
    # =========================================================================
    print(f"\n📊 Tính toán cột phái sinh...")
    
    # Gross Profit = Price - COGS
    df['gross_profit'] = (df['price'] - df['cogs']).round(2)
    print(f"   ├─ gross_profit = price - cogs")
    
    # Margin Rate = (Price - COGS) / Price
    # NOTE: Xử lý trường hợp price = 0 để tránh division by zero
    df['margin_rate'] = df.apply(
        lambda row: round((row['price'] - row['cogs']) / row['price'], 4) 
                    if row['price'] > 0 else 0.0,
        axis=1
    )
    print(f"   └─ margin_rate = (price - cogs) / price (4 chữ số)")
    
    # =========================================================================
    # BƯỚC 4: CHUẨN HÓA TEXT THEO BUSINESS RULES
    # =========================================================================
    print(f"\n🔤 Chuẩn hóa định dạng text...")
    
    # Category và Segment: Title Case (Chữ Đầu Viết Hoa)
    df['category'] = df['category'].str.title()
    print(f"   ├─ category: Title Case")
    
    df['segment'] = df['segment'].str.title()
    print(f"   ├─ segment: Title Case")
    
    # Size: UPPER CASE (VIẾT HOA)
    df['size'] = df['size'].str.upper()
    print(f"   ├─ size: UPPER")
    
    # Color: lower case (viết thường)
    df['color'] = df['color'].str.lower()
    print(f"   └─ color: lower")
    
    # =========================================================================
    # BƯỚC 5: KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU
    # =========================================================================
    validate_products_quality(df)
    
    # =========================================================================
    # BƯỚC 6: XUẤT DỮ LIỆU RA SILVER LAYER
    # =========================================================================
    print(f"\n💾 Xuất dữ liệu ra: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"   └─ Đã ghi {len(df):,} dòng thành công")
    
    print(f"\n{'='*80}")
    print("✅ HOÀN THÀNH: PRODUCTS (Bronze → Silver)")
    print(f"{'='*80}\n")
    
    return df


# ============================================================================
# CHẠY MODULE NẾU ĐƯỢC THỰC THI TRỰC TIẾP
# ============================================================================
if __name__ == "__main__":
    df_products = process_products_to_silver()
    
    # Hiển thị mẫu dữ liệu
    print("\n📋 PREVIEW 5 DÒNG ĐẦU TIÊN:")
    print(df_products.head())
    
    print("\n📊 THỐNG KÊ MÔ TẢ:")
    print(df_products[['price', 'cogs', 'gross_profit', 'margin_rate']].describe())

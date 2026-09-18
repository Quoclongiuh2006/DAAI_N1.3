"""
=============================================================================
MODULE: INVENTORY - BRONZE TO SILVER TRANSFORMATION
=============================================================================
Tác giả: Senior Data Analyst & Engineer
Mô tả: Chuẩn hóa dữ liệu tồn kho từ tầng Bronze lên Silver với các bước:
    - Ép kiểu snapshot_date sang datetime chuẩn ISO
    - Tái lập logic reorder_flag
    - Làm tròn sell_through_rate
    - Kiểm tra toàn vẹn tham chiếu với bảng products
=============================================================================
"""

import pandas as pd
import os
from pathlib import Path


def validate_inventory_quality(df_inventory: pd.DataFrame, df_products: pd.DataFrame) -> None:
    """
    Kiểm tra chất lượng dữ liệu inventory theo các assertions
    
    Args:
        df_inventory: DataFrame chứa dữ liệu inventory đã xử lý
        df_products: DataFrame chứa dữ liệu products để kiểm tra khóa ngoại
        
    Raises:
        AssertionError: Nếu dữ liệu không đạt tiêu chuẩn chất lượng
    """
    print("\n🔍 KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU INVENTORY...")
    
    # 1. Kiểm tra khóa chính tổ hợp không null
    assert df_inventory['snapshot_date'].notna().all(), \
        f"❌ FAILED: Có {df_inventory['snapshot_date'].isna().sum()} giá trị NULL trong snapshot_date"
    print("✅ PASSED: Cột snapshot_date (khóa chính) không có NULL")
    
    assert df_inventory['product_id'].notna().all(), \
        f"❌ FAILED: Có {df_inventory['product_id'].isna().sum()} giá trị NULL trong product_id"
    print("✅ PASSED: Cột product_id (khóa chính) không có NULL")
    
    # 2. Kiểm tra khóa chính tổ hợp không trùng lặp
    composite_key = df_inventory[['snapshot_date', 'product_id']].duplicated()
    assert not composite_key.any(), \
        f"❌ FAILED: Có {composite_key.sum()} cặp (snapshot_date, product_id) trùng lặp"
    print("✅ PASSED: Khóa chính tổ hợp (snapshot_date, product_id) không trùng lặp")
    
    # 3. Kiểm tra snapshot_date đúng định dạng datetime
    assert pd.api.types.is_datetime64_any_dtype(df_inventory['snapshot_date']), \
        "❌ FAILED: snapshot_date chưa được chuyển sang datetime"
    print("✅ PASSED: snapshot_date đã được chuyển sang datetime")
    
    # 4. Kiểm tra toàn vẹn tham chiếu (Referential Integrity)
    products_set = set(df_products['product_id'].unique())
    inventory_products = set(df_inventory['product_id'].unique())
    orphan_products = inventory_products - products_set
    
    assert len(orphan_products) == 0, \
        f"❌ FAILED: Có {len(orphan_products)} product_id trong inventory không tồn tại trong bảng products: {list(orphan_products)[:5]}"
    print(f"✅ PASSED: Toàn vẹn tham chiếu - Tất cả {len(inventory_products)} product_id đều tồn tại trong bảng products")
    
    # 5. Kiểm tra logic reorder_flag
    # reorder_flag = 1 nếu (stockout_days > 0) HOẶC (days_of_supply < 15)
    expected_reorder = ((df_inventory['stockout_days'] > 0) | 
                        (df_inventory['days_of_supply'] < 15)).astype(int)
    reorder_mismatch = (df_inventory['reorder_flag'] != expected_reorder).sum()
    
    assert reorder_mismatch == 0, \
        f"❌ FAILED: Có {reorder_mismatch} dòng reorder_flag không khớp với logic nghiệp vụ"
    print("✅ PASSED: reorder_flag đã được tính toán đúng logic")
    
    # 6. Kiểm tra sell_through_rate đã làm tròn
    # Chuyển về string để đếm số chữ số thập phân
    decimal_check = df_inventory['sell_through_rate'].apply(
        lambda x: len(str(x).split('.')[-1]) <= 4 if pd.notna(x) else True
    )
    assert decimal_check.all(), \
        "❌ FAILED: sell_through_rate chưa được làm tròn đúng 4 chữ số"
    print("✅ PASSED: sell_through_rate đã làm tròn đúng 4 chữ số thập phân")
    
    # 7. Kiểm tra giá trị số không âm (business logic)
    numeric_cols = ['stock_on_hand', 'units_received', 'units_sold', 'stockout_days']
    for col in numeric_cols:
        assert (df_inventory[col] >= 0).all(), \
            f"❌ FAILED: Cột {col} có giá trị âm (không hợp lý)"
    print(f"✅ PASSED: Các cột số {numeric_cols} không có giá trị âm")
    
    print(f"\n🎉 TẤT CẢ {7} KIỂM THỬ ĐÃ PASS! Dữ liệu inventory đạt chất lượng Silver.")


def process_inventory_to_silver() -> pd.DataFrame:
    """
    Xử lý dữ liệu inventory từ Bronze lên Silver
    
    Returns:
        DataFrame đã được xử lý và chuẩn hóa
    """
    # Lấy đường dẫn gốc của project
    project_root = Path(__file__).parent.parent
    
    # Đường dẫn input và output
    input_path = project_root / 'data' / 'inventory.csv'
    output_dir = project_root / 'data_silver'
    output_path = output_dir / 'inventory.csv'
    
    # Đường dẫn products để kiểm tra referential integrity
    products_path = output_dir / 'product.csv'
    
    print(f"\n{'='*80}")
    print("🚀 BẮT ĐẦU XỬ LÝ: INVENTORY (Bronze → Silver)")
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
    # BƯỚC 2: ÉP KIỂU SNAPSHOT_DATE SANG DATETIME CHUẨN ISO
    # =========================================================================
    print(f"\n📅 Chuyển đổi snapshot_date sang datetime...")
    df['snapshot_date'] = pd.to_datetime(df['snapshot_date'])
    print(f"   ├─ Kiểu dữ liệu: {df['snapshot_date'].dtype}")
    print(f"   ├─ Ngày sớm nhất: {df['snapshot_date'].min()}")
    print(f"   └─ Ngày muộn nhất: {df['snapshot_date'].max()}")
    
    # =========================================================================
    # BƯỚC 3: TÁI LẬP LOGIC REORDER_FLAG
    # =========================================================================
    print(f"\n🔄 Tái lập logic reorder_flag...")
    print(f"   Logic: reorder_flag = 1 nếu (stockout_days > 0) HOẶC (days_of_supply < 15)")
    
    # Đếm số lượng trước khi thay đổi
    old_reorder_count = df['reorder_flag'].sum()
    
    # Tính toán lại reorder_flag theo logic nghiệp vụ
    df['reorder_flag'] = ((df['stockout_days'] > 0) | 
                          (df['days_of_supply'] < 15)).astype(int)
    
    new_reorder_count = df['reorder_flag'].sum()
    
    print(f"   ├─ Trước: {old_reorder_count:,} sản phẩm cần reorder")
    print(f"   ├─ Sau: {new_reorder_count:,} sản phẩm cần reorder")
    print(f"   └─ Thay đổi: {new_reorder_count - old_reorder_count:+,}")
    
    # =========================================================================
    # BƯỚC 4: LÀM TRÒN SELL_THROUGH_RATE
    # =========================================================================
    print(f"\n📈 Làm tròn sell_through_rate...")
    df['sell_through_rate'] = df['sell_through_rate'].round(4)
    print(f"   └─ sell_through_rate: làm tròn 4 chữ số thập phân")
    
    # =========================================================================
    # BƯỚC 5: KIỂM THỬ CHẤT LƯỢNG DỮ LIỆU
    # =========================================================================
    # Đọc dữ liệu products để kiểm tra referential integrity
    if products_path.exists():
        print(f"\n🔗 Đọc dữ liệu products để kiểm tra toàn vẹn tham chiếu...")
        df_products = pd.read_csv(products_path)
        validate_inventory_quality(df, df_products)
    else:
        print(f"\n⚠️  WARNING: File {products_path} chưa tồn tại. Bỏ qua kiểm tra referential integrity.")
        print(f"   💡 Gợi ý: Chạy process_products.py trước để tạo file product.csv")
    
    # =========================================================================
    # BƯỚC 6: XUẤT DỮ LIỆU RA SILVER LAYER
    # =========================================================================
    print(f"\n💾 Xuất dữ liệu ra: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"   └─ Đã ghi {len(df):,} dòng thành công")
    
    print(f"\n{'='*80}")
    print("✅ HOÀN THÀNH: INVENTORY (Bronze → Silver)")
    print(f"{'='*80}\n")
    
    return df


# ============================================================================
# CHẠY MODULE NẾU ĐƯỢC THỰC THI TRỰC TIẾP
# ============================================================================
if __name__ == "__main__":
    df_inventory = process_inventory_to_silver()
    
    # Hiển thị mẫu dữ liệu
    print("\n📋 PREVIEW 5 DÒNG ĐẦU TIÊN:")
    print(df_inventory.head())
    
    print("\n📊 THỐNG KÊ REORDER FLAG:")
    print(df_inventory['reorder_flag'].value_counts())
    
    print("\n📊 THỐNG KÊ SELL_THROUGH_RATE:")
    print(df_inventory['sell_through_rate'].describe())

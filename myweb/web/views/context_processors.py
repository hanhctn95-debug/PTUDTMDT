# web/views/context_processors.py
from ..models import DanhMuc, GioHang, ChiTietGioHang, TaiKhoan

def global_data(request):
    # 1. Lấy danh mục menu (Code cũ)
    danh_muc_menu = DanhMuc.objects.all().order_by('TenDanhMuc')
    
    # 2. Lấy số lượng giỏ hàng (Code MỚI)
    cart_count = 0
    
    # Chỉ đếm khi đã đăng nhập
    if 'khach_hang_id' in request.session:
        try:
            kh_id = request.session['khach_hang_id']
            khach_hang = TaiKhoan.objects.get(pk=kh_id)
            
            # Tìm giỏ hàng của khách
            gio_hang = GioHang.objects.filter(TaiKhoan=khach_hang).first()
            
            if gio_hang:
                # Đếm tổng số lượng sản phẩm trong giỏ
                # Cách 1: Đếm số dòng (số loại sản phẩm)
                cart_count = ChiTietGioHang.objects.filter(GioHang=gio_hang).count()
                
                # Cách 2: Nếu muốn đếm tổng số lượng (ví dụ: mua 2 cái bút + 3 quyển vở = 5)
                # items = ChiTietGioHang.objects.filter(GioHang=gio_hang)
                # cart_count = sum(item.SoLuong for item in items)
                
        except Exception as e:
            print(f"Lỗi context processor: {e}")

    return {
        'danh_muc_menu': danh_muc_menu,
        'cart_count': cart_count, # Biến này sẽ dùng ở base.html
    }
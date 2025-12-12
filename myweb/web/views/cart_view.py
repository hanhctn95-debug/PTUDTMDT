from django.shortcuts import render, redirect, get_object_or_404
from ..models import SanPham, GioHang, ChiTietGioHang, TaiKhoan
from django.contrib import messages

# 1. HÀM THÊM VÀO GIỎ (Dùng khi bấm nút "Thêm" ở trang chủ/chi tiết)
def add_to_cart(request, product_id):
    # 1. Kiểm tra đăng nhập (Dùng session)
    if 'khach_hang_id' not in request.session:
        # Lưu lại trang hiện tại để đăng nhập xong quay lại (Optional)
        return redirect('web:login') 

    try:
        # 2. Lấy thông tin khách hàng và sản phẩm
        kh_id = request.session['khach_hang_id']
        khach_hang = TaiKhoan.objects.get(pk=kh_id)
        san_pham = get_object_or_404(SanPham, pk=product_id)

        # Lấy số lượng từ form POST, mặc định là 1 nếu là GET
        so_luong_them = 1
        if request.method == 'POST':
            so_luong_them = int(request.POST.get('quantity', 1))
            if so_luong_them < 1: # Đảm bảo số lượng hợp lệ
                so_luong_them = 1

        # 3. Lấy hoặc tạo Giỏ hàng cho khách này
        gio_hang, _ = GioHang.objects.get_or_create(TaiKhoan=khach_hang)

        # 4. Lấy hoặc tạo chi tiết giỏ hàng
        cart_item, created = ChiTietGioHang.objects.get_or_create(
            GioHang=gio_hang, 
            SanPham=san_pham,
            defaults={'SoLuong': 0}
        )

        # 5. Tăng số lượng
        cart_item.SoLuong += so_luong_them
        cart_item.save()

        # 6. Thông báo thành công
        messages.success(request, f"Đã thêm {so_luong_them} sản phẩm '{san_pham.TenSanPham}' vào giỏ hàng!")
    
    except Exception as e:
        print(f"Lỗi thêm giỏ hàng: {e}")
        messages.error(request, "Có lỗi xảy ra khi thêm vào giỏ.")
        return redirect('web:home')

    # 7. ĐIỀU HƯỚNG
    # Ưu tiên action từ POST (cho form Mua ngay), sau đó đến GET
    action = request.POST.get('action') or request.GET.get('action')
    
    # Nếu có action=buy_now -> Chuyển đến trang Giỏ hàng
    if action == 'buy_now':
        return redirect('web:view_cart')
    
    # Mặc định ở lại trang cũ
    return redirect(request.META.get('HTTP_REFERER', 'web:home'))

# 2. HÀM XEM GIỎ HÀNG
# web/views/cart_view.py

def view_cart(request):
    if 'khach_hang_id' not in request.session:
        return redirect('web:login')

    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)
    
    # Lấy giỏ hàng
    gio_hang = GioHang.objects.filter(TaiKhoan=khach_hang).first()
    cart_items = []
    tong_tien = 0

    if gio_hang:
        # Dùng select_related để tối ưu, lấy luôn thông tin SanPham kèm theo
        cart_items = ChiTietGioHang.objects.filter(GioHang=gio_hang).select_related('SanPham')
        
        # --- SỬA ĐOẠN TÍNH TIỀN NÀY ---
        for item in cart_items:
            # 1. Lấy giá đã giảm (new_price) từ hàm trong Model
            new_price, percent, discount_amt = item.SanPham.get_discounted_price()
            
            # 2. Tính tổng tiền item theo giá mới
            item.tong_gia = new_price * item.SoLuong
            
            # 3. Cộng dồn vào tổng tiền giỏ hàng
            tong_tien += item.tong_gia
            
            # (Optional) Gán thêm biến để hiển thị ra HTML nếu muốn báo khách là được giảm bao nhiêu
            item.price_display = new_price
            item.old_price = item.SanPham.DonGia if percent > 0 else None
            item.discount_percent = percent

    context = {
        'cart_items': cart_items,
        'tong_tien': tong_tien
    }
    return render(request, 'cart.html', context)

# 3. HÀM XÓA SẢN PHẨM KHỎI GIỎ
def remove_from_cart(request, item_id):
    if 'khach_hang_id' in request.session:
        try:
            item = ChiTietGioHang.objects.get(pk=item_id)
            item.delete()
            messages.success(request, "Đã xóa sản phẩm khỏi giỏ.")
        except:
            pass
    return redirect('web:view_cart')
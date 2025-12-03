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

        # 3. Lấy hoặc tạo Giỏ hàng cho khách này
        gio_hang, created = GioHang.objects.get_or_create(TaiKhoan=khach_hang)

        # 4. Kiểm tra xem sản phẩm này đã có trong giỏ chưa
        cart_item, created = ChiTietGioHang.objects.get_or_create(
            GioHang=gio_hang, 
            SanPham=san_pham,
            defaults={'SoLuong': 0}
        )

        # 5. Tăng số lượng lên 1
        cart_item.SoLuong += 1
        cart_item.save()

        # 6. Thông báo thành công (Hiện ở base.html)
        messages.success(request, f"Đã thêm vào giỏ hàng!")
    
    except Exception as e:
        print(f"Lỗi thêm giỏ hàng: {e}")
        messages.error(request, "Có lỗi xảy ra khi thêm vào giỏ.")
        return redirect('web:home')

    # 7. ĐIỀU HƯỚNG (Logic quan trọng bạn yêu cầu)
    action = request.GET.get('action')
    
    # Nếu bấm nút "MUA NGAY" -> Chuyển đến trang Giỏ hàng
    if action == 'buy_now':
        return redirect('web:view_cart')
    
    # Nếu bấm nút "Thêm vào giỏ" -> Ở lại trang cũ (Reload lại trang hiện tại)
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
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import TaiKhoan, GioHang, DiaChi, PhuongThucThanhToan, DonHang, ChiTietDonHang, GiamGia
from django.utils import timezone


#Tính lại tổng tiền từ đầu chứ không lấy từ js tránh xung đột python với js
def checkout(request):
    # 1. Bắt buộc đăng nhập
    if 'khach_hang_id' not in request.session:
        return redirect('web:login')
    
    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)

    # 2. Kiểm tra giỏ hàng
    gio_hang = GioHang.objects.filter(TaiKhoan=khach_hang).first()
    if not gio_hang or not gio_hang.items.exists():
        return redirect('web:home')
    
    # 3. TÍNH TOÁN DỮ LIỆU (Dùng chung cho cả GET và POST)
    cart_items = list(gio_hang.items.select_related('SanPham').all())
    
    server_tam_tinh = 0
    for item in cart_items:
        # Lấy giá chuẩn từ Database (đã giảm giá sản phẩm nếu có)
        price, _, _ = item.SanPham.get_discounted_price()
        item.tong_gia_item = price * item.SoLuong
        server_tam_tinh += item.tong_gia_item
        
    server_phi_ship = 30000 if server_tam_tinh < 500000 else 0
    # Đây là tổng tiền gốc (chưa trừ voucher) tính bởi Python
    server_tong_cong = server_tam_tinh + server_phi_ship 

    # --- XỬ LÝ KHI BẤM NÚT "HOÀN TẤT ĐƠN HÀNG" (POST) ---
    if request.method == 'POST':
        try:
            # Lấy thông tin giao hàng
            sdt = request.POST.get('shipping_phone')
            dia_chi_text = request.POST.get('shipping_address')
            tinh = request.POST.get('shipping_city')
            huyen = request.POST.get('shipping_ward')
            pttt_id = request.POST.get('payment_method')
            selected_id = request.POST.get('selected_address_id')
            
            # CHỈ LẤY MÃ CODE, KHÔNG LẤY TIỀN TỪ HTML (ĐỂ TRÁNH LỖI)
            coupon_code = request.POST.get('coupon_code')

            # Validate
            if not pttt_id:
                messages.error(request, "Vui lòng chọn phương thức thanh toán.")
                return redirect('web:checkout')

            # 1. Xử lý địa chỉ (Logic thông minh: Dùng lại hoặc Tạo mới)
            dia_chi_giao = None
            create_new = True 
            if selected_id:
                try:
                    old_addr = DiaChi.objects.get(pk=selected_id)
                    check_sdt = old_addr.SDTLienHe.strip() == sdt.strip()
                    check_text = old_addr.ChiTietDiaChi.strip() == dia_chi_text.strip()
                    # So sánh tương đối để tránh lỗi chữ hoa thường
                    check_tinh = old_addr.Tinh_Thanh_Pho.strip().lower() == tinh.strip().lower()
                    
                    if check_sdt and check_text and check_tinh:
                        dia_chi_giao = old_addr
                        create_new = False
                except DiaChi.DoesNotExist:
                    pass

            if create_new:
                dia_chi_giao = DiaChi.objects.create(
                    TaiKhoan=khach_hang,
                    SDTLienHe=sdt,
                    ChiTietDiaChi=dia_chi_text,
                    Tinh_Thanh_Pho=tinh,
                    Phuong_Xa=huyen,
                    MacDinh=False 
                )

            # 2. TÍNH TOÁN LẠI MÃ GIẢM GIÁ (SERVER SIDE)
            obj_giam_gia = None
            # Bắt đầu với tổng tiền gốc do Python tính
            final_money_to_save = server_tong_cong 

            if coupon_code:
                try:
                    # Query lại DB để lấy thông tin mã
                    coupon = GiamGia.objects.get(MaGiamGia=coupon_code)
                    now = timezone.now()
                    
                    # Kiểm tra hạn sử dụng
                    if coupon.TGbatDau <= now <= coupon.TGKetThuc:
                        obj_giam_gia = coupon
                        
                        # Thực hiện trừ tiền
                        # Lưu ý: Model GiamGia của bạn đang lưu số tiền cố định (AMOUNT)
                        discount_value = coupon.GiaTriGiam
                        final_money_to_save = final_money_to_save - discount_value
                        
                        # Không để tiền âm
                        if final_money_to_save < 0: 
                            final_money_to_save = 0
                except GiamGia.DoesNotExist:
                    pass # Mã sai thì bỏ qua, vẫn lưu đơn với giá gốc

            # 3. Lưu Đơn Hàng (Dùng biến final_money_to_save đã tính sạch sẽ)
            thanh_toan = PhuongThucThanhToan.objects.get(pk=pttt_id)
            don_hang = DonHang.objects.create(
                TaiKhoan=khach_hang,
                ThanhToan=thanh_toan,
                DiaChi=dia_chi_giao,
                TongTien=final_money_to_save, 
                TrangThaiGH='Chờ xử lý',
                GiamGia=obj_giam_gia
            )

            # 4. Lưu chi tiết
            for item in cart_items:
                # Lấy giá tại thời điểm mua
                price_at_purchase, _, _ = item.SanPham.get_discounted_price()
                ChiTietDonHang.objects.create(
                    DonHang=don_hang,
                    SanPham=item.SanPham,
                    SoLuong=item.SoLuong,
                    DonGiaTaiThoiDiemMua=price_at_purchase
                )
                # Trừ tồn kho
                item.SanPham.SoLuongTonKho -= item.SoLuong
                item.SanPham.save()

            # 5. Xóa giỏ
            gio_hang.items.all().delete()

            return redirect('web:order_success')

        except Exception as e:
            print(f"Lỗi Checkout: {e}") 
            messages.error(request, f"Lỗi chi tiết: {e}")
            return redirect('web:checkout') 

    # --- GET: Hiển thị trang ---
    addresses = DiaChi.objects.filter(TaiKhoan=khach_hang).order_by('-MacDinh')
    payment_methods = PhuongThucThanhToan.objects.all()

    context = {
        'user': khach_hang,
        'items': cart_items,
        'tam_tinh': server_tam_tinh,
        'phi_van_chuyen': server_phi_ship,
        'tong_cong': server_tong_cong,
        'addresses': addresses,
        'payment_methods': payment_methods
    }
    return render(request, 'checkout.html', context)

def order_success(request):
    return render(request, 'order_success.html')
from django.shortcuts import render, redirect, get_object_or_404
from ..models import SanPham, GioHang, ChiTietGioHang, TaiKhoan
from django.contrib import messages
from django.http import JsonResponse 
from django.views.decorators.http import require_POST 
import json 

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

        # --- BẮT ĐẦU THÊM KIỂM TRA TỒN KHO ---
        if san_pham.SoLuongTonKho == 0:
            messages.error(request, f"Sản phẩm '{san_pham.TenSanPham}' hiện đã hết hàng.")
            return redirect(request.META.get('HTTP_REFERER', 'web:home'))

        # 3. Lấy hoặc tạo Giỏ hàng cho khách này
        gio_hang, _ = GioHang.objects.get_or_create(TaiKhoan=khach_hang)

        # 4. Lấy hoặc tạo chi tiết giỏ hàng
        cart_item, created = ChiTietGioHang.objects.get_or_create(
            GioHang=gio_hang, 
            SanPham=san_pham,
            defaults={'SoLuong': 0}
        )

        current_qty_in_cart = cart_item.SoLuong
        requested_total_qty = current_qty_in_cart + so_luong_them

        if requested_total_qty > san_pham.SoLuongTonKho:
            # Nếu số lượng yêu cầu vượt quá tồn kho, chỉ cho phép thêm tối đa
            if current_qty_in_cart < san_pham.SoLuongTonKho:
                allowed_to_add = san_pham.SoLuongTonKho - current_qty_in_cart
                cart_item.SoLuong = san_pham.SoLuongTonKho
                cart_item.save()
                messages.warning(request, f"Chỉ thêm được {allowed_to_add} sản phẩm '{san_pham.TenSanPham}' vào giỏ do không đủ hàng. Tổng số lượng trong giỏ hiện tại là {san_pham.SoLuongTonKho}.")
            else:
                messages.error(request, f"Sản phẩm '{san_pham.TenSanPham}' trong giỏ đã đạt số lượng tối đa có thể mua ({san_pham.SoLuongTonKho}).")
            return redirect(request.META.get('HTTP_REFERER', 'web:home'))
        
        # --- KẾT THÚC THÊM KIỂM TRA TỒN KHO ---

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

@require_POST
def update_cart_quantity(request):
    if 'khach_hang_id' not in request.session:
        return JsonResponse({'success': False, 'error': 'Bạn chưa đăng nhập.'}, status=401)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = data.get('quantity')

        if not item_id or not quantity:
            return JsonResponse({'success': False, 'error': 'Thiếu ID sản phẩm hoặc số lượng.'}, status=400)

        quantity = int(quantity)
        if quantity < 1:
            return JsonResponse({'success': False, 'error': 'Số lượng phải lớn hơn 0.'}, status=400)

        kh_id = request.session['khach_hang_id']
        khach_hang = TaiKhoan.objects.get(pk=kh_id)
        
        cart_item = get_object_or_404(ChiTietGioHang, pk=item_id, GioHang__TaiKhoan=khach_hang)
        
        san_pham = cart_item.SanPham
        if quantity > san_pham.SoLuongTonKho:
            return JsonResponse({'success': False, 'error': f"Chỉ còn {san_pham.SoLuongTonKho} sản phẩm '{san_pham.TenSanPham}' trong kho."}, status=400)
        
        cart_item.SoLuong = quantity
        cart_item.save()

        # Recalculate item total and cart total
        new_price, _, _ = cart_item.SanPham.get_discounted_price()
        item_total = new_price * cart_item.SoLuong

        # Get the cart and recalculate total
        gio_hang = cart_item.GioHang
        cart_items = ChiTietGioHang.objects.filter(GioHang=gio_hang).select_related('SanPham')
        cart_total = 0
        for item in cart_items:
            item_new_price, _, _ = item.SanPham.get_discounted_price()
            cart_total += item_new_price * item.SoLuong

        return JsonResponse({
            'success': True,
            'item_id': item_id,
            'new_quantity': quantity,
            'item_total': item_total,
            'cart_total': cart_total
        })

    except TaiKhoan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Khách hàng không tồn tại.'}, status=404)
    except ChiTietGioHang.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Sản phẩm trong giỏ hàng không tồn tại.'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu JSON không hợp lệ.'}, status=400)
    except Exception as e:
        print(f"Lỗi cập nhật số lượng giỏ hàng: {e}")
        return JsonResponse({'success': False, 'error': f'Đã xảy ra lỗi: {str(e)}'}, status=500)
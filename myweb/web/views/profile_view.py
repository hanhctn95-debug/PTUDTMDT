from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import TaiKhoan, DonHang, DiaChi, ChiTietDonHang
from .decorators import login_required
from django.db.models import Sum
from django.db.models import ProtectedError


@login_required
def profile_info(request):
    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)

    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            ten_moi = request.POST.get('fullname')
            sdt_moi = request.POST.get('phone')
            ngay_sinh = request.POST.get('dob') # Dạng chuỗi YYYY-MM-DD
            gioi_tinh = request.POST.get('gender')

            # Cập nhật vào đối tượng
            khach_hang.TenKhachHang = ten_moi
            khach_hang.SDT = sdt_moi
            khach_hang.GioiTinh = gioi_tinh
            
            # Xử lý ngày sinh (nếu có nhập)
            if ngay_sinh:
                khach_hang.NgaySinh = ngay_sinh
            
            # Lưu vào DB
            khach_hang.save()
            
            # Cập nhật lại tên trong session (để header đổi tên theo)
            request.session['khach_hang_ten'] = ten_moi
            
            messages.success(request, "Cập nhật thông tin thành công!")
            
        except Exception as e:
            print(e)
            messages.error(request, "Có lỗi xảy ra, vui lòng kiểm tra lại thông tin.")

    return render(request, 'profile/info.html', {'user': khach_hang})


# web/views/profile_view.py
@login_required
def membership(request):
    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)

    # 2. Tính tổng tiền (Chỉ tính đơn đã giao)
    tong_tien = DonHang.objects.filter(
        TaiKhoan=khach_hang, 
        TrangThaiGH='Đã giao hàng' 
    ).aggregate(Sum('TongTien'))['TongTien__sum'] or 0
    
    # 3. Logic xác định hạng và TIỀN CẦN MUA THÊM
    # Mặc định là hạng Thường (New)
    hang_hien_tai = "Thành viên mới"
    hang_tiep_theo = "Silver"
    tien_len_hang = 1000000 - tong_tien # Mốc Silver là 1 triệu
    icon_rank = "new_member.png" 

    # Logic leo hạng
    if 1000000 <= tong_tien < 3000000:
        hang_hien_tai = "Silver"
        hang_tiep_theo = "Gold"
        tien_len_hang = 3000000 - tong_tien
        icon_rank = "silver.png"
        
    elif 3000000 <= tong_tien < 7000000:
        hang_hien_tai = "Gold"
        hang_tiep_theo = "Platinum"
        tien_len_hang = 7000000 - tong_tien
        icon_rank = "gold.png"
        
    elif 7000000 <= tong_tien < 10000000:
        hang_hien_tai = "Platinum"
        hang_tiep_theo = "Diamond"
        tien_len_hang = 10000000 - tong_tien
        icon_rank = "platinum.png"
        
    elif tong_tien >= 10000000:
        hang_hien_tai = "Diamond"
        hang_tiep_theo = "Max Level"
        tien_len_hang = 0
        icon_rank = "diamond.png"

    # Cập nhật DB
    if khach_hang.HangThanhVien != hang_hien_tai:
        khach_hang.HangThanhVien = hang_hien_tai
        khach_hang.save()

    # Không cần tính 'percent' nữa
    context = {
        'user': khach_hang,
        'tong_tien': tong_tien,
        'hang_hien_tai': hang_hien_tai,
        'hang_tiep_theo': hang_tiep_theo,
        'tien_len_hang': tien_len_hang,
        'icon_rank': icon_rank
    }
    return render(request, 'profile/membership.html', context)

@login_required
def order_history(request):
    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)

    # 2. Lấy danh sách đơn hàng của khách này, sắp xếp mới nhất lên đầu (-NgayDat)
    don_hangs = DonHang.objects.filter(TaiKhoan=khach_hang).order_by('-NgayDat')

    context = {
        'user': khach_hang,
        'orders': don_hangs
    }
    return render(request, 'profile/orders.html', context)


@login_required
def address_book(request):
    kh_id = request.session['khach_hang_id']
    khach_hang = TaiKhoan.objects.get(pk=kh_id)

    if request.method == 'POST':
        try:
            sdt = request.POST.get('phone')
            tinh_tp = request.POST.get('city')
            phuong_xa = request.POST.get('ward')
            chi_tiet = request.POST.get('address_detail')
            
            # Lấy giá trị checkbox (nếu tích thì là 'on', không tích là None)
            is_default = request.POST.get('is_default') == 'on'
            
            # LOGIC QUAN TRỌNG: Nếu đặt cái mới là mặc định, thì bỏ mặc định các cái cũ đi
            if is_default:
                DiaChi.objects.filter(TaiKhoan=khach_hang).update(MacDinh=False)
            
            # Nếu đây là địa chỉ đầu tiên của khách, auto set mặc định luôn
            if not DiaChi.objects.filter(TaiKhoan=khach_hang).exists():
                is_default = True

            DiaChi.objects.create(
                TaiKhoan=khach_hang,
                SDTLienHe=sdt,
                Tinh_Thanh_Pho=tinh_tp,
                Phuong_Xa=phuong_xa,
                ChiTietDiaChi=chi_tiet,
                MacDinh=is_default # Lưu trạng thái
            )
            messages.success(request, "Thêm địa chỉ thành công!")
        except Exception as e:
            print(e)
            messages.error(request, "Lỗi thêm địa chỉ.")
        return redirect('web:profile_addresses')

    # Sắp xếp: Địa chỉ mặc định lên đầu (-MacDinh), sau đó đến mới nhất (-id)
    addresses = DiaChi.objects.filter(TaiKhoan=khach_hang).order_by('-MacDinh', '-id')

    context = {
        'user': khach_hang,
        'addresses': addresses
    }
    return render(request, 'profile/addresses.html', context)

# --- HÀM 2: ĐẶT MẶC ĐỊNH CHO ĐỊA CHỈ CŨ ---
@login_required
def set_default_address(request, address_id):
    kh_id = request.session['khach_hang_id']
    
    # 1. Reset tất cả về False
    DiaChi.objects.filter(TaiKhoan_id=kh_id).update(MacDinh=False)
    
    # 2. Set cái được chọn thành True
    DiaChi.objects.filter(id=address_id, TaiKhoan_id=kh_id).update(MacDinh=True)
    
    return redirect('web:profile_addresses')

# --- HÀM 3: XÓA ĐỊA CHỈ ---
@login_required
def delete_address(request, address_id):
    try:
        kh_id = request.session['khach_hang_id']
        # Tìm địa chỉ
        addr = DiaChi.objects.get(id=address_id, TaiKhoan_id=kh_id)
        
        # Cố gắng xóa
        addr.delete()
        messages.success(request, "Đã xóa địa chỉ thành công.")
        
    except DiaChi.DoesNotExist:
        messages.error(request, "Địa chỉ không tồn tại.")
        
    except ProtectedError:
        messages.error(request, "Không thể xóa địa chỉ này vì đã có đơn hàng sử dụng nó. Bạn hãy dùng tính năng Sửa.")
        
    except Exception as e:
        messages.error(request, "Có lỗi xảy ra, không thể xóa.")
        
    return redirect('web:profile_addresses')


@login_required
def edit_address(request, address_id):
    kh_id = request.session['khach_hang_id']
    
    # Chỉ xử lý POST (Khi bấm nút Lưu từ Modal)
    if request.method == 'POST':
        try:
            address = DiaChi.objects.get(pk=address_id, TaiKhoan_id=kh_id)
            
            # Cập nhật dữ liệu
            address.SDTLienHe = request.POST.get('phone')
            address.Tinh_Thanh_Pho = request.POST.get('city')
            address.Phuong_Xa = request.POST.get('ward')
            address.ChiTietDiaChi = request.POST.get('address_detail')
            
            is_default = request.POST.get('is_default') == 'on'
            if is_default:
                DiaChi.objects.filter(TaiKhoan_id=kh_id).update(MacDinh=False)
                address.MacDinh = True
            
            address.save()
            messages.success(request, "Cập nhật địa chỉ thành công!")
            
        except Exception as e:
            print(e)
            messages.error(request, "Lỗi cập nhật.")
            
    # Dù thành công hay thất bại, đều quay về trang danh sách địa chỉ
    return redirect('web:profile_addresses')

@login_required
def order_detail(request, order_id):
    kh_id = request.session['khach_hang_id']
    # 2. Lấy đơn hàng (Có kiểm tra bảo mật: Phải đúng ID khách hàng)
    try:
        don_hang = DonHang.objects.get(pk=order_id, TaiKhoan_id=kh_id)
    except DonHang.DoesNotExist:
        # Nếu cố tình xem đơn của người khác -> Đá về danh sách
        return redirect('web:profile_orders')

    # 3. Lấy chi tiết sản phẩm trong đơn đó
    chi_tiet = ChiTietDonHang.objects.filter(DonHang=don_hang).select_related('SanPham')
    
    # Ép kiểu thành list để gán biến tạm
    items_list = []
    subtotal = 0 

    for item in chi_tiet:
        item.thanh_tien_item = item.DonGiaTaiThoiDiemMua * item.SoLuong
        subtotal += item.thanh_tien_item
        items_list.append(item)
    
    # 1. TÍNH PHÍ SHIP (Logic giống hệt lúc Checkout)
    # Nếu đơn < 500k thì ship 30k, ngược lại free
    if subtotal < 500000:
        shipping_fee = 30000
    else:
        shipping_fee = 0

    # 2. TÍNH TIỀN GIẢM GIÁ
    # Công thức: (Hàng + Ship) - (Số tiền khách thực trả) = Số tiền được giảm
    # Ví dụ: Mua 200k + 30k ship = 230k. Khách trả 180k (do có mã).
    # => Giảm giá = 230k - 180k = 50k.
    expected_total = subtotal + shipping_fee
    discount_amount = expected_total - don_hang.TongTien

    # Xử lý làm tròn số âm (phòng trường hợp sai số nhỏ)
    if discount_amount < 0:
        discount_amount = 0

    context = {
        'user': don_hang.TaiKhoan,
        'order': don_hang,
        'items': items_list,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'discount_amount': discount_amount 
    }
    return render(request, 'profile/order_detail.html', context)
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import TaiKhoan

def login_view(request):
    # Nếu đã đăng nhập (có session) thì đá về trang chủ
    if 'khach_hang_id' in request.session:
        return redirect('web:home')

    if request.method == 'POST':
        email_input = request.POST.get('username') # Form HTML name="username" nhưng ta hiểu là email
        password_input = request.POST.get('password')

        try:
            # --- LOGIC MỚI: KIỂM TRA TRỰC TIẾP BẢNG TAIKHOAN ---
            # Tìm tài khoản có Email và MatKhau khớp
            user = TaiKhoan.objects.get(Email=email_input, MatKhau=password_input)
            
            # --- ĐĂNG NHẬP THÀNH CÔNG ---
            # Lưu thông tin vào Session (Bộ nhớ phiên làm việc)
            request.session['khach_hang_id'] = user.id
            request.session['khach_hang_ten'] = user.TenKhachHang
            
            messages.success(request, f"Xin chào {user.TenKhachHang}!")
            
            # Kiểm tra xem cần quay lại trang trước đó không
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            return redirect('web:home')
            
        except TaiKhoan.DoesNotExist:
            # Không tìm thấy tài khoản khớp
            messages.error(request, "Email hoặc mật khẩu không chính xác!")
    
    return render(request, 'login.html')

def logout_view(request):
    # Xóa session để đăng xuất
    if 'khach_hang_id' in request.session:
        del request.session['khach_hang_id']
    if 'khach_hang_ten' in request.session:
        del request.session['khach_hang_ten']
        
    messages.info(request, "Đã đăng xuất.")
    return redirect('web:home')


def register_view(request):
    """
    Hàm xử lý Đăng ký tài khoản mới
    """
    if request.method == 'POST':
        # 1. Lấy dữ liệu từ Form
        ten_kh = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        re_password = request.POST.get('re_password')

        # 2. Validate (Kiểm tra dữ liệu)
        
        # Kiểm tra mật khẩu nhập lại
        if password != re_password:
            messages.error(request, "Mật khẩu nhập lại không khớp!")
            return render(request, 'register.html')

        # Kiểm tra Email đã tồn tại chưa
        if TaiKhoan.objects.filter(Email=email).exists():
            messages.error(request, "Email này đã được sử dụng!")
            return render(request, 'register.html')

        # 3. Tạo tài khoản mới
        try:
            new_user = TaiKhoan.objects.create(
                TenKhachHang=ten_kh,
                Email=email,
                MatKhau=password, # Lưu ý: Nên mã hóa mật khẩu nếu làm dự án thật (hiện tại lưu text thường theo ý bạn)
                # Các trường khác như SDT, GioiTinh có thể update sau
            )

            # 4. Đăng ký xong -> Tự động đăng nhập luôn (Tạo session)
            request.session['khach_hang_id'] = new_user.id
            request.session['khach_hang_ten'] = new_user.TenKhachHang
            
            messages.success(request, "Đăng ký thành công! Chào mừng bạn đến với VPP Shop.")
            return redirect('web:home')

        except Exception as e:
            print(e)
            messages.error(request, "Có lỗi xảy ra, vui lòng thử lại.")

    return render(request, 'register.html')
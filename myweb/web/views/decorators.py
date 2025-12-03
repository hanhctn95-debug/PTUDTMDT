from django.shortcuts import redirect
from functools import wraps

def login_required(view_func):
    """
    Decorator kiểm tra xem người dùng đã đăng nhập hay chưa (dựa trên session).
    Nếu chưa đăng nhập, chuyển hướng đến trang login.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'khach_hang_id' not in request.session:
            return redirect('web:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
from django.shortcuts import render
from django.utils import timezone
from django.core.paginator import Paginator
# Dấu .. nghĩa là thoát ra khỏi thư mục views để tìm file models.py ở thư mục cha
from ..models import SanPham 

def index(request):
    # 1. Lấy từ khóa người dùng gửi lên (mặc định là rỗng nếu không có)
    query = request.GET.get('q', '')

    # 2. Lấy các sản phẩm có khuyến mãi đang hoạt động
    now = timezone.now()
    san_pham_list = SanPham.objects.filter(
        khuyen_mai__NgayBatDau__lte=now,
        khuyen_mai__NgayKetThuc__gte=now,
    ).distinct().prefetch_related('hinhanhs').order_by('-id')


    # 3. Nếu có từ khóa tìm kiếm -> Lọc danh sách
    if query:
        # icontains: Tìm kiếm tương đối (chứa từ khóa) và không phân biệt hoa/thường
        # Ví dụ: Tìm "bút" sẽ ra "Bút bi", "Hộp bút", "bút chì"...
        san_pham_list = san_pham_list.filter(TenSanPham__icontains=query)

    paginator = Paginator(san_pham_list, 10) # Show 10 products per page.
    page_number = request.GET.get('page')
    san_pham = paginator.get_page(page_number)

    context = {
        'san_pham': san_pham,
        'query': query, # Truyền lại từ khóa để hiển thị trong ô input ở base.html
    }

    return render(request, 'home.html', context)
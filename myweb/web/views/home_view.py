from django.shortcuts import render
# Dấu .. nghĩa là thoát ra khỏi thư mục views để tìm file models.py ở thư mục cha
from ..models import SanPham 

def index(request):
    # 1. Lấy từ khóa người dùng gửi lên (mặc định là rỗng nếu không có)
    query = request.GET.get('q', '')

    # 2. Khởi tạo danh sách sản phẩm gốc (Mới nhất lên đầu)
    san_pham = SanPham.objects.all().prefetch_related('hinhanhs').order_by('-id')

    # 3. Nếu có từ khóa tìm kiếm -> Lọc danh sách
    if query:
        # icontains: Tìm kiếm tương đối (chứa từ khóa) và không phân biệt hoa/thường
        # Ví dụ: Tìm "bút" sẽ ra "Bút bi", "Hộp bút", "bút chì"...
        san_pham = san_pham.filter(TenSanPham__icontains=query)

    context = {
        'san_pham': san_pham,
        'query': query, # Truyền lại từ khóa để hiển thị trong ô input ở base.html
    }

    return render(request, 'home.html', context)
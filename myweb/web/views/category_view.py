# web/views/category_view.py
from django.shortcuts import render, get_object_or_404
from ..models import SanPham, DanhMuc
from django.db.models import Q
from django.core.paginator import Paginator

def view_category(request, danh_muc_id):
    # 1. Lấy danh mục hiện tại (nếu ko có thì báo lỗi 404)
    danh_muc_hien_tai = get_object_or_404(DanhMuc, pk=danh_muc_id)
    
    # 2. Lấy tất cả sản phẩm thuộc danh mục này
    base_products = SanPham.objects.filter(DanhMuc=danh_muc_hien_tai)
    
    # --- SỬA LỖI TRÙNG LẶP TẠI ĐÂY ---
    # B1: Lấy danh sách thương hiệu
    # B2: .exclude(ThuongHieu__isnull=True): Bỏ dòng null
    # B3: .exclude(ThuongHieu__exact=''): Bỏ dòng rỗng
    # B4: .distinct(): Lọc trùng lặp (Cốt lõi)
    # B5: .order_by(): Sắp xếp A-Z
    all_brands = base_products.exclude(ThuongHieu__isnull=True)\
                              .exclude(ThuongHieu__exact='')\
                              .values_list('ThuongHieu', flat=True)\
                              .distinct()\
                              .order_by('ThuongHieu')

    # 2. Khởi tạo biến products để lọc (kế thừa từ base_products)
    products_list = base_products.prefetch_related('hinhanhs').order_by('id')
    
    # B. Lọc theo Thương hiệu (Người dùng tích chọn bên trái)
    selected_brands = request.GET.getlist('brand') # Lấy danh sách brand user chọn
    if selected_brands:
        products_list = products_list.filter(ThuongHieu__in=selected_brands)

    # C. Lọc theo Giá
    price_range = request.GET.get('price')
    if price_range:
        if price_range == 'under_100':
            products_list = products_list.filter(DonGia__lt=100000)
        elif price_range == '100_300':
            products_list = products_list.filter(DonGia__range=(100000, 300000))
        elif price_range == '300_500':
            products_list = products_list.filter(DonGia__range=(300000, 500000))
        elif price_range == 'above_500':
            products_list = products_list.filter(DonGia__gt=500000)
    
    paginator = Paginator(products_list, 10) # Show 10 products per page.
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)


    # Context bắn sang HTML
    context = {
        'danh_muc': danh_muc_hien_tai,
        'products': products,
        'all_brands': all_brands, # Để hiển thị checkbox thương hiệu
        'selected_brands': selected_brands, # Để giữ trạng thái tích chọn
        'selected_price': price_range,
    }
    
    return render(request, 'category_detail.html', context)
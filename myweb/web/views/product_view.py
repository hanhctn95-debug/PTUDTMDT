from django.shortcuts import render, get_object_or_404, redirect
from ..models import SanPham, SanPham_ThuocTinh, DanhGia, TaiKhoan
from django.contrib import messages


from django.urls import reverse
from django.http import HttpResponseRedirect
def detail(request, product_id):
    product = get_object_or_404(SanPham, pk=product_id)
    
    # --- XỬ LÝ POST: KHI NGƯỜI DÙNG BẤM GỬI ĐÁNH GIÁ ---
    # Tìm đến đoạn xử lý POST trong hàm detail
    if request.method == 'POST':
        # 1. Kiểm tra session thay vì request.user
        if 'khach_hang_id' not in request.session:
            return redirect('web:login')
            
        try:
            rating = int(request.POST.get('rate'))
            content = request.POST.get('content')
            
            # 2. Lấy ID khách hàng từ Session
            kh_id = request.session['khach_hang_id']
            khach_hang = TaiKhoan.objects.get(pk=kh_id)
            
            # 3. Lưu đánh giá
            DanhGia.objects.create(
                SanPham=product,
                TaiKhoan=khach_hang,
                Diem=rating,
                NoiDung=content
            )
            messages.success(request, 'Đánh giá thành công!')
            
        except Exception as e:
            print(f"Lỗi: {e}")
            messages.error(request, 'Có lỗi xảy ra.')
            
        url = reverse('web:product_detail', args=[product_id])
        return HttpResponseRedirect(url + '#reviewSection')

    # --- XỬ LÝ GET: HIỂN THỊ TRANG ---
    images = product.hinhanhs.all()
    attributes = SanPham_ThuocTinh.objects.filter(SanPham=product).select_related('ThuocTinh')
    related_products = SanPham.objects.filter(DanhMuc=product.DanhMuc).exclude(id=product.id).prefetch_related('hinhanhs')[:5]
    reviews = product.reviews.all().order_by('-id')

    context = {
        'product': product,
        'images': images,
        'attributes': attributes,
        'related_products': related_products,
        'reviews': reviews,
    }
    
    return render(request, 'product_detail.html', context)
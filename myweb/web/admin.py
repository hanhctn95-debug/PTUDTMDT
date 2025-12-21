from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import (
    DanhMuc, LoaiThuocTinh, PhuongThucThanhToan, GiamGia, KhuyenMai,
    TaiKhoan, DiaChi, SanPham, HinhAnh, SanPham_ThuocTinh, SanPham_KhuyenMai,
    GioHang, ChiTietGioHang, DonHang, ChiTietDonHang, DanhGia, BaoCaoThongKe
)

# =============================================================
# 1. CÁC DANH MỤC TỪ ĐIỂN (LOOKUP MODELS)
# =============================================================

@admin.register(DanhMuc)
class DanhMucAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenDanhMuc')

@admin.register(LoaiThuocTinh)
class LoaiThuocTinhAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenThuocTinh', 'DonViTinh')
    search_fields = ('TenThuocTinh',)

@admin.register(PhuongThucThanhToan)
class PhuongThucThanhToanAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenPTTT',)

@admin.register(GiamGia)
class GiamGiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'MaGiamGia', 'GiaTriGiam', 'TGbatDau', 'TGKetThuc')
    list_filter = ('TGKetThuc',)

@admin.register(KhuyenMai)
class KhuyenMaiAdmin(admin.ModelAdmin):
    list_display = ('id', 'LoaiGiamGia', 'GiaTri', 'NgayBatDau', 'NgayKetThuc')
    list_filter = ('LoaiGiamGia',)

# =============================================================
# 2. NGƯỜI DÙNG (USER MODELS)
# =============================================================

@admin.register(TaiKhoan)
class TaiKhoanAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenKhachHang', 'Email', 'SDT', 'HangThanhVien')
    search_fields = ('TenKhachHang', 'Email', 'SDT')

@admin.register(DiaChi)
class DiaChiAdmin(admin.ModelAdmin):
    list_display = ('id', 'TaiKhoan', 'Tinh_Thanh_Pho', 'Phuong_Xa', 'ChiTietDiaChi', 'MacDinh')
    list_filter = ('Tinh_Thanh_Pho',)
    search_fields = ('TaiKhoan__TenKhachHang', 'SDTLienHe')

# =============================================================
# 3. SẢN PHẨM (PRODUCT MANAGEMENT)
# =============================================================

class HinhAnhInline(admin.TabularInline):
    model = HinhAnh
    extra = 1
    # Thêm các trường để hiển thị ảnh preview
    readonly_fields = ('image_preview',)
    fields = ('Anh', 'image_preview')

    def image_preview(self, obj):
        if obj.Anh:
            return format_html('<img src="{}" width="150" height="auto" />', obj.Anh.url)
        return "(Chưa có ảnh)"
    image_preview.short_description = "Xem trước"

class SanPhamThuocTinhInline(admin.TabularInline):
    model = SanPham_ThuocTinh
    extra = 1

class SanPhamKhuyenMaiInline(admin.TabularInline):
    model = SanPham_KhuyenMai
    extra = 1
    verbose_name = "Chương trình khuyến mãi"
    verbose_name_plural = "Áp dụng khuyến mãi"

# --- MAIN ADMIN (Chỉ đăng ký Sản phẩm, các bảng con nằm bên trong) ---
@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ('id', 'TenSanPham', 'DanhMuc', 'DonGia', 'SoLuongTonKho')
    list_filter = ('DanhMuc', 'ThuongHieu')
    search_fields = ('TenSanPham',)
    prepopulated_fields = {'Slug': ('TenSanPham',)}
    
    # Nhúng 3 bảng con vào đây để quản lý tập trung
    inlines = [HinhAnhInline, SanPhamThuocTinhInline, SanPhamKhuyenMaiInline]

# =============================================================
# 4. GIỎ HÀNG & ĐƠN HÀNG (ORDER MANAGEMENT)
# =============================================================



class ChiTietDonHangInline(admin.TabularInline):
    model = ChiTietDonHang
    extra = 0
    readonly_fields = ('DonGiaTaiThoiDiemMua',) # Giá lúc mua không được sửa
    can_delete = False # Không cho xóa chi tiết đơn hàng (để bảo toàn lịch sử)

@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = ('id', 'TaiKhoan', 'TongTien', 'trangThaiGH', 'NgayDat')
    list_filter = ('trangThaiGH', 'NgayDat')
    search_fields = ('id', 'TaiKhoan__TenKhachHang')
    
    inlines = [ChiTietDonHangInline] # Quản lý chi tiết đơn hàng ngay trong Đơn hàng

# =============================================================
# 5. ĐÁNH GIÁ (REVIEWS)
# =============================================================

@admin.register(DanhGia)
class DanhGiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'SanPham', 'TaiKhoan', 'Diem', 'NoiDung')
    list_filter = ('Diem',)
    search_fields = ('SanPham__TenSanPham', 'TaiKhoan__TenKhachHang')


# =============================================================
# 6. ANALYTICS DASHBOARD (DUMMY MODEL ADMIN)
# =============================================================

@admin.register(BaoCaoThongKe)
class BaoCaoThongKeAdmin(admin.ModelAdmin):
    """
    Dummy Admin class to redirect to Analytics Dashboard.
    This creates a link in the admin sidebar that points to our custom analytics view.
    """
    list_display = ('get_analytics_link',)
    list_display_links = None  # Disable default admin links
    
    def has_add_permission(self, request):
        """Hide 'Add' button"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Hide 'Delete' button"""
        return False
    
    def changelist_view(self, request, extra_context=None):
        """
        Override changelist view to redirect to analytics dashboard
        """
        return HttpResponseRedirect(reverse('admin_analytics'))
    
    def get_analytics_link(self, obj):
        """Display a link to open analytics dashboard"""
        url = reverse('admin_analytics')
        return format_html(
            '<a href="{}" style="color: #417690; text-decoration: none; font-weight: bold;">📊 Mở Dashboard Thống Kê</a>',
            url
        )
    get_analytics_link.short_description = 'Báo Cáo Thống Kê'
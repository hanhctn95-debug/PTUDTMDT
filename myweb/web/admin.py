from django.contrib import admin
from .models import (
    DanhMuc, LoaiThuocTinh, PhuongThucThanhToan, GiamGia, KhuyenMai,
    TaiKhoan, DiaChi, SanPham, HinhAnh, SanPham_ThuocTinh, SanPham_KhuyenMai,
    GioHang, ChiTietGioHang, DonHang, ChiTietDonHang, DanhGia
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

# --- INLINES (Các thành phần con của Sản phẩm) ---
class HinhAnhInline(admin.TabularInline):
    model = HinhAnh
    extra = 1

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
    list_display = ('id', 'TaiKhoan', 'TongTien', 'TrangThaiGH', 'NgayDat')
    list_filter = ('TrangThaiGH', 'NgayDat')
    search_fields = ('id', 'TaiKhoan__TenKhachHang')
    
    # Cho phép sửa trạng thái nhanh ngay bên ngoài danh sách (như bạn yêu cầu lúc nãy)
    list_editable = ('TrangThaiGH',) 
    
    inlines = [ChiTietDonHangInline] # Quản lý chi tiết đơn hàng ngay trong Đơn hàng

# =============================================================
# 5. ĐÁNH GIÁ (REVIEWS)
# =============================================================

@admin.register(DanhGia)
class DanhGiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'SanPham', 'TaiKhoan', 'Diem', 'NoiDung')
    list_filter = ('Diem',)
    search_fields = ('SanPham__TenSanPham', 'TaiKhoan__TenKhachHang')
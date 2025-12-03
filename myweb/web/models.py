from django.db import models
from django.utils.text import slugify

# LƯU Ý: Django tự động tạo trường 'id' (PK) cho các Model không định nghĩa khóa chính.

# -------------------------------------------------------------
# 1. LOOKUP MODELS (1-5)
# -------------------------------------------------------------

# [1] Bảng DanhMuc
class DanhMuc(models.Model):
    # DanhMucID (PK)
    TenDanhMuc = models.CharField(max_length=200, unique=True, verbose_name="Tên Danh mục")

    class Meta:
        ordering = ('TenDanhMuc',)
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'

    def __str__(self):
        return self.TenDanhMuc

# [2] Bảng LoaiThuocTinh
class LoaiThuocTinh(models.Model):
    # ThuocTinhID (PK)
    TenThuocTinh = models.CharField(max_length=100, unique=True, verbose_name="Tên Thuộc tính")
    DonViTinh = models.CharField(max_length=50, null=True, blank=True, verbose_name="Đơn vị tính")

    class Meta:
        verbose_name = 'Loại thuộc tính'
        verbose_name_plural = 'Loại thuộc tính'

    def __str__(self):
        return self.TenThuocTinh

# [3] Bảng PhuongThucThanhToan
class PhuongThucThanhToan(models.Model):
    # ThanhToanID (PK)
    TenPTTT = models.CharField(max_length=100, unique=True, verbose_name="Tên PTTT")

    class Meta:
        verbose_name = 'Phương thức thanh toán'
        verbose_name_plural = 'Phương thức thanh toán'

    def __str__(self):
        return self.TenPTTT

# [4] Bảng GiamGia
class GiamGia(models.Model):
    # GiamGiaID (PK)
    MaGiamGia = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    TGbatDau = models.DateTimeField(verbose_name="Thời gian bắt đầu")
    TGKetThuc = models.DateTimeField(verbose_name="Thời gian kết thúc")
    GiaTriGiam = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Giá trị giảm")

    class Meta:
        verbose_name = 'Mã giảm giá'
        verbose_name_plural = 'Mã giảm giá'
        
    def __str__(self):
        return self.MaGiamGia

# [5] Bảng KhuyenMai
class KhuyenMai(models.Model):
    # KhuyenMaiID (PK)
    LoaiGiamGia = models.CharField(max_length=10, 
                                   choices=[('PERCENT', 'Phần trăm (%)'), ('AMOUNT', 'Số tiền cố định (VNĐ)')], 
                                   verbose_name="Loại giảm giá")
                                   
    GiaTri = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Giá trị")
    
    NgayBatDau = models.DateTimeField(verbose_name="Bắt đầu")
    NgayKetThuc = models.DateTimeField(verbose_name="Kết thúc")

    class Meta:
        verbose_name = 'Chương trình khuyến mãi'
        verbose_name_plural = 'Chương trình khuyến mãi'

    def __str__(self):
        if self.LoaiGiamGia == 'PERCENT':
             return f"Giảm {self.GiaTri * 100}%"
        return f"Giảm {self.GiaTri} VNĐ"


# -------------------------------------------------------------
# 6. USER & ADDRESS MODELS
# -------------------------------------------------------------

# [6] Bảng TaiKhoan
class TaiKhoan(models.Model):
    # TaiKhoanID (PK)
    TenKhachHang = models.CharField(max_length=200, verbose_name="Tên khách hàng")
    SDT = models.CharField(max_length=20, null=True, blank=True, verbose_name="Số điện thoại")
    GioiTinh = models.CharField(max_length=10, null=True, blank=True, verbose_name="Giới tính")
    
    Email = models.EmailField(max_length=255, unique=True)
    MatKhau = models.CharField(max_length=255) 
    
    HangThanhVien = models.CharField(max_length=50, null=True, blank=True, verbose_name="Hạng TV")
    NgaySinh = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Tài khoản'
        verbose_name_plural = 'Tài khoản'

    def __str__(self):
        return self.TenKhachHang

# [7] Bảng DiaChi
class DiaChi(models.Model):
    # DiaChiID (PK)
    TaiKhoan = models.ForeignKey(TaiKhoan, 
                                 related_name='diachis', 
                                 on_delete=models.CASCADE, 
                                 verbose_name="Tài khoản")
    
    ChiTietDiaChi = models.CharField(max_length=255, verbose_name="Chi tiết")
    Phuong_Xa = models.CharField(max_length=100)
    Tinh_Thanh_Pho = models.CharField(max_length=100)
    SDTLienHe = models.CharField(max_length=20, null=True, blank=True, verbose_name="SĐT liên hệ")
    MacDinh = models.BooleanField(default=False, verbose_name="Mặc định")
    class Meta:
        verbose_name = 'Địa chỉ'
        verbose_name_plural = 'Địa chỉ'
        
    def __str__(self):
        return f"ĐC của {self.TaiKhoan.TenKhachHang}: {self.ChiTietDiaChi}"


# -------------------------------------------------------------
# 8. BẢNG JUNCTION N:N: SanPham_KhuyenMai
# -------------------------------------------------------------

# [8] Bảng SanPham_KhuyenMai (Bảng trung gian N:N)
class SanPham_KhuyenMai(models.Model):
    # Khóa chính kết hợp (SanPhamID, KhuyenMaiID)
    SanPham = models.ForeignKey('SanPham', on_delete=models.CASCADE)
    KhuyenMai = models.ForeignKey(KhuyenMai, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('SanPham', 'KhuyenMai'),)
        verbose_name = 'Liên kết KM'
        verbose_name_plural = 'Liên kết KM'

    def __str__(self):
        return f'Liên kết {self.SanPham_id} <-> {self.KhuyenMai_id}'


# -------------------------------------------------------------
# 9. PRODUCT CORE MODEL
# -------------------------------------------------------------

# [9] Bảng SanPham
class SanPham(models.Model):
    # SanPhamID (PK)
    DanhMuc = models.ForeignKey(DanhMuc, 
                                related_name='sanphams', 
                                on_delete=models.PROTECT, 
                                verbose_name="Danh mục")
    
    TenSanPham = models.CharField(max_length=255, db_index=True, verbose_name="Tên Sản phẩm")
    Slug = models.SlugField(max_length=255, unique=True, blank=True)
    DonGia = models.DecimalField(max_digits=15, decimal_places=2)
    SoLuongTonKho = models.IntegerField(default=0, verbose_name="Tồn kho")
    MoTa = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    ThuongHieu = models.CharField(max_length=255, null=True, blank=True, verbose_name="Thương hiệu")
    
    # Mối quan hệ N:N sử dụng bảng trung gian đã định nghĩa (through)
    khuyen_mai = models.ManyToManyField(KhuyenMai, 
                                        through='SanPham_KhuyenMai', 
                                        related_name='sanphams_ap_dung',
                                        verbose_name="Chương trình khuyến mãi")

    class Meta:
        ordering = ('TenSanPham',)
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'

    def save(self, *args, **kwargs):
        if not self.Slug:
            self.Slug = slugify(self.TenSanPham)
        super(SanPham, self).save(*args, **kwargs)

    def __str__(self):
        return self.TenSanPham
    
    def get_discounted_price(self):
        """
        Hàm tính giá sau khi giảm. 
        Trả về: (Giá mới, Phần trăm giảm, Giá trị giảm)
        """
        from django.utils import timezone
        now = timezone.now()
        
        # Lấy khuyến mãi đang chạy (Ngày bắt đầu <= Hiện tại <= Ngày kết thúc)
        # Sắp xếp lấy cái giảm nhiều nhất trước (nếu có nhiều KM)
        active_promotions = self.khuyen_mai.filter(
            NgayBatDau__lte=now, 
            NgayKetThuc__gte=now
        ).order_by('-GiaTri')

        if active_promotions.exists():
            km = active_promotions.first()
            if km.LoaiGiamGia == 'PERCENT':
                discount_amount = self.DonGia * km.GiaTri # GiaTri lưu 0.1 (10%)
                new_price = self.DonGia - discount_amount
                return new_price, km.GiaTri * 100, discount_amount
            else:
                # Giảm tiền mặt
                new_price = self.DonGia - km.GiaTri
                return new_price, 0, km.GiaTri
                
        return self.DonGia, 0, 0


# -------------------------------------------------------------
# 10. DYNAMIC ATTRIBUTE MODEL
# -------------------------------------------------------------

# [10] BẢNG JUNCTION EAV: SanPham_ThuocTinh
class SanPham_ThuocTinh(models.Model):
    SanPham = models.ForeignKey(SanPham, related_name='thuoc_tinh', on_delete=models.CASCADE) 
    ThuocTinh = models.ForeignKey(LoaiThuocTinh, on_delete=models.CASCADE)
    GiaTriThuocTinh = models.CharField(max_length=255, verbose_name="Giá trị")

    class Meta:
        unique_together = (('SanPham', 'ThuocTinh'),) 
        verbose_name = 'Thuộc tính SP'
        verbose_name_plural = 'Thuộc tính SP'
    
    def __str__(self):
        return f"{self.SanPham.TenSanPham} - {self.ThuocTinh.TenThuocTinh}: {self.GiaTriThuocTinh}"


# -------------------------------------------------------------
# 11. IMAGE MODEL
# -------------------------------------------------------------

# [11] Bảng HinhAnh
class HinhAnh(models.Model):
    # HinhAnhID (PK)
    SanPham = models.ForeignKey(SanPham, related_name='hinhanhs', on_delete=models.CASCADE, verbose_name="Sản phẩm")
    Anh = models.CharField(max_length=255, verbose_name="Đường dẫn ảnh")
    
    class Meta:
        verbose_name = 'Hình ảnh'
        verbose_name_plural = 'Hình ảnh'

    def __str__(self):
        return f"Ảnh của {self.SanPham.TenSanPham}"


# -------------------------------------------------------------
# 12. CART MODELS
# -------------------------------------------------------------

# [12] Bảng GioHang
class GioHang(models.Model):
    # GioHangID (PK)
    TaiKhoan = models.OneToOneField(TaiKhoan, 
                                    related_name='giohang', 
                                    on_delete=models.CASCADE, 
                                    null=True, blank=True, 
                                    verbose_name="Tài khoản") 

    class Meta:
        verbose_name = 'Giỏ hàng'
        verbose_name_plural = 'Giỏ hàng'

    def __str__(self):
        return f"Giỏ hàng của {self.TaiKhoan.TenKhachHang if self.TaiKhoan else 'Khách vãng lai'}"

# -------------------------------------------------------------
# 13. CART ITEM MODEL
# -------------------------------------------------------------

# [13] Bảng ChiTietGioHang
class ChiTietGioHang(models.Model):
    # Khóa chính kết hợp (GioHangID, SanPhamID)
    GioHang = models.ForeignKey(GioHang, related_name='items', on_delete=models.CASCADE)
    SanPham = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    SoLuong = models.IntegerField()

    class Meta:
        unique_together = (('GioHang', 'SanPham'),)
        verbose_name = 'Chi tiết giỏ hàng'
        verbose_name_plural = 'Chi tiết giỏ hàng'

    def __str__(self):
        return f"{self.SoLuong} x {self.SanPham.TenSanPham}"


# -------------------------------------------------------------
# 14. ORDER MODEL
# -------------------------------------------------------------

# [14] Bảng DonHang
class DonHang(models.Model):
    # DonHangID (PK)
    TaiKhoan = models.ForeignKey(TaiKhoan, 
                                 on_delete=models.SET_NULL, 
                                 null=True, blank=True, 
                                 verbose_name="Tài khoản")
    ThanhToan = models.ForeignKey(PhuongThucThanhToan, on_delete=models.PROTECT)
    GiamGia = models.ForeignKey(GiamGia, on_delete=models.SET_NULL, null=True, blank=True)
    DiaChi = models.ForeignKey(DiaChi, on_delete=models.PROTECT, verbose_name="Địa chỉ giao hàng")
    
    NgayDat = models.DateTimeField(auto_now_add=True)
    TRANG_THAI_CHOICES = [
        ('Chờ xử lý', 'Chờ xử lý'),
        ('Đang giao', 'Đang giao'), # Đã đổi thành 'Đang giao' theo ý bạn
        ('Đã giao', 'Đã giao'),
        ('Hủy', 'Hủy'),
    ]

    # 2. Thêm choices vào trường này
    TrangThaiGH = models.CharField(
        max_length=50, 
        choices=TRANG_THAI_CHOICES, # <--- QUAN TRỌNG
        default='Chờ xử lý',        # Mặc định khi mới đặt
        verbose_name="Trạng thái"
    )
    TongTien = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        ordering = ('-NgayDat',)
        verbose_name = 'Đơn hàng'
        verbose_name_plural = 'Đơn hàng'
    
    def __str__(self):
        return f"Đơn hàng #{self.id} ({self.TaiKhoan.TenKhachHang if self.TaiKhoan else 'Vãng lai'})"


# -------------------------------------------------------------
# 15. ORDER ITEM MODEL
# -------------------------------------------------------------

# [15] Bảng ChiTietDonHang
class ChiTietDonHang(models.Model):
    # Khóa chính kết hợp (DonHangID, SanPhamID)
    DonHang = models.ForeignKey(DonHang, related_name='items', on_delete=models.CASCADE)
    SanPham = models.ForeignKey(SanPham, on_delete=models.PROTECT)
    SoLuong = models.IntegerField()
    DonGiaTaiThoiDiemMua = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = (('DonHang', 'SanPham'),)
        verbose_name = 'Chi tiết đơn hàng'
        verbose_name_plural = 'Chi tiết đơn hàng'

    def __str__(self):
        return f"Chi tiết DH #{self.DonHang.id}"

# -------------------------------------------------------------
# 16. REVIEW MODEL
# -------------------------------------------------------------

# [16] Bảng DanhGia
class DanhGia(models.Model):
    # DanhGiaID (PK)
    SanPham = models.ForeignKey(SanPham, related_name='reviews', on_delete=models.CASCADE)
    TaiKhoan = models.ForeignKey(TaiKhoan, on_delete=models.CASCADE)
    NoiDung = models.TextField(null=True, blank=True)
    Diem = models.IntegerField(verbose_name="Điểm đánh giá") 
    
    class Meta:
        verbose_name = 'Đánh giá'
        verbose_name_plural = 'Đánh giá'

    def __str__(self):
        return f"Đánh giá {self.Diem} sao của {self.TaiKhoan.TenKhachHang}"

# Create your models here.

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncDay, TruncDate
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import json
import pytz

from ..models import DonHang, ChiTietDonHang, SanPham

# =========================================================================
# HELPER FUNCTIONS
# =========================================================================

def remove_vietnamese_diacritics(text):
    """
    Remove Vietnamese diacritics and convert to ASCII
    Example: 'Báo Cáo' -> 'Bao Cao'
    """
    if not text:
        return text
    
    # Vietnamese character mapping
    vietnamese_chars = {
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd',
        'Á': 'A', 'À': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ắ': 'A', 'Ằ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ấ': 'A', 'Ầ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'É': 'E', 'È': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ế': 'E', 'Ề': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Í': 'I', 'Ì': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ó': 'O', 'Ò': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ố': 'O', 'Ồ': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ớ': 'O', 'Ờ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ú': 'U', 'Ù': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ứ': 'U', 'Ừ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ý': 'Y', 'Ỳ': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        'Đ': 'D',
    }
    
    result = ''
    for char in text:
        result += vietnamese_chars.get(char, char)
    
    return result


def get_date_range(request):
    """
    Extract start_date and end_date from GET request.
    Default: Current month (1st to Today)
    """
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    start_date_str = request.GET.get('start_date', first_day_of_month.isoformat())
    end_date_str = request.GET.get('end_date', today.isoformat())
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        start_date = first_day_of_month
        end_date = today
    
    return start_date, end_date


def get_revenue_data(start_date, end_date):
    """
    Query 1: Revenue by Day
    Filters DonHang (Status='Đã giao', Date range)
    Returns: List of dicts with date and total_revenue
    """
    revenue_data = DonHang.objects.filter(
        trangThaiGH='Đã giao',
        NgayDat__date__gte=start_date,
        NgayDat__date__lte=end_date
    ).annotate(
        date=TruncDate('NgayDat')
    ).values('date').annotate(
        total_revenue=Sum('TongTien')
    ).order_by('date')

    # Convert Decimal to float
    result = []
    for item in revenue_data:
        result.append({
            'date': item['date'],
            'total_revenue': float(item['total_revenue']) if item['total_revenue'] else 0
        })
    
    return result


def get_sales_volume_data(start_date, end_date):
    """
    Query 2: Sales Volume by Day
    Filters ChiTietDonHang via DonHang (Status='Đã giao', Date range)
    Returns: List of dicts with date and total_quantity
    """
    sales_data = ChiTietDonHang.objects.filter(
        DonHang__trangThaiGH='Đã giao',
        DonHang__NgayDat__date__gte=start_date,
        DonHang__NgayDat__date__lte=end_date
    ).annotate(
        date=TruncDate('DonHang__NgayDat')
    ).values('date').annotate(
        total_quantity=Sum('SoLuong')
    ).order_by('date')
    
    return list(sales_data)


def get_low_stock_products():
    """
    Query 3: Low Stock Products
    Filter SanPham where SoLuongTonKho < 15
    Returns: List of dicts with product names without diacritics
    """
    products = SanPham.objects.filter(
        SoLuongTonKho__lt=15
    ).select_related('DanhMuc').order_by('SoLuongTonKho').values(
        'id', 'TenSanPham', 'DonGia', 'SoLuongTonKho', 'DanhMuc__TenDanhMuc'
    )
    
    result = []
    for product in products:
        result.append({
            'id': product['id'],
            'TenSanPham': remove_vietnamese_diacritics(product['TenSanPham']),
            'DonGia': float(product['DonGia']) if product['DonGia'] else 0,
            'SoLuongTonKho': product['SoLuongTonKho'],
            'DanhMuc__TenDanhMuc': remove_vietnamese_diacritics(product['DanhMuc__TenDanhMuc']) if product['DanhMuc__TenDanhMuc'] else ''
        })
    
    return result


def get_best_sellers(start_date, end_date, limit=10):
    """
    Query 4: Best Sellers
    Filter ChiTietDonHang (Date range)
    Group by SanPham, annotate sum SoLuong
    Returns: Top 10 products by quantity sold
    """
    best_sellers = ChiTietDonHang.objects.filter(
        DonHang__trangThaiGH='Đã giao',
        DonHang__NgayDat__date__gte=start_date,
        DonHang__NgayDat__date__lte=end_date
    ).values(
        'SanPham__id',
        'SanPham__TenSanPham',
        'SanPham__DonGia',
        'SanPham__DanhMuc__TenDanhMuc'
    ).annotate(
        total_sold=Sum('SoLuong'),
        total_revenue=Sum(F('SoLuong') * F('DonGiaTaiThoiDiemMua'), output_field=DecimalField())
    ).order_by('-total_sold')[:limit]
    
    # Convert Decimal to float for template rendering
    result = []
    for item in best_sellers:
        result.append({
            'SanPham__id': item['SanPham__id'],
            'SanPham__TenSanPham': remove_vietnamese_diacritics(item['SanPham__TenSanPham']),
            'SanPham__DonGia': float(item['SanPham__DonGia']) if item['SanPham__DonGia'] else 0,
            'SanPham__DanhMuc__TenDanhMuc': remove_vietnamese_diacritics(item['SanPham__DanhMuc__TenDanhMuc']) if item['SanPham__DanhMuc__TenDanhMuc'] else '',
            'total_sold': item['total_sold'] or 0,
            'total_revenue': float(item['total_revenue']) if item['total_revenue'] else 0,
        })
    
    return result


def serialize_for_charts(revenue_data, sales_data):
    """
    Convert queryset results to JSON-friendly format for Chart.js
    """
    # Revenue Chart Data
    revenue_dates = [item['date'].strftime('%d/%m/%Y') for item in revenue_data]
    revenue_values = [float(item['total_revenue'] or 0) for item in revenue_data]
    
    # Sales Chart Data
    sales_dates = [item['date'].strftime('%d/%m/%Y') for item in sales_data]
    sales_values = [int(item['total_quantity'] or 0) for item in sales_data]
    
    # Format values to ensure proper JSON serialization
    def format_decimal(value):
        """Convert Decimal to float safely"""
        if value is None:
            return 0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0
    
    revenue_values = [format_decimal(v) for v in revenue_values]
    
    return {
        'revenue_chart': json.dumps({
            'labels': revenue_dates,
            'data': revenue_values
        }),
        'sales_chart': json.dumps({
            'labels': sales_dates,
            'data': sales_values
        })
    }


# =========================================================================
# MAIN ANALYTICS VIEW
# =========================================================================

@staff_member_required
@require_http_methods(["GET"])
def admin_analytics(request):
    """
    Main Analytics Dashboard View
    Accessible only to staff members
    """
    # Get date range from request
    start_date, end_date = get_date_range(request)
    
    # Query all data
    revenue_data = get_revenue_data(start_date, end_date)
    sales_data = get_sales_volume_data(start_date, end_date)
    low_stock_products = get_low_stock_products()
    best_sellers = get_best_sellers(start_date, end_date)
    
    # Calculate KPIs
    total_revenue = sum(float(item['total_revenue'] or 0) for item in revenue_data)
    total_sales_volume = sum(item['total_quantity'] or 0 for item in sales_data)
    total_orders = DonHang.objects.filter(
        trangThaiGH='Đã giao',
        NgayDat__date__gte=start_date,
        NgayDat__date__lte=end_date
    ).count()
    
    # Serialize data for Chart.js
    charts_data = serialize_for_charts(revenue_data, sales_data)
    
    context = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_revenue': total_revenue,
        'total_sales_volume': total_sales_volume,
        'total_orders': total_orders,
        'revenue_data': revenue_data,
        'sales_data': sales_data,
        'low_stock_products': low_stock_products,
        'best_sellers': best_sellers,
        'revenue_chart_json': charts_data['revenue_chart'],
        'sales_chart_json': charts_data['sales_chart'],
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)


# =========================================================================
# PDF EXPORT VIEW
# =========================================================================

@staff_member_required
@require_http_methods(["GET"])
def export_analytics_pdf(request, report_type):
    """
    Generate PDF report based on report_type
    report_type: 'revenue', 'sales', 'inventory', 'best_sellers'
    """
    from io import BytesIO
    from xhtml2pdf import pisa
    
    start_date, end_date = get_date_range(request)
    
    # Prepare data based on report type
    if report_type == 'revenue':
        data = get_revenue_data(start_date, end_date)
        title = 'Bao cao Doanh Thu'
    elif report_type == 'sales':
        data = get_sales_volume_data(start_date, end_date)
        title = 'Bao cao Doanh So'
    elif report_type == 'inventory':
        data = get_low_stock_products()
        title = 'Bao cao Ton Kho Thap'
    elif report_type == 'best_sellers':
        data = get_best_sellers(start_date, end_date, limit=None)
        title = 'Bao cao San Pham Ban Chay'
    else:
        return HttpResponse('Invalid report type', status=400)
    
    context = {
        'report_type': report_type,
        'title': title,
        'start_date': start_date,
        'end_date': end_date,
        'data': data,
        'shop_name': 'VPP Shop',
        'report_date': timezone.now().astimezone(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y %H:%M')
    }
    
    html = render(request, 'admin/report_pdf.html', context).content.decode('utf-8')
    
    # Generate PDF
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, result)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    
    result.seek(0)
    response = HttpResponse(result.read(), content_type='application/pdf')
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_{report_type}_{timezone.now().astimezone(vietnam_tz).strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response

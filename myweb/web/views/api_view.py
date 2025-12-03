from django.http import JsonResponse
from django.utils import timezone
from ..models import GiamGia

def check_coupon(request):
    code = request.GET.get('code')
    now = timezone.now()
    try:
        coupon = GiamGia.objects.get(MaGiamGia=code)
        if coupon.TGbatDau <= now <= coupon.TGKetThuc:
            return JsonResponse({
                'valid': True, 
                'message': 'Áp dụng thành công!', 
                'value': float(coupon.GiaTriGiam), 
                'type': 'AMOUNT' # Giả định giảm tiền cố định
            })
        return JsonResponse({'valid': False, 'message': 'Mã đã hết hạn'})
    except GiamGia.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Mã không tồn tại'})
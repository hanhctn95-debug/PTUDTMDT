from django.urls import path
# Import file home_view.py từ thư mục views
from .views import home_view, category_view, product_view, auth_view, profile_view, cart_view, checkout_view, api_view, analytics_view

app_name = 'web'

urlpatterns = [
    # Gọi hàm 'index' nằm trong file 'home_view.py'
    path('', home_view.index, name='home'),
    path('danh-muc/<int:danh_muc_id>/', category_view.view_category, name='category_detail'),
    path('san-pham/<int:product_id>/', product_view.detail, name='product_detail'),
    path('dang-nhap/', auth_view.login_view, name='login'),
    path('dang-xuat/', auth_view.logout_view, name='logout'),
    path('dang-ky/', auth_view.register_view, name='register'),
    path('tai-khoan/thong-tin/', profile_view.profile_info, name='profile_info'),
    path('tai-khoan/hang-thanh-vien/', profile_view.membership, name='profile_membership'),
    path('tai-khoan/don-hang/', profile_view.order_history, name='profile_orders'),
    path('gio-hang/', cart_view.view_cart, name='view_cart'),
    

    path('them-vao-gio/<int:product_id>/', cart_view.add_to_cart, name='add_to_cart'),
    
    path('xoa-khoi-gio/<int:item_id>/', cart_view.remove_from_cart, name='remove_from_cart'),
    path('cap-nhat-so-luong-gio-hang/', cart_view.update_cart_quantity, name='update_cart_quantity'),
    path('tai-khoan/dia-chi/', profile_view.address_book, name='profile_addresses'),
    path('tai-khoan/dia-chi/mac-dinh/<int:address_id>/', profile_view.set_default_address, name='set_default_address'),
    path('tai-khoan/dia-chi/xoa/<int:address_id>/', profile_view.delete_address, name='delete_address'),
    path('tai-khoan/dia-chi/sua/<int:address_id>/', profile_view.edit_address, name='edit_address'),path('thanh-toan/', checkout_view.checkout, name='checkout'),
    path('thanh-toan/', checkout_view.checkout, name='checkout'),
    path('dat-hang-thanh-cong/', checkout_view.order_success, name='order_success'),
    path('api/check-coupon/', api_view.check_coupon, name='check_coupon'),
    path('tai-khoan/don-hang/<int:order_id>/', profile_view.order_detail, name='order_detail'),
]
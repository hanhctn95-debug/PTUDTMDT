"""
URL configuration for myweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from web.views import analytics_view

# Customize admin site title
admin.site.site_header = "VPP Shop - Quản Lý Admin"
admin.site.site_title = "VPP Shop Admin"
admin.site.index_title = "Chào mừng đến Dashboard Quản Lý"

urlpatterns = [
    # Analytics URLs (MUST be before admin.site.urls!)
    path('admin/analytics/', analytics_view.admin_analytics, name='admin_analytics'),
    path('admin/export-pdf/<str:report_type>/', analytics_view.export_analytics_pdf, name='export_analytics_pdf'),
    path('admin/', admin.site.urls),
    path('', include('web.urls')), # <== Include web app URLs
]

# Cấu hình Media/Static cho môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # The static() helper is for development only and works with STATIC_ROOT.
    # Your settings use STATICFILES_DIRS, which is handled automatically by the runserver.
    # The line below is often not needed if you use STATICFILES_DIRS correctly.
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

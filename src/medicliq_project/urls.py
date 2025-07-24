# medicliq_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('database/', include('medicliq_database.urls')),  # Root URL pointing to medicliq_database
    path('payment/', include('medicliq_payment.src.urls')),  # Include payment URLs
    path("i18n/", include("django.conf.urls.i18n")),  # Django's built-in i18n URL
]+static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])


# medicliq_database/urls.py

from django.urls import path
from . import views
from django.conf.urls.i18n import i18n_patterns
from .views import set_language


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('p_method/',views.p_method,name='p_method'),
    path('upload_prescription/', views.upload_prescription, name='upload_prescription'),
    path('save_prescription/', views.save_prescription, name='save_prescription'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('language/', views.language_selection, name='language_selection'),
    path('set_language/', views.set_language, name='set_language'),
    path('prescription/', views.prescription_image, name='prescription_image'),
    path('selectmedicine/', views.select_medicine, name='selectmedicine'),
    path('upload_from_scanner/', views.handle_scanner_upload, name='upload_from_scanner'),
    path('generate_qr/', views.generate_qr, name='generate_qr'),
    path('mobile_upload/', views.qr_upload_page, name='mobile_upload'),
    path('handle_mobile_upload/', views.handle_mobile_upload, name='handle_mobile_upload'),
    path('upload_status/', views.upload_status, name='upload_status'),
    path('check_upload/', views.check_upload, name='check_upload'),
    path('scanner_instructions/', views.scanner_instructions, name='scanner_instructions'),
    path('scan_image/', views.scan_image, name='scan_image'),



    # Remove the cart URL pattern
    path('login/', views.custom_login, name='login'),
    
     
]
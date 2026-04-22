from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('booking/', views.booking_view, name='booking'),
    path('appointments/', views.appointments_view, name='appointments'),
    path("appointments/<int:appointment_id>/delete/", views.delete_appointment, name="delete_appointment"),

    # mascotas
    path('register-pet/', views.register_pet_view, name='register_pet'),
    path('pet/<int:pet_id>/edit/', views.edit_pet, name='edit_pet'),
    path('pet/<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
    path('pet/<int:pet_id>/', views.pet_detail_view, name='pet_detail'),

    path('documents/', views.documents_view, name='documents'),
    path('services-schedules/', views.services_schedules_view, name='services_schedules'),

    # perfil
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/avatar/', views.update_avatar, name='update_avatar'),

    # contraseña
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="booking/change_password.html",
            success_url=reverse_lazy("profile"),
        ),
        name="change_password",
    ),
    path(
        "change-password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="booking/change_password_done.html"
        ),
        name="password_change_done",
    ),
    
    path('historial/', views.medical_history_view, name='medical_history'),
    path('historial/consulta/<int:consultation_id>/pdf/', views.export_consultation_pdf, name='export_consultation_pdf'),
    path('historial/receta/<int:prescription_id>/pdf/', views.export_prescription_pdf, name='export_prescription_pdf'),
    path('veterinarios/', views.veterinarians_view, name='veterinarians'),
    path('api/vets-by-service/<int:service_id>/', views.vets_by_service, name='vets_by_service'),
    path('api/all-vets/', views.all_vets, name='all_vets'),
]
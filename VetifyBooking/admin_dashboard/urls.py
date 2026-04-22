from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    # Dashboard principal
    path('', views.dashboard_view, name='dashboard'),

    # Gestión de citas
    path('appointments/', views.appointments_view, name='appointments'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/<int:appointment_id>/status/', views.change_appointment_status, name='change_appointment_status'),
    path('appointments/create/', views.create_appointment_admin, name='create_appointment_admin'),

    # Gestión de usuarios
    path('users/', views.users_view, name='users'),
    path('users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('users/create/', views.create_user_view, name='create_user'),
    path('register/', views.admin_register_view, name='admin_register'),
    path('profile/', views.admin_profile_view, name='admin_profile'),

    # Gestión de mascotas
    path('pets/', views.pets_view, name='pets'),
    path('pets/delete/<int:pet_id>/', views.delete_pet, name='delete_pet'),
    path('pets/create/', views.create_pet, name='create_pet'),
    path('pets/<int:pet_id>/vaccines/', views.pet_vaccines_view, name='pet_vaccines'),
    path('vaccines/<int:vaccine_id>/delete/', views.delete_vaccine_view, name='delete_vaccine'),

    # Gestión de veterinarios
    path('veterinarians/', views.veterinarians_view, name='veterinarians'),
    path('veterinarians/toggle/<int:vet_id>/', views.toggle_vet_status, name='toggle_vet_status'),
    path('veterinarians/add/', views.add_veterinarian, name='add_veterinarian'),
    path('veterinarians/<int:vet_id>/edit/', views.edit_veterinarian_view, name='edit_veterinarian'),

    # Gestión de servicios
    path('services/', views.services_view, name='services'),
    path('services/toggle/<int:service_id>/', views.toggle_service_status, name='toggle_service_status'),
    path('services/create/', views.create_service_view, name='create_service'),
    path('services/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),

    # Horarios
    path('schedules/create/', views.create_schedule_view, name='create_schedule'),
    path('schedules/<int:schedule_id>/edit/', views.edit_schedule_view, name='edit_schedule'),
    path('schedules/', views.schedules_view, name='schedules'),

    # Reportes
    path('reports/', views.reports_view, name='reports'),

    #Documentos
    path('documents/', views.upload_document_view, name='upload_document'),
    path('documents/delete/<int:document_id>/', views.delete_document_view, name='delete_document'),
    path('documents/toggle/<int:document_id>/', views.toggle_document_status_view, name='toggle_document'),

    # Consultas y Recetas
    path('consultations/', views.consultations_view, name='consultations'),
    path('consultations/add/', views.add_consultation_view, name='add_consultation'),
    path('consultations/<int:consultation_id>/edit/', views.edit_consultation_view, name='edit_consultation'),
    path('consultations/<int:consultation_id>/delete/', views.delete_consultation_view, name='delete_consultation'),
    path('consultations/<int:consultation_id>/prescription/add/', views.add_prescription_view, name='add_prescription'),
    path('prescriptions/<int:prescription_id>/edit/', views.edit_prescription_view, name='edit_prescription'),
    path('prescriptions/<int:prescription_id>/delete/', views.delete_prescription_view, name='delete_prescription'),

]

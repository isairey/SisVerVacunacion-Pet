from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth.models import User
from booking.models import Appointment, Pet, Service, Veterinarian, ClinicSchedule
from .decorators import admin_required
import json
from django.contrib.auth import update_session_auth_hash


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def admin_login_view(request):
    """Vista de login exclusiva para administradores"""
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard:dashboard')
        else:
            messages.error(request, 'Credenciales inválidas o no tienes permisos de administrador')
    
    return render(request, 'admin_dashboard/login.html')


@admin_required
def dashboard_view(request):
    """Vista principal del dashboard con estadísticas"""
    
    # KPIs generales
    total_appointments = Appointment.objects.count()
    total_users = User.objects.filter(is_superuser=False).count()
    total_pets = Pet.objects.count()
    total_vets = Veterinarian.objects.filter(is_active=True).count()
    
    # Citas de hoy
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(date=today).count()
    
    # Citas pendientes (futuras)
    pending_appointments = Appointment.objects.filter(date__gte=today).count()
    
    # Estadísticas de los últimos 7 días
    last_7_days = today - timedelta(days=7)
    recent_appointments = Appointment.objects.filter(date__gte=last_7_days)
    
    # Datos para gráfica de citas por día (últimos 7 días)
    appointments_by_day = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Appointment.objects.filter(date=day).count()
        appointments_by_day.append({
            'date': day.strftime('%d/%m'),
            'count': count
        })
    
    # Mascotas por tipo
    pets_by_type = Pet.objects.values('pet_type').annotate(count=Count('id'))
    
    # Servicios más solicitados
    top_services = Service.objects.filter(is_active=True)[:5]
    
    # Últimas citas registradas
    latest_appointments = Appointment.objects.select_related('user').order_by('-created_at')[:10]
    
    # Veterinarios activos
    active_vets = Veterinarian.objects.filter(is_active=True)[:5]
    
    context = {
        'total_appointments': total_appointments,
        'total_users': total_users,
        'total_pets': total_pets,
        'total_vets': total_vets,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'appointments_by_day': json.dumps(appointments_by_day),
        'pets_by_type': pets_by_type,
        'top_services': top_services,
        'latest_appointments': latest_appointments,
        'active_vets': active_vets,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)

@admin_required
def appointments_view(request):
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date', '')
    search = request.GET.get('search', '')

    appointments = Appointment.objects.select_related('user', 'pet').order_by('-date', '-time')

    if status_filter == 'today':
        appointments = appointments.filter(date=timezone.now().date())
    elif status_filter == 'upcoming':
        appointments = appointments.filter(date__gte=timezone.now().date())
    elif status_filter == 'past':
        appointments = appointments.filter(date__lt=timezone.now().date())
    elif status_filter in ['pending', 'confirmed', 'completed', 'cancelled']:
        appointments = appointments.filter(status=status_filter)

    if date_filter:
        appointments = appointments.filter(date=date_filter)

    if search:
        appointments = appointments.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(pet__name__icontains=search)
        )

    # Para el modal de crear cita
    from django.contrib.auth.models import User
    users = User.objects.filter(is_superuser=False).order_by('username')
    pets = Pet.objects.select_related('owner').order_by('name')
    services = Service.objects.filter(is_active=True)

    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search': search,
        'total_count': appointments.count(),
        'today': timezone.now().date(),
        'users': users,
        'pets': pets,
        'services': services,
    }
    return render(request, 'admin_dashboard/appointments.html', context)


@admin_required
def change_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'confirmed', 'completed', 'cancelled']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Estado actualizado a {appointment.get_status_display()}')
    return redirect('admin_dashboard:appointments')


@admin_required
def create_appointment_admin(request):
    if request.method == 'POST':
        Appointment.objects.create(
            user_id=request.POST.get('user'),
            pet_id=request.POST.get('pet'),
            service_id=request.POST.get('service'),
            date=request.POST.get('date'),
            time=request.POST.get('time'),
            notes=request.POST.get('notes', ''),
            status='confirmed'
        )
        messages.success(request, 'Cita creada exitosamente.')
    return redirect('admin_dashboard:appointments')


@admin_required
def users_view(request):
    """Vista de gestión de usuarios"""
    
    search = request.GET.get('search', '')
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Agregar estadísticas por usuario
    users_data = []
    for user in users:
        users_data.append({
            'user': user,
            'pets_count': Pet.objects.filter(owner=user).count(),
            'appointments_count': Appointment.objects.filter(user=user).count(),
        })
    
    context = {
        'users_data': users_data,
        'search': search,
        'total_count': users.count(),
    }
    
    return render(request, 'admin_dashboard/users.html', context)

from datetime import date
@admin_required
def pets_view(request):
    """Vista de gestión de mascotas"""
    
    type_filter = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    
    pets = Pet.objects.select_related('owner').order_by('-created_at')
    
    if type_filter != 'all':
        pets = pets.filter(pet_type=type_filter)
    
    if search:
        pets = pets.filter(
            Q(name__icontains=search) |
            Q(owner__username__icontains=search) |
            Q(breed__icontains=search)
        )
    
    # Estadísticas
    total_dogs = Pet.objects.filter(pet_type='dog').count()
    total_cats = Pet.objects.filter(pet_type='cat').count()
    total_others = Pet.objects.filter(pet_type='other').count()
    users = User.objects.filter(is_superuser=False).order_by('username')

    context = {
        'pets': pets,
        'type_filter': type_filter,
        'search': search,
        'total_count': pets.count(),
        'total_dogs': total_dogs,
        'total_cats': total_cats,
        'total_others': total_others,
        'users': users,
        'today': date.today().isoformat()
    }

    return render(request, 'admin_dashboard/pets.html', context)


@admin_required
def veterinarians_view(request):
    """Vista de gestión de veterinarios"""
    
    specialty_filter = request.GET.get('specialty', 'all')
    search = request.GET.get('search', '')
    
    vets = Veterinarian.objects.all().order_by('name')
    
    if specialty_filter != 'all':
        vets = vets.filter(specialty=specialty_filter)
    
    if search:
        vets = vets.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(license_number__icontains=search)
        )
    
    context = {
        'veterinarians': vets,
        'specialty_filter': specialty_filter,
        'search': search,
        'total_count': vets.count(),
        'active_count': vets.filter(is_active=True).count(),
        'veterinarians': vets,
        'specialty_filter': specialty_filter,
        'search': search,
        'total_count': vets.count(),
        'active_count': vets.filter(is_active=True).count(),
        'services': Service.objects.filter(is_active=True),
    }
    
    return render(request, 'admin_dashboard/veterinarians.html', context)


@admin_required
def services_view(request):
    """Vista de gestión de servicios"""
    
    search = request.GET.get('search', '')
    
    services = Service.objects.all().order_by('name')
    
    if search:
        services = services.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'services': services,
        'search': search,
        'total_count': services.count(),
        'active_count': services.filter(is_active=True).count(),
    }
    
    return render(request, 'admin_dashboard/services.html', context)


@admin_required
def schedules_view(request):
    clinic_schedules = ClinicSchedule.objects.all()

    open_days = clinic_schedules.filter(is_open=True).count()

    context = {
        'clinic_schedules': clinic_schedules,
        'open_days': open_days,
    }

    return render(request, 'admin_dashboard/schedules.html', context)


@admin_required
def reports_view(request):
    """Vista de reportes y estadísticas avanzadas"""
    
    # Período de reporte
    period = request.GET.get('period', '30')  # días
    days = int(period)
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Citas en el período
    appointments_in_period = Appointment.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Nuevos usuarios en el período
    new_users = User.objects.filter(
        date_joined__gte=start_date,
        is_superuser=False
    ).count()
    
    # Nuevas mascotas en el período
    new_pets = Pet.objects.filter(
        created_at__gte=start_date
    ).count()
    
    # Citas por mes (últimos 6 meses)
    appointments_by_month = []
    for i in range(5, -1, -1):
        month_date = end_date - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1)
        
        count = Appointment.objects.filter(
            date__gte=month_start,
            date__lt=month_end
        ).count()
        
        appointments_by_month.append({
            'month': month_date.strftime('%B'),
            'count': count
        })
    
    # Top 5 usuarios con más citas
    top_users = User.objects.filter(is_superuser=False).annotate(
        appointments_count=Count('appointments')
    ).order_by('-appointments_count')[:5]
    
    # Servicios más solicitados (simulado con citas)
    service_stats = Service.objects.filter(is_active=True).annotate(
        usage_count=Count('id')
    )[:10]
    
    context = {
        'period': period,
        'start_date': start_date,
        'end_date': end_date,
        'total_appointments': appointments_in_period.count(),
        'new_users': new_users,
        'new_pets': new_pets,
        'appointments_by_month': json.dumps(appointments_by_month),
        'top_users': top_users,
        'service_stats': service_stats,
    }
    
    return render(request, 'admin_dashboard/reports.html', context)


@admin_required
def delete_appointment(request, appointment_id):
    """Eliminar una cita"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    messages.success(request, 'Cita eliminada exitosamente')
    return redirect('admin_dashboard:appointments')


@admin_required
def toggle_user_status(request, user_id):
    """Activar/desactivar usuario"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f'Usuario {status} exitosamente')
    return redirect('admin_dashboard:users')


@admin_required
def delete_pet(request, pet_id):
    """Eliminar una mascota"""
    pet = get_object_or_404(Pet, id=pet_id)
    pet_name = pet.name
    pet.delete()
    messages.success(request, f'{pet_name} ha sido eliminado')
    return redirect('admin_dashboard:pets')


@admin_required
def toggle_vet_status(request, vet_id):
    """Activar/desactivar veterinario"""
    vet = get_object_or_404(Veterinarian, id=vet_id)
    vet.is_active = not vet.is_active
    vet.save()
    status = "activado" if vet.is_active else "desactivado"
    messages.success(request, f'Veterinario {status} exitosamente')
    return redirect('admin_dashboard:veterinarians')


@admin_required
def toggle_service_status(request, service_id):
    """Activar/desactivar servicio"""
    service = get_object_or_404(Service, id=service_id)
    service.is_active = not service.is_active
    service.save()
    status = "activado" if service.is_active else "desactivado"
    messages.success(request, f'Servicio {status} exitosamente')
    return redirect('admin_dashboard:services')


@admin_required
def upload_document_view(request):
    """Vista para subir documentos PDF"""
    from booking.models import Document
    from django.contrib import messages
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        icon = request.POST.get('icon', '📄')
        file = request.FILES.get('file')
        
        if not all([title, category, file]):
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return redirect('admin_dashboard:upload_document')
        
        # Validar que sea un PDF
        if not file.name.endswith('.pdf'):
            messages.error(request, 'Solo se permiten archivos PDF.')
            return redirect('admin_dashboard:upload_document')
        
        try:
            document = Document.objects.create(
                title=title,
                description=description,
                category=category,
                icon=icon,
                file=file,
                uploaded_by=request.user
            )
            messages.success(request, f'Documento "{title}" subido exitosamente.')
            return redirect('admin_dashboard:upload_document')
        except Exception as e:
            messages.error(request, f'Error al subir el documento: {str(e)}')
            return redirect('admin_dashboard:upload_document')
    
    # GET request
    documents = Document.objects.all().order_by('-created_at')
    
    context = {
        'documents': documents,
        'category_choices': Document.CATEGORY_CHOICES,
    }
    
    return render(request, 'admin_dashboard/upload_document.html', context)


@admin_required
def delete_document_view(request, document_id):
    """Vista para eliminar un documento"""
    from booking.models import Document
    from django.contrib import messages
    import os
    
    try:
        document = Document.objects.get(id=document_id)
        
        # Eliminar el archivo físico
        if document.file:
            if os.path.isfile(document.file.path):
                os.remove(document.file.path)
        
        document_title = document.title
        document.delete()
        
        messages.success(request, f'Documento "{document_title}" eliminado exitosamente.')
    except Document.DoesNotExist:
        messages.error(request, 'El documento no existe.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el documento: {str(e)}')
    
    return redirect('admin_dashboard:upload_document')


@admin_required
def toggle_document_status_view(request, document_id):
    """Vista para activar/desactivar un documento"""
    from booking.models import Document
    from django.contrib import messages
    
    try:
        document = Document.objects.get(id=document_id)
        document.is_active = not document.is_active
        document.save()
        
        status = "activado" if document.is_active else "desactivado"
        messages.success(request, f'Documento "{document.title}" {status} exitosamente.')
    except Document.DoesNotExist:
        messages.error(request, 'El documento no existe.')
    except Exception as e:
        messages.error(request, f'Error al cambiar el estado: {str(e)}')
    
    return redirect('admin_dashboard:upload_document')

@admin_required
def add_veterinarian(request):
    if request.method == 'POST':
        vet = Veterinarian.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            license_number=request.POST.get('license_number'),
            specialty=request.POST.get('specialty'),
            years_experience=request.POST.get('years_experience', 0),
            start_time=request.POST.get('start_time', '08:00'),
            end_time=request.POST.get('end_time', '17:00'),
            is_active=True
        )
        if request.FILES.get('photo'):
            vet.photo = request.FILES['photo']
            vet.save()

        selected_services = request.POST.getlist('services')
        vet.services.set(selected_services)

        messages.success(request, 'Veterinario agregado exitosamente.')
    return redirect('admin_dashboard:veterinarians')

# =========================
#   CONSULTAS Y RECETAS
# =========================
from booking.models import MedicalConsultation, MedicalPrescription, PrescriptionItem

@admin_required
def consultations_view(request):
    """Lista de todas las consultas"""
    search = request.GET.get('search', '')
    
    consultations = MedicalConsultation.objects.select_related(
        'appointment__pet',
        'appointment__user',
        'veterinarian'
    ).order_by('-created_at')
    
    if search:
        consultations = consultations.filter(
            Q(appointment__pet__name__icontains=search) |
            Q(appointment__user__username__icontains=search) |
            Q(diagnosis__icontains=search)
        )
    
    context = {
        'consultations': consultations,
        'search': search,
        'total_count': consultations.count(),
    }
    return render(request, 'admin_dashboard/consultations.html', context)


@admin_required
def add_consultation_view(request):
    appointments = Appointment.objects.select_related(
        'pet', 'user'
    ).filter(
        status='completed'
    ).exclude(
        consultation__isnull=False
    ).order_by('-date')
    
    veterinarians = Veterinarian.objects.filter(is_active=True)
    selected_appointment = request.GET.get('appointment', '')

    if request.method == 'POST':
        appointment_id = request.POST.get('appointment')
        vet_id = request.POST.get('veterinarian')

        if MedicalConsultation.objects.filter(appointment_id=appointment_id).exists():
            messages.error(request, 'Ya existe una consulta para esta cita.')
            return redirect('admin_dashboard:add_consultation')

        consultation = MedicalConsultation.objects.create(
            appointment_id=appointment_id,
            veterinarian_id=vet_id if vet_id else None,
            reason=request.POST.get('reason'),
            symptoms=request.POST.get('symptoms'),
            diagnosis=request.POST.get('diagnosis'),
            treatment=request.POST.get('treatment'),
            notes=request.POST.get('notes', ''),
            weight_at_visit=request.POST.get('weight_at_visit') or None,
            temperature=request.POST.get('temperature') or None,
            next_visit=request.POST.get('next_visit') or None,
        )
        messages.success(request, 'Consulta creada exitosamente.')

        if request.POST.get('has_prescription'):
            return redirect('admin_dashboard:add_prescription', consultation_id=consultation.id)

        return redirect('admin_dashboard:consultations')

    context = {
        'appointments': appointments,
        'veterinarians': veterinarians,
        'selected_appointment': selected_appointment,
    }
    return render(request, 'admin_dashboard/add_consultation.html', context)

@admin_required
def edit_consultation_view(request, consultation_id):
    """Editar consulta existente"""
    consultation = get_object_or_404(MedicalConsultation, id=consultation_id)
    veterinarians = Veterinarian.objects.filter(is_active=True)

    if request.method == 'POST':
        consultation.veterinarian_id = request.POST.get('veterinarian') or None
        consultation.reason = request.POST.get('reason')
        consultation.symptoms = request.POST.get('symptoms')
        consultation.diagnosis = request.POST.get('diagnosis')
        consultation.treatment = request.POST.get('treatment')
        consultation.notes = request.POST.get('notes', '')
        consultation.weight_at_visit = request.POST.get('weight_at_visit') or None
        consultation.temperature = request.POST.get('temperature') or None
        consultation.next_visit = request.POST.get('next_visit') or None
        consultation.save()

        messages.success(request, 'Consulta actualizada exitosamente.')
        return redirect('admin_dashboard:consultations')

    context = {
        'consultation': consultation,
        'veterinarians': veterinarians,
    }
    return render(request, 'admin_dashboard/edit_consultation.html', context)


@admin_required
def delete_consultation_view(request, consultation_id):
    consultation = get_object_or_404(MedicalConsultation, id=consultation_id)
    consultation.delete()
    messages.success(request, 'Consulta eliminada.')
    return redirect('admin_dashboard:consultations')


@admin_required
def add_prescription_view(request, consultation_id):
    """Crear receta para una consulta"""
    consultation = get_object_or_404(MedicalConsultation, id=consultation_id)

    # Si ya tiene receta, redirige a editarla
    if hasattr(consultation, 'prescription'):
        return redirect('admin_dashboard:edit_prescription', prescription_id=consultation.prescription.id)

    if request.method == 'POST':
        prescription = MedicalPrescription.objects.create(
            consultation=consultation,
            general_instructions=request.POST.get('general_instructions'),
            warnings=request.POST.get('warnings', ''),
        )

        # Medicamentos (pueden venir múltiples)
        medications = request.POST.getlist('medication')
        doses = request.POST.getlist('dose')
        frequencies = request.POST.getlist('frequency')
        durations = request.POST.getlist('duration')
        routes = request.POST.getlist('route')
        instructions_list = request.POST.getlist('instructions')

        for i in range(len(medications)):
            if medications[i]:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medication=medications[i],
                    dose=doses[i] if i < len(doses) else '',
                    frequency=frequencies[i] if i < len(frequencies) else '',
                    duration=durations[i] if i < len(durations) else '',
                    route=routes[i] if i < len(routes) else 'oral',
                    instructions=instructions_list[i] if i < len(instructions_list) else '',
                )

        messages.success(request, 'Receta creada exitosamente.')
        return redirect('admin_dashboard:consultations')

    context = {
        'consultation': consultation,
        'routes': PrescriptionItem.ROUTES,
    }
    return render(request, 'admin_dashboard/add_prescription.html', context)


@admin_required
def edit_prescription_view(request, prescription_id):
    """Editar receta existente"""
    prescription = get_object_or_404(MedicalPrescription, id=prescription_id)

    if request.method == 'POST':
        prescription.general_instructions = request.POST.get('general_instructions')
        prescription.warnings = request.POST.get('warnings', '')
        prescription.save()

        # Eliminar items anteriores y recrear
        prescription.items.all().delete()

        medications = request.POST.getlist('medication')
        doses = request.POST.getlist('dose')
        frequencies = request.POST.getlist('frequency')
        durations = request.POST.getlist('duration')
        routes = request.POST.getlist('route')
        instructions_list = request.POST.getlist('instructions')

        for i in range(len(medications)):
            if medications[i]:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medication=medications[i],
                    dose=doses[i] if i < len(doses) else '',
                    frequency=frequencies[i] if i < len(frequencies) else '',
                    duration=durations[i] if i < len(durations) else '',
                    route=routes[i] if i < len(routes) else 'oral',
                    instructions=instructions_list[i] if i < len(instructions_list) else '',
                )

        messages.success(request, 'Receta actualizada exitosamente.')
        return redirect('admin_dashboard:consultations')

    context = {
        'prescription': prescription,
        'routes': PrescriptionItem.ROUTES,
    }
    return render(request, 'admin_dashboard/edit_prescription.html', context)


@admin_required
def delete_prescription_view(request, prescription_id):
    prescription = get_object_or_404(MedicalPrescription, id=prescription_id)
    consultation_id = prescription.consultation.id
    prescription.delete()
    messages.success(request, 'Receta eliminada.')
    return redirect('admin_dashboard:consultations')


from django.contrib.auth.models import User
from booking.models import UserProfile

@admin_required
def create_user_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')

        # Verificar que no exista el username o email
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya existe.')
            return redirect('admin_dashboard:users')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ese email ya está registrado.')
            return redirect('admin_dashboard:users')

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Crear o actualizar perfil
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.phone = phone
        profile.address = address
        profile.save()

        messages.success(request, f'Usuario {username} creado exitosamente.')
        return redirect('admin_dashboard:users')

    return redirect('admin_dashboard:users')

# =========================
#   SERVICIOS CRUD
# =========================
@admin_required
def create_service_view(request):
    if request.method == 'POST':
        Service.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            duration=request.POST.get('duration'),
            price=request.POST.get('price'),
            icon=request.POST.get('icon', 'bi bi-clipboard-pulse'),
            is_active=True
        )
        messages.success(request, 'Servicio creado exitosamente.')
    return redirect('admin_dashboard:services')


@admin_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.duration = request.POST.get('duration')
        service.price = request.POST.get('price')
        service.icon = request.POST.get('icon', 'bi bi-clipboard-pulse')
        service.save()
        messages.success(request, 'Servicio actualizado.')
    return redirect('admin_dashboard:services')


# =========================
#   HORARIOS CRUD
# =========================
@admin_required
def edit_schedule_view(request, schedule_id):
    schedule = get_object_or_404(ClinicSchedule, id=schedule_id)
    if request.method == 'POST':
        schedule.is_open = request.POST.get('is_open') == 'on'
        schedule.opening_time = request.POST.get('opening_time')
        schedule.closing_time = request.POST.get('closing_time')
        schedule.notes = request.POST.get('notes', '')
        schedule.save()
        messages.success(request, 'Horario actualizado.')
    return redirect('admin_dashboard:schedules')


@admin_required
def create_schedule_view(request):
    if request.method == 'POST':
        day = request.POST.get('day_of_week')
        if ClinicSchedule.objects.filter(day_of_week=day).exists():
            messages.error(request, 'Ya existe un horario para ese día.')
            return redirect('admin_dashboard:schedules')
        ClinicSchedule.objects.create(
            day_of_week=day,
            is_open=request.POST.get('is_open') == 'on',
            opening_time=request.POST.get('opening_time'),
            closing_time=request.POST.get('closing_time'),
            notes=request.POST.get('notes', '')
        )
        messages.success(request, 'Horario creado exitosamente.')
    return redirect('admin_dashboard:schedules')

from django.conf import settings

def admin_register_view(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_dashboard:dashboard')

    if request.method == 'POST':
        secret = request.POST.get('secret_key')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if secret != settings.ADMIN_SECRET_KEY:
            messages.error(request, 'Clave secreta incorrecta.')
            return redirect('admin_dashboard:admin_register')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('admin_dashboard:admin_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya existe.')
            return redirect('admin_dashboard:admin_register')

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        login(request, user)
        return redirect('admin_dashboard:dashboard')

    return render(request, 'admin_dashboard/admin_register.html')

from booking.models import UserProfile

@admin_required
def admin_profile_view(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()

        new_password = request.POST.get('new_password', '')
        if new_password:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)

        if request.FILES.get('avatar'):
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.avatar = request.FILES['avatar']
            profile.save()

        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('admin_dashboard:admin_profile')

    return render(request, 'admin_dashboard/admin_profile.html')


@admin_required
def create_pet(request):
    if request.method == 'POST':
        from django.contrib.auth.models import User
        Pet.objects.create(
            owner_id=request.POST.get('owner'),
            name=request.POST.get('name'),
            pet_type=request.POST.get('pet_type'),
            breed=request.POST.get('breed', ''),
            date_of_birth=request.POST.get('date_of_birth') or None,
            weight=request.POST.get('weight', 0),
            color=request.POST.get('color', ''),
            vaccination_status=request.POST.get('vaccination_status', 'updated'),
        )
        messages.success(request, 'Mascota agregada exitosamente.')
    return redirect('admin_dashboard:pets')

from booking.models import Vaccine

@admin_required
def pet_vaccines_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)
    vaccines = Vaccine.objects.filter(pet=pet).order_by('-date')

    if request.method == 'POST':
        Vaccine.objects.create(
            pet=pet,
            name=request.POST.get('name'),
            date=request.POST.get('date'),
            next_date=request.POST.get('next_date') or None,
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'Vacuna agregada a {pet.name}.')
        return redirect('admin_dashboard:pet_vaccines', pet_id=pet.id)

    context = {
        'pet': pet,
        'vaccines': vaccines,
        'today': date.today(),
    }
    return render(request, 'admin_dashboard/pet_vaccines.html', context)


@admin_required
def delete_vaccine_view(request, vaccine_id):
    vaccine = get_object_or_404(Vaccine, id=vaccine_id)
    pet_id = vaccine.pet.id
    vaccine.delete()
    messages.success(request, 'Vacuna eliminada.')
    return redirect('admin_dashboard:pet_vaccines', pet_id=pet_id)


@admin_required
def edit_veterinarian_view(request, vet_id):
    vet = get_object_or_404(Veterinarian, id=vet_id)
    services = Service.objects.filter(is_active=True)

    if request.method == 'POST':
        vet.name = request.POST.get('name')
        vet.email = request.POST.get('email')
        vet.phone = request.POST.get('phone', '')
        vet.license_number = request.POST.get('license_number')
        vet.specialty = request.POST.get('specialty')
        vet.years_experience = request.POST.get('years_experience', 0)
        vet.start_time = request.POST.get('start_time', '08:00')
        vet.end_time = request.POST.get('end_time', '17:00')
        vet.bio = request.POST.get('bio', '')

        if request.FILES.get('photo'):
            vet.photo = request.FILES['photo']

        vet.save()

        # Servicios seleccionados
        selected_services = request.POST.getlist('services')
        vet.services.set(selected_services)

        messages.success(request, 'Veterinario actualizado exitosamente.')
        return redirect('admin_dashboard:veterinarians')

    context = {
        'vet': vet,
        'services': services,
        'selected_services': list(vet.services.values_list('id', flat=True)),
    }
    return render(request, 'admin_dashboard/edit_veterinarian.html', context)
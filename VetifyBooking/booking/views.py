from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone

from .forms import RegisterForm, AppointmentForm
from .models import (
    Appointment,
    Pet,
    Service,
    Veterinarian,
    ClinicSchedule,
    Document,
)


# =============================
# AUTH
# =============================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'booking/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'booking/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# =============================
# HOME
# =============================

@login_required
def home_view(request):
    total_vets = Veterinarian.objects.filter(is_active=True).count()
    return render(request, 'booking/home.html', {'total_vets': total_vets})


# =============================
# BOOKINGS
# =============================
@login_required
def booking_view(request):

    preselected_vet_id = request.GET.get('vet')
    preselected_service_id = request.GET.get('service')

    preselected_vet = None

    if preselected_vet_id:
        preselected_vet = Veterinarian.objects.filter(id=preselected_vet_id).first()

    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()

            messages.success(
                request,
                f'¡Cita agendada para {appointment.pet.name}!'
            )
            return redirect('appointments')
    else:
        form = AppointmentForm(user=request.user)

    return render(request, 'booking/booking.html', {
        'form': form,
        'preselected_vet_id': preselected_vet_id,
        'preselected_vet': preselected_vet,
        'preselected_service_id': preselected_service_id
    })


@login_required
def appointments_view(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(
        request,
        'booking/appointments.html',
        {'appointments': appointments}
    )

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment,
        pk=appointment_id,
        user=request.user
    )
    appointment.delete()
    messages.success(request, '¡Cita cancelada correctamente!')
    return redirect('appointments')


# =============================
# PROFILE & PETS
# =============================

@login_required
def profile_view(request):
    pets = Pet.objects.filter(owner=request.user)
    appointments_count = Appointment.objects.filter(
        user=request.user
    ).count()

    next_appointment = Appointment.objects.filter(
        user=request.user,
        date__gte=timezone.now().date()
    ).order_by('date', 'time').first()

    context = {
        'pets': pets,
        'appointments_count': appointments_count,
        'next_appointment': next_appointment,
        'pets_count': pets.count(),
    }

    return render(request, 'booking/profile.html', context)


from datetime import date

@login_required
def register_pet_view(request):
    if request.method == 'POST':
        pet = Pet(owner=request.user)

        pet.name = request.POST.get('name')
        pet.pet_type = request.POST.get('species')
        pet.other_type = request.POST.get('other_type', '')
        pet.breed = request.POST.get('breed', '')
        pet.color = request.POST.get('color', '')
        pet.date_of_birth = request.POST.get('date_of_birth') or None
        pet.weight = request.POST.get('weight', 0)
        pet.vaccination_status = request.POST.get('vaccination', 'updated')
        pet.allergies = request.POST.get('allergies', '')
        pet.friendly_with_people = request.POST.get('friendly_people') == 'on'
        pet.friendly_with_animals = request.POST.get('friendly_animals') == 'on'
        pet.nervous_at_vet = request.POST.get('nervous') == 'on'
        pet.special_care = request.POST.get('special_care') == 'on'
        pet.emergency_contact_name = request.POST.get('emergency_name', '')
        pet.emergency_contact_phone = request.POST.get('emergency_phone', '')

        if 'photo' in request.FILES:
            pet.photo = request.FILES['photo']

        pet.save()

        messages.success(request, f'¡{pet.name} ha sido registrado exitosamente!')
        return redirect('profile')

    return render(request, 'booking/register_pet.html', {'today': date.today().isoformat()})



# =============================
# SERVICES & SCHEDULES
# =============================

@login_required
def services_schedules_view(request):
    services = Service.objects.filter(is_active=True).order_by('name')

    days = [
        ('Lunes',     'monday'),
        ('Martes',    'tuesday'),
        ('Miércoles', 'wednesday'),
        ('Jueves',    'thursday'),
        ('Viernes',   'friday'),
        ('Sábado',    'saturday'),
        ('Domingo',   'sunday'),
    ]

    today_name = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][date.today().weekday()]

    schedules = []
    for name, day_key in days:
        schedule = ClinicSchedule.objects.filter(day_of_week=day_key).first()

        if not schedule:
            schedule = ClinicSchedule(day_of_week=day_key, is_open=False)

        schedule.day_display = name
        schedule.is_today = (day_key == today_name)

        # Compatibilidad con el template que usa start_time/end_time
        schedule.start_time = schedule.opening_time
        schedule.end_time = schedule.closing_time

        schedules.append(schedule)

    veterinarians = Veterinarian.objects.filter(is_active=True).order_by('name')

    return render(request, 'booking/services_schedules.html', {
        'services': services,
        'schedules': schedules,
        'veterinarians': veterinarians,
    })


# =============================
# DOCUMENTS
# =============================

@login_required
def documents_view(request):

    documents = Document.objects.filter(
        is_active=True
    ).order_by('-created_at')

    documents_by_category = {}

    for doc in documents:
        category = doc.get_category_display()
        documents_by_category.setdefault(category, []).append(doc)

    return render(
        request,
        'booking/documents.html',
        {
            'documents': documents,
            'documents_by_category': documents_by_category,
            'total_documents': documents.count(),
        }
    )
    
    
# booking/views.py - Vistas para el perfil de usuario

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import UserProfile, Pet, Appointment
from datetime import datetime

@login_required
def profile(request):
    """
    Vista para mostrar el perfil del usuario
    """
    # Obtener o crear el perfil del usuario
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Obtener estadísticas del usuario
    total_appointments = Appointment.objects.filter(user=request.user).count()
    completed_appointments = Appointment.objects.filter(
        user=request.user, 
        status='completed'
    ).count()
    pending_appointments = Appointment.objects.filter(
        user=request.user, 
        status__in=['pending', 'confirmed']
    ).count()
    
    context = {
        'user': request.user,
        'profile': profile,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'pending_appointments': pending_appointments,
    }
    
    return render(request, 'booking/profile.html', context)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.bio = request.POST.get('bio', '')
        
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
        return redirect('profile')
    
    context = {'user': request.user, 'profile': profile}
    return render(request, 'booking/edit_profile.html', context)

@login_required
def update_avatar(request):
    """
    Vista para actualizar la foto de perfil del usuario
    """
    if request.method == 'POST' and request.FILES.get('avatar'):
        # Obtener o crear el perfil del usuario
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Actualizar avatar
        profile.avatar = request.FILES['avatar']
        profile.save()
        
        messages.success(request, '¡Tu foto de perfil ha sido actualizada!')
        return redirect('edit_profile')
    
    return redirect('edit_profile')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Pet



from django.urls import resolve, reverse, NoReverseMatch

@login_required
def edit_pet(request, pet_id):
    if request.user.is_superuser:
        pet = get_object_or_404(Pet, id=pet_id)
    else:
        pet = get_object_or_404(Pet, id=pet_id, owner=request.user)

    next_url = request.GET.get('next') or request.POST.get('next')
    if not next_url:
        next_url = reverse('profile')

    if request.method == "POST":
        pet.name = request.POST.get("name")
        pet.pet_type = request.POST.get("species") or pet.pet_type
        pet.other_type = request.POST.get("other_type", '')
        pet.breed = request.POST.get("breed", '')
        pet.color = request.POST.get("color", '')
        pet.date_of_birth = request.POST.get('date_of_birth') or None
        pet.weight = request.POST.get("weight")
        pet.vaccination_status = request.POST.get('vaccination', 'updated')
        pet.allergies = request.POST.get('allergies', '')
        pet.friendly_with_people = request.POST.get('friendly_people') == 'on'
        pet.friendly_with_animals = request.POST.get('friendly_animals') == 'on'
        pet.nervous_at_vet = request.POST.get('nervous') == 'on'
        pet.special_care = request.POST.get('special_care') == 'on'
        pet.emergency_contact_name = request.POST.get('emergency_name', '')
        pet.emergency_contact_phone = request.POST.get('emergency_phone', '')

        if request.FILES.get('photo'):
            pet.photo = request.FILES['photo']

        pet.save()
        return redirect(next_url)

    return render(request, "booking/register_pet.html", {
        "pet": pet,
        "next": next_url,
        "today": date.today().isoformat()
    })

@login_required
def delete_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    if request.method == 'POST':
        pet_name = pet.name
        pet.delete()
        messages.success(request, f'{pet_name} ha sido eliminado de tu perfil.')
        return redirect('profile')

    context = {
        'pet': pet,
    }

    return render(request, 'booking/confirm_delete_pet.html', context)

# =============================
# HISTORIAL MÉDICO
# =============================
from django.utils import timezone

@login_required
def medical_history_view(request):
    appointments = Appointment.objects.filter(
        user=request.user
    ).select_related(
        'pet'
    ).prefetch_related(
        'consultation__veterinarian',
        'consultation__prescription__items'
    ).order_by('-date', '-time')

    context = {
        'appointments': appointments,
        'today': timezone.now().date(),
    }
    return render(request, 'booking/medical_history.html', context)

# =============================
# EXPORTAR PDF
# =============================
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .models import MedicalConsultation, MedicalPrescription

@login_required
def export_consultation_pdf(request, consultation_id):
    consultation = get_object_or_404(
        MedicalConsultation,
        id=consultation_id,
        appointment__user=request.user
    )
    html_string = render_to_string('booking/pdf_consultation.html', {
        'consultation': consultation,
    })
    buffer = BytesIO()
    pisa.CreatePDF(html_string, dest=buffer)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="consulta_{consultation.appointment.pet.name}_{consultation.appointment.date}.pdf"'
    return response


@login_required
def export_prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(
        MedicalPrescription,
        id=prescription_id,
        consultation__appointment__user=request.user
    )
    html_string = render_to_string('booking/pdf_prescription.html', {
        'prescription': prescription,
    })
    buffer = BytesIO()
    pisa.CreatePDF(html_string, dest=buffer)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receta_{prescription.consultation.appointment.pet.name}_{prescription.consultation.appointment.date}.pdf"'
    return response

from .models import Vaccine

@login_required
def pet_detail_view(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, owner=request.user)
    vaccines = Vaccine.objects.filter(pet=pet).order_by('-date')
    today = date.today()

    context = {
        'pet': pet,
        'vaccines': vaccines,
        'today': today,
    }
    return render(request, 'booking/pet_detail.html', context)

@login_required
def veterinarians_view(request):
    veterinarians = Veterinarian.objects.all().order_by('name')
    return render(request, 'booking/veterinarians.html', {
        'veterinarians': veterinarians,
    })

from django.http import JsonResponse

@login_required
def vets_by_service(request, service_id):
    vets = Veterinarian.objects.filter(
        services__id=service_id,
        is_active=True
    )

    return JsonResponse({
        'vets': [
            {
                'id': vet.id,
                'name': vet.name,
                'specialty': vet.get_specialty_display(),
                'photo': vet.photo.url if vet.photo else None
            }
            for vet in vets
        ]
    })

from django.http import JsonResponse
from .models import Veterinarian

def all_vets(request):
    vets = Veterinarian.objects.filter(is_active=True)

    return JsonResponse({
        'vets': [
            {
                'id': vet.id,
                'name': vet.name,
                'specialty': vet.get_specialty_display()
            }
            for vet in vets
        ]
    })
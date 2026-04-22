from django.db import models
from django.contrib.auth.models import User


# =========================
#        PET MODEL
# =========================
class Pet(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', 'Perro'),
        ('cat', 'Gato'),
        ('other', 'Otro'),
    ]

    VACCINATION_STATUS_CHOICES = [
        ('updated', 'Al día'),
        ('pending', 'Pendiente'),
        ('none', 'Sin vacunas'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')

    name = models.CharField(max_length=100, verbose_name="Nombre")
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES, verbose_name="Tipo")
    other_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Especificar tipo")

    breed = models.CharField(max_length=100, blank=True, verbose_name="Raza")
    color = models.CharField(max_length=50, blank=True, verbose_name="Color")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (kg)")

    vaccination_status = models.CharField(
        max_length=10,
        choices=VACCINATION_STATUS_CHOICES,
        default='updated',
        verbose_name="Estado de vacunación"
    )

    allergies = models.TextField(blank=True, verbose_name="Alergias o condiciones médicas")

    friendly_with_people = models.BooleanField(default=True)
    friendly_with_animals = models.BooleanField(default=True)
    nervous_at_vet = models.BooleanField(default=False)
    special_care = models.BooleanField(default=False)

    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    photo = models.ImageField(upload_to='pets/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_pet_type_display()})"

    def get_icon(self):
        icons = {
            'dog': 'bi bi-heart',
            'cat': 'bi bi-heart-fill',
            'other': 'bi bi-star'
        }
        return icons.get(self.pet_type, 'bi bi-paw')

    def get_last_appointment(self):
        return self.appointments.order_by('-date', '-time').first()


# =========================
#     APPOINTMENT MODEL
# =========================
class Appointment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')

    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Servicio"
    )

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.pet.name} - {self.date} {self.time} ({self.status})"


class Service(models.Model):
    """Servicios que ofrece la veterinaria"""

    name = models.CharField(max_length=100, verbose_name="Nombre del servicio")
    description = models.TextField(verbose_name="Descripción")
    duration = models.IntegerField(verbose_name="Duración (minutos)")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")

    icon = models.CharField(
        max_length=50,
        default="bi bi-clipboard-pulse",
        verbose_name="Icono Bootstrap"
    )

    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['name']

    def __str__(self):
        return self.name


class Veterinarian(models.Model):
    """Veterinarios disponibles"""

    SPECIALTIES = [
        ('general', 'Medicina General'),
        ('surgery', 'Cirugía'),
        ('dental', 'Odontología'),
        ('dermatology', 'Dermatología'),
        ('cardiology', 'Cardiología'),
        ('emergency', 'Emergencias'),
    ]

    name = models.CharField(max_length=200, verbose_name="Nombre completo")
    specialty = models.CharField(max_length=20, choices=SPECIALTIES, verbose_name="Especialidad")
    license_number = models.CharField(max_length=50, verbose_name="Número de cédula")
    email = models.EmailField(verbose_name="Correo electrónico")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")

    years_experience = models.IntegerField(verbose_name="Años de experiencia")
    bio = models.TextField(verbose_name="Biografía", blank=True)

    available_days = models.JSONField(
        default=list,
        verbose_name="Días disponibles"
    )

    start_time = models.TimeField(verbose_name="Hora de inicio", default="09:00")
    end_time = models.TimeField(verbose_name="Hora de fin", default="17:00")

    photo = models.ImageField(upload_to='vets/', blank=True, null=True, verbose_name="Foto")

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='veterinarians',
        verbose_name="Servicios que ofrece"
    )

    class Meta:
        verbose_name = "Veterinario"
        verbose_name_plural = "Veterinarios"
        ordering = ['name']

    def __str__(self):
        return f"Dr(a). {self.name} - {self.get_specialty_display()}"

    def get_icon(self):
        icons = {
            'general': 'bi bi-heart-pulse',
            'surgery': 'bi bi-hospital',
            'dental': 'bi bi-emoji-smile',
            'dermatology': 'bi bi-capsule',
            'cardiology': 'bi bi-heart',
            'emergency': 'bi bi-ambulance',
        }
        return icons.get(self.specialty, 'bi bi-person-badge')


class ClinicSchedule(models.Model):

    DAYS_OF_WEEK = [
        ('monday', 'Lunes'),
        ('tuesday', 'Martes'),
        ('wednesday', 'Miércoles'),
        ('thursday', 'Jueves'),
        ('friday', 'Viernes'),
        ('saturday', 'Sábado'),
        ('sunday', 'Domingo'),
    ]

    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK, unique=True, verbose_name="Día")
    is_open = models.BooleanField(default=True, verbose_name="Abierto")

    opening_time = models.TimeField(verbose_name="Hora de apertura", default="09:00")
    closing_time = models.TimeField(verbose_name="Hora de cierre", default="17:00")

    notes = models.TextField(blank=True, verbose_name="Notas adicionales")

    class Meta:
        verbose_name = "Horario de Clínica"
        verbose_name_plural = "Horarios de Clínica"
        ordering = ['day_of_week']

    def __str__(self):
        if self.is_open:
            return f"{self.get_day_of_week_display()}: {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
        return f"{self.get_day_of_week_display()}: Cerrado"


class Document(models.Model):

    CATEGORY_CHOICES = [
        ('general', 'Información General'),
        ('care', 'Cuidado de Mascotas'),
        ('health', 'Salud y Vacunación'),
        ('nutrition', 'Nutrición'),
        ('training', 'Entrenamiento'),
        ('other', 'Otros'),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción", blank=True)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name="Categoría"
    )

    file = models.FileField(upload_to='documents/', verbose_name="Archivo PDF")

    icon = models.CharField(
        max_length=50,
        default='bi bi-file-earmark-pdf',
        verbose_name="Icono Bootstrap"
    )

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Subido por")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de subida")

    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"

    def __str__(self):
        return self.title

    def get_file_size(self):
        try:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        except:
            return "Desconocido"


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    phone = models.CharField(max_length=20, blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)

    date_of_birth = models.DateField(null=True, blank=True)

    bio = models.TextField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
# =========================
#   MEDICAL CONSULTATION
# =========================
class MedicalConsultation(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='consultation',
        verbose_name="Cita"
    )
    veterinarian = models.ForeignKey(
        Veterinarian,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Veterinario"
    )

    # Campos clínicos
    reason = models.CharField(max_length=300, verbose_name="Motivo de consulta")
    symptoms = models.TextField(verbose_name="Síntomas observados")
    diagnosis = models.TextField(verbose_name="Diagnóstico")
    treatment = models.TextField(verbose_name="Tratamiento indicado")
    notes = models.TextField(blank=True, verbose_name="Notas adicionales")

    # Signos vitales
    weight_at_visit = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Peso (kg)"
    )
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1,
        null=True, blank=True,
        verbose_name="Temperatura (°C)"
    )

    next_visit = models.DateField(null=True, blank=True, verbose_name="Próxima visita")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Consulta Médica"
        verbose_name_plural = "Consultas Médicas"
        ordering = ['-created_at']

    def __str__(self):
        return f"Consulta - {self.appointment.pet.name} ({self.appointment.date})"


# =========================
#   MEDICAL PRESCRIPTION
# =========================
class MedicalPrescription(models.Model):

    consultation = models.OneToOneField(
        MedicalConsultation,
        on_delete=models.CASCADE,
        related_name='prescription',
        verbose_name="Consulta"
    )

    general_instructions = models.TextField(
        verbose_name="Indicaciones generales"
    )
    warnings = models.TextField(
        blank=True,
        verbose_name="Advertencias"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Receta Médica"
        verbose_name_plural = "Recetas Médicas"

    def __str__(self):
        return f"Receta - {self.consultation.appointment.pet.name} ({self.consultation.appointment.date})"


# =========================
#   PRESCRIPTION ITEM
# =========================
class PrescriptionItem(models.Model):

    ROUTES = [
        ('oral', 'Oral'),
        ('topical', 'Tópico'),
        ('injectable', 'Inyectable'),
        ('ophthalmic', 'Oftálmico'),
        ('otic', 'Ótico'),
        ('other', 'Otro'),
    ]

    prescription = models.ForeignKey(
        MedicalPrescription,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Receta"
    )

    medication = models.CharField(max_length=200, verbose_name="Medicamento")
    dose = models.CharField(max_length=100, verbose_name="Dosis")
    frequency = models.CharField(max_length=100, verbose_name="Frecuencia")
    duration = models.CharField(max_length=100, verbose_name="Duración")
    route = models.CharField(
        max_length=20,
        choices=ROUTES,
        default='oral',
        verbose_name="Vía de administración"
    )
    instructions = models.TextField(blank=True, verbose_name="Instrucciones específicas")

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    def __str__(self):
        return f"{self.medication} - {self.dose}"
    
    
# =========================
#     VACCINE MODEL
# =========================
class Vaccine(models.Model):
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='vaccines',
        verbose_name="Mascota"
    )
    name = models.CharField(max_length=200, verbose_name="Nombre de la vacuna")
    date = models.DateField(verbose_name="Fecha de aplicación")
    next_date = models.DateField(null=True, blank=True, verbose_name="Próxima dosis")
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.pet.name} ({self.date})"
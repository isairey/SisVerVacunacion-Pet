from django.contrib import admin
from .models import Appointment, Pet


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'user', 'service', 'date', 'time')
    list_filter = ('service', 'date')
    search_fields = ('pet__name', 'user__username')


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'pet_type', 'date_of_birth', 'vaccination_status')
    list_filter = ('pet_type', 'vaccination_status')
    search_fields = ('name', 'owner__username')
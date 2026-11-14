from django.contrib import admin
from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_type', 'team', 'health', 'attack_points')
    list_filter = ('team', 'unit_type')
    search_fields = ('name',)
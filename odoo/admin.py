from django.contrib import admin
from .models import OdooConnection


@admin.register(OdooConnection)
class OdooConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "database", "username", "is_active", "created_at")
    search_fields = ("tenant__name", "database", "username")
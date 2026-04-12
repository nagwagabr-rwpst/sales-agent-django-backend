from django.contrib import admin
from .models import SalesAgent


@admin.register(SalesAgent)
class SalesAgentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tenant", "is_active", "created_at")
    search_fields = ("user__username", "tenant__name")
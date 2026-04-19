from django.contrib import admin

from .models import SalesAgent


@admin.register(SalesAgent)
class SalesAgentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "tenant", "is_active", "created_at")
    list_filter = ("is_active", "tenant")
    search_fields = (
        "user__username",
        "user__email",
        "tenant__name",
        "tenant__code",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "tenant")
    list_select_related = ("user", "tenant")
    readonly_fields = ("created_at",)

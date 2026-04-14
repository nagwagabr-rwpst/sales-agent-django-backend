from django.contrib import admin

from .models import OdooConnection, OfflineSalesOrder


@admin.register(OdooConnection)
class OdooConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "tenant",
        "base_url",
        "database",
        "username",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "tenant")
    search_fields = (
        "tenant__name",
        "tenant__code",
        "base_url",
        "database",
        "username",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("tenant",)
    list_select_related = ("tenant",)
    readonly_fields = ("created_at",)
    fields = (
        "tenant",
        "base_url",
        "database",
        "username",
        "password",
        "is_active",
        "created_at",
    )


@admin.register(OfflineSalesOrder)
class OfflineSalesOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "tenant",
        "sales_agent",
        "customer_id",
        "status",
        "odoo_order_id",
        "odoo_order_name",
        "created_at",
        "synced_at",
    )
    search_fields = (
        "uuid",
        "tenant__name",
        "tenant__code",
        "sales_agent__user__username",
        "odoo_order_name",
    )
    list_filter = (
        "status",
        "tenant",
        "sales_agent",
        "created_at",
        "synced_at",
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_select_related = ("tenant", "sales_agent", "sales_agent__user")
    readonly_fields = (
        "uuid",
        "tenant",
        "sales_agent",
        "customer_id",
        "payload",
        "status",
        "odoo_order_id",
        "odoo_order_name",
        "error_message",
        "created_at",
        "synced_at",
    )

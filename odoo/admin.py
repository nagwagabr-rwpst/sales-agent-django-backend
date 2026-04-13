from django.contrib import admin
from .models import OdooConnection


from django.contrib import admin
from .models import OdooConnection, OfflineSalesOrder


@admin.register(OdooConnection)
class OdooConnectionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "base_url", "database", "username", "is_active", "created_at")
    search_fields = ("tenant__name", "base_url", "database", "username")
    list_filter = ("is_active",)


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
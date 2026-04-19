from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

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
        "odoo_products_link",
        "odoo_customers_link",
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
    fields = (
        "tenant",
        "base_url",
        "database",
        "username",
        "password",
        "is_active",
        "created_at",
        "odoo_products_link",
        "odoo_customers_link",
    )
    readonly_fields = ("created_at", "odoo_products_link", "odoo_customers_link")

    def _support_link(self, obj, url_name, label):
        url = reverse(url_name)
        query = urlencode({"tenant_id": obj.tenant_id})
        return format_html('<a href="{}?{}">{}</a>', url, query, label)

    @admin.display(description="View Odoo Products")
    def odoo_products_link(self, obj):
        return self._support_link(obj, "odoo_support_products", "View Odoo Products")

    @admin.display(description="View Odoo Customers")
    def odoo_customers_link(self, obj):
        return self._support_link(obj, "odoo_support_customers", "View Odoo Customers")


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

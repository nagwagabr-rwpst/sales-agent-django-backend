from django.contrib import admin
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "is_active",
        "created_at",
        "odoo_products_link",
        "odoo_customers_link",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("name",)
    readonly_fields = ("created_at", "odoo_products_link", "odoo_customers_link")

    def _support_link(self, obj, url_name, label):
        url = reverse(url_name)
        query = urlencode({"tenant_id": obj.pk})
        return format_html('<a href="{}?{}">{}</a>', url, query, label)

    @admin.display(description="View Odoo Products")
    def odoo_products_link(self, obj):
        return self._support_link(obj, "odoo_support_products", "View Odoo Products")

    @admin.display(description="View Odoo Customers")
    def odoo_customers_link(self, obj):
        return self._support_link(obj, "odoo_support_customers", "View Odoo Customers")

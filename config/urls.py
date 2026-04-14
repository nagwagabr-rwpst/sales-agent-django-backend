
from django.contrib import admin
from django.urls import include, path

from odoo.internal_support_views import (
    odoo_support_customers,
    odoo_support_products,
)

urlpatterns = [
    path(
        "admin/odoo-support/products/",
        admin.site.admin_view(odoo_support_products),
        name="odoo_support_products",
    ),
    path(
        "admin/odoo-support/customers/",
        admin.site.admin_view(odoo_support_customers),
        name="odoo_support_customers",
    ),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/odoo/", include("odoo.urls")),

]



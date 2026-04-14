"""
Staff-only internal views for Odoo read-only inspection (support / debugging).
Not part of the public API.
"""

from django.contrib import admin
from django.shortcuts import render
from core.models import Tenant

from .models import OdooConnection
from .services import OdooService

_SUPPORT_PAGE_SIZE_DEFAULT = 50
_SUPPORT_PAGE_SIZE_MAX = 100


def _parse_int(raw, default, *, minimum, maximum=None):
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return default, "Must be a valid integer."
    if v < minimum:
        return default, f"Must be >= {minimum}."
    if maximum is not None and v > maximum:
        return default, f"Must be <= {maximum}."
    return v, None


def odoo_support_products(request):
    """Read-only product list from live Odoo for a selected tenant."""
    tenants = Tenant.objects.order_by("name")
    error = None
    empty_message = None
    results = None
    total_count = None
    page = 1
    page_size = _SUPPORT_PAGE_SIZE_DEFAULT
    tenant = None
    tenant_id = request.GET.get("tenant")

    if tenant_id:
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except (Tenant.DoesNotExist, ValueError):
            error = "Selected tenant does not exist."
        else:
            page, err = _parse_int(
                request.GET.get("page", "1"),
                1,
                minimum=1,
                maximum=10_000,
            )
            if err:
                error = f"Page: {err}"
            page_size, err2 = _parse_int(
                request.GET.get("page_size", str(_SUPPORT_PAGE_SIZE_DEFAULT)),
                _SUPPORT_PAGE_SIZE_DEFAULT,
                minimum=1,
                maximum=_SUPPORT_PAGE_SIZE_MAX,
            )
            if err2:
                error = error or f"Page size: {err2}"

            if not error:
                try:
                    service = OdooService(tenant)
                except OdooConnection.DoesNotExist:
                    error = (
                        "No active Odoo connection is configured for this tenant."
                    )
                else:
                    try:
                        total_count = service.count_products()
                        offset = (page - 1) * page_size
                        results = service.get_products(
                            limit=page_size,
                            offset=offset,
                        )
                        if not results:
                            empty_message = "No products returned from Odoo for this page."
                    except Exception:
                        error = "Unable to load products from Odoo. Check connection and Odoo availability."

    context = {
        **admin.site.each_context(request),
        "title": "Odoo products by tenant",
        "tenants": tenants,
        "selected_tenant_id": str(tenant_id) if tenant_id else "",
        "tenant": tenant,
        "error": error,
        "empty_message": empty_message,
        "results": results,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "page_size_max": _SUPPORT_PAGE_SIZE_MAX,
    }
    return render(request, "admin/odoo_support/products.html", context)


def odoo_support_customers(request):
    """Read-only customer list from live Odoo for a selected tenant."""
    tenants = Tenant.objects.order_by("name")
    error = None
    empty_message = None
    results = None
    total_count = None
    page = 1
    page_size = _SUPPORT_PAGE_SIZE_DEFAULT
    search = (request.GET.get("search") or "").strip() or None
    tenant = None
    tenant_id = request.GET.get("tenant")

    if tenant_id:
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except (Tenant.DoesNotExist, ValueError):
            error = "Selected tenant does not exist."
        else:
            page, err = _parse_int(
                request.GET.get("page", "1"),
                1,
                minimum=1,
                maximum=10_000,
            )
            if err:
                error = f"Page: {err}"
            page_size, err2 = _parse_int(
                request.GET.get("page_size", str(_SUPPORT_PAGE_SIZE_DEFAULT)),
                _SUPPORT_PAGE_SIZE_DEFAULT,
                minimum=1,
                maximum=_SUPPORT_PAGE_SIZE_MAX,
            )
            if err2:
                error = error or f"Page size: {err2}"

            if not error:
                try:
                    service = OdooService(tenant)
                except OdooConnection.DoesNotExist:
                    error = (
                        "No active Odoo connection is configured for this tenant."
                    )
                else:
                    try:
                        offset = (page - 1) * page_size
                        data = service.get_customers(
                            search=search,
                            limit=page_size,
                            offset=offset,
                        )
                        total_count = data["count"]
                        results = data["results"]
                        if not results:
                            empty_message = (
                                "No customers matched this query (or empty page)."
                            )
                    except Exception:
                        error = "Unable to load customers from Odoo. Check connection and Odoo availability."

    context = {
        **admin.site.each_context(request),
        "title": "Odoo customers by tenant",
        "tenants": tenants,
        "selected_tenant_id": str(tenant_id) if tenant_id else "",
        "tenant": tenant,
        "search": search or "",
        "error": error,
        "empty_message": empty_message,
        "results": results,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "page_size_max": _SUPPORT_PAGE_SIZE_MAX,
    }
    return render(request, "admin/odoo_support/customers.html", context)

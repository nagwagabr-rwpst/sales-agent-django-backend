from rest_framework.decorators import api_view
from rest_framework.response import Response

from accounts.services import get_user_tenant
from odoo.services import OdooService


@api_view(["GET"])
def get_products_view(request):
    tenant = get_user_tenant(request.user)

    if not tenant:
        return Response({"error": "No tenant found"}, status=400)

    service = OdooService(tenant)
    products = service.get_products()

    return Response({"products": products})
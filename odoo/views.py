from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.services import get_user_tenant
from .services import OdooService
from .serializers import CreateOrderSerializer




@api_view(["GET"])
def get_products_view(request):
    tenant = get_user_tenant(request.user)

    if not tenant:
        return Response({"error": "No tenant found"}, status=400)

    service = OdooService(tenant)
    products = service.get_products()

    return Response({"products": products})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services import OdooService
from .serializers import CreateOrderSerializer


class OdooCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = get_user_tenant(request.user)
        if not tenant:
            return Response({"error": "No tenant found"}, status=status.HTTP_400_BAD_REQUEST)

        service = OdooService(tenant)

        customer_id = serializer.validated_data["customer_id"]
        items = serializer.validated_data["items"]

        result = service.create_order(
            customer_id=customer_id,
            items=items,
        )

        return Response(result, status=status.HTTP_201_CREATED)
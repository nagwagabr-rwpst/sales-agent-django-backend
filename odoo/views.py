from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.services import get_user_tenant
from .models import OfflineSalesOrder
from .services import OdooService
from .serializers import CreateOrderSerializer, OfflineSalesOrderListSerializer


@api_view(["GET"])
def get_products_view(request):
    tenant = get_user_tenant(request.user)

    if not tenant:
        return Response({"error": "No tenant found"}, status=400)

    service = OdooService(tenant)
    products = service.get_products()

    return Response({"products": products})


class OdooCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = request.user.salesagent.tenant
        sales_agent = request.user.salesagent

        customer_id = serializer.validated_data["customer_id"]
        items = serializer.validated_data["items"]

        offline_order = OfflineSalesOrder.objects.create(
            tenant=tenant,
            sales_agent=sales_agent,
            customer_id=customer_id,
            payload={
                "customer_id": customer_id,
                "items": items,
            },
        )

        return Response(
            {
                "success": True,
                "message": "Order saved locally (pending sync)",
                "offline_order_id": offline_order.id,
                "uuid": str(offline_order.uuid),
                "status": offline_order.status,
            },
            status=status.HTTP_201_CREATED,
        )


class SyncOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_uuid):
        tenant = request.user.salesagent.tenant
        sales_agent = request.user.salesagent
        service = OdooService(tenant)

        offline_order = get_object_or_404(
            OfflineSalesOrder,
            uuid=order_uuid,
            tenant=tenant,
            sales_agent=sales_agent,
        )

        if offline_order.status == OfflineSalesOrder.STATUS_SYNCED:
            return Response(
                {
                    "success": True,
                    "message": "Order already synced.",
                    "offline_order_id": offline_order.id,
                    "uuid": str(offline_order.uuid),
                    "status": offline_order.status,
                    "odoo_order_id": offline_order.odoo_order_id,
                    "odoo_order_name": offline_order.odoo_order_name,
                },
                status=status.HTTP_200_OK,
            )

        try:
            payload = offline_order.payload

            result = service.create_order(
                customer_id=payload["customer_id"],
                items=payload["items"],
            )

            offline_order.status = OfflineSalesOrder.STATUS_SYNCED
            offline_order.odoo_order_id = result.get("order_id")
            offline_order.odoo_order_name = result.get("name")
            offline_order.error_message = None
            offline_order.synced_at = timezone.now()
            offline_order.save()

            return Response(
                {
                    "success": True,
                    "message": "Order synced successfully.",
                    "offline_order_id": offline_order.id,
                    "uuid": str(offline_order.uuid),
                    "status": offline_order.status,
                    "odoo_order_id": offline_order.odoo_order_id,
                    "odoo_order_name": offline_order.odoo_order_name,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            offline_order.status = OfflineSalesOrder.STATUS_FAILED
            offline_order.error_message = str(e)
            offline_order.save()

            return Response(
                {
                    "success": False,
                    "message": "Order sync failed.",
                    "offline_order_id": offline_order.id,
                    "uuid": str(offline_order.uuid),
                    "status": offline_order.status,
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class OfflineSalesOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant = request.user.salesagent.tenant

        queryset = OfflineSalesOrder.objects.filter(
            tenant=tenant
        ).select_related("tenant", "sales_agent__user").order_by("-created_at")

        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        sales_agent_id = request.query_params.get("sales_agent_id")
        if sales_agent_id:
            queryset = queryset.filter(sales_agent_id=sales_agent_id)

        tenant_id = request.query_params.get("tenant_id")
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        created_from = request.query_params.get("created_from")
        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)

        created_to = request.query_params.get("created_to")
        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)

        uuid_param = request.query_params.get("uuid")
        if uuid_param:
            queryset = queryset.filter(uuid=uuid_param)

        customer_id = request.query_params.get("customer_id")
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        total_count = queryset.count()

        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)

        try:
            page = int(page)
            if page < 1:
                page = 1
        except (TypeError, ValueError):
            page = 1

        try:
            page_size = int(page_size)
            if page_size < 1:
                page_size = 10
            if page_size > 100:
                page_size = 100
        except (TypeError, ValueError):
            page_size = 10

        start = (page - 1) * page_size
        end = start + page_size

        paginated_queryset = queryset[start:end]

        serializer = OfflineSalesOrderListSerializer(paginated_queryset, many=True)

        return Response(
            {
                "count": total_count,
                "page": page,
                "page_size": page_size,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from accounts.services import resolve_sales_agent_context
from .models import OfflineSalesOrder, OdooConnection
from .services import OdooService
from .serializers import (
    BulkSyncOrdersSerializer,
    CreateOrderSerializer,
    OfflineSalesOrderListSerializer,
)


def _sync_offline_order_to_odoo(offline_order, service):
    if offline_order.status == OfflineSalesOrder.STATUS_SYNCED:
        return {
            "status": "skipped",
            "message": "Order already synced.",
            "odoo_order_id": offline_order.odoo_order_id,
            "odoo_order_name": offline_order.odoo_order_name,
        }

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

        return {
            "status": "success",
            "message": "Order synced successfully.",
            "odoo_order_id": offline_order.odoo_order_id,
            "odoo_order_name": offline_order.odoo_order_name,
        }
    except Exception:
        offline_order.status = OfflineSalesOrder.STATUS_FAILED
        offline_order.error_message = "Unable to sync order."
        offline_order.save()
        return {
            "status": "failed",
            "message": "Unable to sync order.",
        }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_products_view(request):
    ctx = resolve_sales_agent_context(request.user)
    service = OdooService(ctx.tenant)
    products = service.get_products()

    return Response({"products": products})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_customers_view(request):
    ctx = resolve_sales_agent_context(request.user)

    search = request.query_params.get("search")
    if search is not None:
        search = search.strip() or None

    page_raw = request.query_params.get("page", "1")
    page_size_raw = request.query_params.get("page_size", "10")

    try:
        page = int(page_raw)
    except (TypeError, ValueError):
        return Response({"detail": "Invalid page."}, status=status.HTTP_400_BAD_REQUEST)
    if page < 1:
        return Response({"detail": "Invalid page."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        page_size = int(page_size_raw)
    except (TypeError, ValueError):
        return Response({"detail": "Invalid page_size."}, status=status.HTTP_400_BAD_REQUEST)
    if page_size < 1 or page_size > 100:
        return Response({"detail": "Invalid page_size."}, status=status.HTTP_400_BAD_REQUEST)

    offset = (page - 1) * page_size
    limit = page_size

    try:
        service = OdooService(ctx.tenant)
    except OdooConnection.DoesNotExist:
        return Response(
            {"detail": "Odoo connection not configured for this tenant."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        data = service.get_customers(search=search, limit=limit, offset=offset)
    except Exception:
        return Response(
            {"detail": "Unable to fetch customers from Odoo."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(
        {
            "count": data["count"],
            "page": page,
            "page_size": page_size,
            "results": data["results"],
        },
        status=status.HTTP_200_OK,
    )


class OdooCreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = resolve_sales_agent_context(request.user)
        tenant = ctx.tenant
        sales_agent = ctx.sales_agent

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
        ctx = resolve_sales_agent_context(request.user)
        tenant = ctx.tenant
        sales_agent = ctx.sales_agent
        service = OdooService(tenant)

        offline_order = get_object_or_404(
            OfflineSalesOrder,
            uuid=order_uuid,
            tenant=tenant,
            sales_agent=sales_agent,
        )

        sync_result = _sync_offline_order_to_odoo(offline_order, service)
        is_success = sync_result["status"] in {"success", "skipped"}

        response_data = {
            "success": is_success,
            "message": sync_result["message"],
            "offline_order_id": offline_order.id,
            "uuid": str(offline_order.uuid),
            "status": offline_order.status,
            "odoo_order_id": offline_order.odoo_order_id,
            "odoo_order_name": offline_order.odoo_order_name,
        }
        if sync_result["status"] == "failed":
            response_data["error"] = sync_result["message"]

        return Response(
            response_data,
            status=status.HTTP_200_OK if is_success else status.HTTP_400_BAD_REQUEST,
        )


class BulkSyncOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BulkSyncOrdersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = resolve_sales_agent_context(request.user)
        tenant = ctx.tenant
        sales_agent = ctx.sales_agent

        try:
            service = OdooService(tenant)
        except OdooConnection.DoesNotExist:
            return Response(
                {"detail": "Odoo connection not configured for this tenant."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order_uuids = serializer.validated_data["order_uuids"]
        scoped_orders = OfflineSalesOrder.objects.filter(
            uuid__in=order_uuids,
            tenant=tenant,
            sales_agent=sales_agent,
        )
        orders_by_uuid = {str(o.uuid): o for o in scoped_orders}

        results = []
        for requested_uuid in order_uuids:
            requested_uuid_str = str(requested_uuid)
            offline_order = orders_by_uuid.get(requested_uuid_str)

            if offline_order is None:
                results.append(
                    {
                        "order_uuid": requested_uuid_str,
                        "status": "failed",
                        "message": "Order not found in your scope.",
                    }
                )
                continue

            sync_result = _sync_offline_order_to_odoo(offline_order, service)
            item = {
                "order_uuid": requested_uuid_str,
                "status": sync_result["status"],
                "message": sync_result["message"],
            }
            if sync_result["status"] == "success":
                item["odoo_order_id"] = offline_order.odoo_order_id
            results.append(item)

        return Response(
            {
                "total_requested": len(order_uuids),
                "total_processed": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class OfflineSalesOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ctx = resolve_sales_agent_context(request.user)
        tenant = ctx.tenant

        queryset = OfflineSalesOrder.objects.filter(
            tenant=tenant
        ).select_related("tenant", "sales_agent__user").order_by("-created_at")

        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Phase 1 strict rule: never trust agent_id / tenant_id from client requests.

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
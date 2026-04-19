from rest_framework import serializers

from .models import OfflineSalesOrder


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.FloatField()
    unit_price = serializers.FloatField()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Unit price cannot be negative.")
        return value


class CreateOrderSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Items list cannot be empty.")
        return value


class BulkSyncOrdersSerializer(serializers.Serializer):
    order_uuids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
    )


class OfflineSalesOrderListSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    sales_agent_name = serializers.CharField(
        source="sales_agent.user.username",
        read_only=True,
    )

    class Meta:
        model = OfflineSalesOrder
        fields = [
            "id",
            "uuid",
            "tenant",
            "tenant_name",
            "sales_agent",
            "sales_agent_name",
            "customer_id",
            "status",
            "odoo_order_id",
            "odoo_order_name",
            "error_message",
            "created_at",
            "synced_at",
        ]
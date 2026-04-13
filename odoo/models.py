from django.db import models
from core.models import Tenant
import uuid
from django.conf import settings




class OdooConnection(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE)
    base_url = models.URLField()
    database = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.database}"





class OfflineSalesOrder(models.Model):
    STATUS_PENDING = "pending"
    STATUS_SYNCED = "synced"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SYNCED, "Synced"),
        (STATUS_FAILED, "Failed"),
    ]

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="offline_sales_orders",
    )
    sales_agent = models.ForeignKey(
        "accounts.SalesAgent",
        on_delete=models.CASCADE,
        related_name="offline_sales_orders",
    )

    customer_id = models.IntegerField()
    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    odoo_order_id = models.IntegerField(null=True, blank=True)
    odoo_order_name = models.CharField(max_length=100, null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.uuid} - {self.status}"
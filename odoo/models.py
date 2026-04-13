from django.db import models
from core.models import Tenant




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
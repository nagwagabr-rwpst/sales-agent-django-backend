import xmlrpc.client

from .models import OdooConnection


class OdooService:
    def __init__(self, tenant):
        self.tenant = tenant

        connection = OdooConnection.objects.get(tenant=tenant, is_active=True)

        self.url = connection.base_url
        self.db = connection.database
        self.username = connection.username
        self.password = connection.password

        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

        self.uid = self.authenticate()

    def authenticate(self):
        uid = self.common.authenticate(
            self.db,
            self.username,
            self.password,
            {}
        )
        return uid

    def get_products(self):
        products = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "product.product",
            "search_read",
            [[]],
            {
                "fields": ["id", "name", "list_price"],
                "limit": 10,
            },
        )
        return products
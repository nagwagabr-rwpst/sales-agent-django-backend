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

    def get_products(self, limit=10, offset=0):
        """List products from Odoo. Defaults match the public API (first 10)."""
        products = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "product.product",
            "search_read",
            [[]],
            {
                "fields": ["id", "name", "list_price"],
                "limit": limit,
                "offset": offset,
            },
        )
        return products

    def count_products(self) -> int:
        """Total product.product rows (no domain filter), for admin/support pagination."""
        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "product.product",
            "search_count",
            [[]],
        )

    def get_customers(
        self,
        *,
        search: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        """
        Fetch customers (res.partner) with optional name search and pagination.
        Domain: partners with customer_rank > 0 (Odoo 14+).
        Returns: {"count": int, "results": list[dict]}
        """
        domain: list = [("customer_rank", ">", 0)]
        if search:
            term = search.strip()
            if term:
                domain = [
                    "&",
                    ("customer_rank", ">", 0),
                    ("name", "ilike", f"%{term}%"),
                ]

        total_count = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search_count",
            [domain],
        )

        records = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "res.partner",
            "search_read",
            [domain],
            {
                "fields": ["id", "name", "phone", "email"],
                "limit": limit,
                "offset": offset,
            },
        )

        results = []
        for r in records:
            results.append(
                {
                    "id": r.get("id"),
                    "name": r.get("name") if r.get("name") is not False else "",
                    "phone": r.get("phone") if r.get("phone") is not False else "",
                    "email": r.get("email") if r.get("email") is not False else "",
                }
            )

        return {"count": total_count, "results": results}

    def create_order(self, customer_id: int, items: list[dict]) -> dict:
        order_id = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            'sale.order',
            'create',
            [{
                'partner_id': customer_id,
            }]
        )

        for item in items:
            self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'sale.order.line',
                'create',
                [{
                    'order_id': order_id,
                    'product_id': item['product_id'],
                    'product_uom_qty': item['quantity'],
                    'price_unit': item['unit_price'],
                }]
            )

        order_data = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            'sale.order',
            'read',
            [[order_id]],
            {'fields': ['id', 'name']}
        )

        order_name = order_data[0].get('name') if order_data else None

        return {
            'success': True,
            'order_id': order_id,
            'name': order_name,
        }
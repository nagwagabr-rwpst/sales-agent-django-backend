class OdooService:

    def __init__(self, tenant):
        self.tenant = tenant

    def get_products(self):
        print(f"Fetching products for tenant: {self.tenant}")
        return []
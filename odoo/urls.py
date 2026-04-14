from django.urls import path
from .views import (
    get_customers_view,
    get_products_view,
    OdooCreateOrderView,
    OfflineSalesOrderListView,
    SyncOrdersView,
)


urlpatterns = [
    path("products/", get_products_view),
    path("customers/", get_customers_view, name="odoo-customers"),
    path("orders/", OdooCreateOrderView.as_view(), name="odoo-create-order"),
    path("sync-orders/<uuid:order_uuid>/", SyncOrdersView.as_view(), name="sync-order-by-uuid"),
    path("offline-orders/", OfflineSalesOrderListView.as_view(), name="offline-orders-list"),
]
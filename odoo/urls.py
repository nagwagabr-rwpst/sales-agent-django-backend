from django.urls import path
from .views import get_products_view, OdooCreateOrderView, SyncOrdersView,OfflineSalesOrderListView


urlpatterns = [
    path("products/", get_products_view),
    path("orders/", OdooCreateOrderView.as_view(), name="odoo-create-order"),
    path("sync-orders/<uuid:order_uuid>/", SyncOrdersView.as_view(), name="sync-order-by-uuid"),
    path("offline-orders/", OfflineSalesOrderListView.as_view(), name="offline-orders-list"),
]
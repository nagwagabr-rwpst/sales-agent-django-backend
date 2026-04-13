from django.urls import path
from .views import get_products_view
from .views import OdooCreateOrderView


urlpatterns = [
    path("products/", get_products_view),
    path('orders/', OdooCreateOrderView.as_view(), name='odoo-create-order'),

]
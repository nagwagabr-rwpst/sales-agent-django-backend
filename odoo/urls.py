from django.urls import path
from .views import get_products_view

urlpatterns = [
    path("products/", get_products_view),
]
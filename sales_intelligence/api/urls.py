from django.urls import path

from .views import CustomerPrioritiesView


urlpatterns = [
    path("customers/priorities", CustomerPrioritiesView.as_view(), name="customer-priorities"),
]

from django.urls import path
from . import views

app_name = "drivers"

urlpatterns = [
    path("", views.DriverListView.as_view(), name="drivers_view"),
    path("create/", views.DriverCreateView.as_view(), name="driver_create"),
    path("<int:pk>/update/", views.DriverUpdateView.as_view(), name="driver_update"),
    path("<int:pk>/delete/", views.DriverDeleteView.as_view(), name="driver_delete"),
]
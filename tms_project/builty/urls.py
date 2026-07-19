from django.urls import path

from . import views


app_name = "builty"


urlpatterns = [
    path("", views.BuiltyListView.as_view(), name="builty_list"),
    path("create/", views.BuiltyCreateView.as_view(), name="builty_create"),
    path(
        "<int:pk>/update/",
        views.BuiltyUpdateView.as_view(),
        name="builty_update",
    ),
    path(
        "<int:pk>/detail/",
        views.BuiltyDetailView.as_view(),
        name="builty_detail",
    ),
    path(
        "<int:pk>/cancel/",
        views.BuiltyCancelView.as_view(),
        name="builty_cancel",
    ),
    path(
        "customer-search/",
        views.CustomerSearchView.as_view(),
        name="customer-search",
    ),
    path(
        "vehicle-search/",
        views.VehicleSearchView.as_view(),
        name="vehicle-search",
    ),
    path(
        "driver-search/",
        views.DriverSearchView.as_view(),
        name="driver-search",
    ),
]

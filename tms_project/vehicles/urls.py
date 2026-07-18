from django.urls import path

from . import views


app_name = "vehicles"


urlpatterns = [
    path(
        "",
        views.VehicleListView.as_view(),
        name="vehicles_view",
    ),

    path(
        "create/",
        views.VehicleCreateView.as_view(),
        name="vehicle_create",
    ),

    path(
        "<int:pk>/update/",
        views.VehicleUpdateView.as_view(),
        name="vehicle_update",
    ),

    path(
        "<int:pk>/delete/",
        views.VehicleDeleteView.as_view(),
        name="vehicle_delete",
    ),

    path(
        "<int:pk>/detail/",
        views.VehicleDetailView.as_view(),
        name="vehicle_detail",
    ),

    path(
        "<int:pk>/depreciation/",
        views.VehicleDepreciationView.as_view(),
        name="vehicle_depreciation",
    ),
]
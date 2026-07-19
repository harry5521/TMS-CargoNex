from django.urls import path

from . import views


app_name = "trips"


urlpatterns = [
    path("", views.TripListView.as_view(), name="trip_list"),
    path("assign/", views.TripAssignView.as_view(), name="trip_assign"),
    path(
        "unassigned-builty-search/",
        views.UnassignedBuiltySearchView.as_view(),
        name="unassigned_builty_search",
    ),
    path("<int:pk>/detail/", views.TripDetailView.as_view(), name="trip_detail"),
    path("<int:pk>/start/", views.TripStartView.as_view(), name="trip_start"),
    path(
        "<int:pk>/complete/",
        views.TripCompleteView.as_view(),
        name="trip_complete",
    ),
    path(
        "<int:trip_pk>/expenses/create/",
        views.TripExpenseCreateView.as_view(),
        name="expense_create",
    ),
    path(
        "expenses/<int:pk>/update-title/",
        views.TripExpenseTitleUpdateView.as_view(),
        name="expense_update_title",
    ),
]

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payments_view'),
    path('payment-create/', views.PaymentCreateView.as_view(), name='payment_create'),


    # builty searchable function path
    path("search-builties/", views.search_builties, name="search-builties"),
]

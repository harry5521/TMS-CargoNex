from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='customers-list'),
    path('create/', views.CustomerFormView.as_view(), name='customer-create'),
    path('edit/<int:pk>/', views.CustomerUpdateView.as_view(), name='customer-edit'),
]
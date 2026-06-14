from django.urls import path
from . import views

app_name = 'builty'

urlpatterns = [
    path('', views.BuiltyListView.as_view(), name='builty_list'),
    path('create/', views.BuiltyCreateView.as_view(), name='builty_create'),


    path('customer-search/', views.CustomerSearchView.as_view(), name='customer-search')
]
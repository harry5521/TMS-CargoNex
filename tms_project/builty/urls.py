from django.urls import path
from . import views

app_name = 'builty'

urlpatterns = [
    path('', views.BuiltyListView.as_view(), name='builty_list'),
]
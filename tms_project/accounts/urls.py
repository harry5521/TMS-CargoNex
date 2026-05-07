from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('accounts/', views.AccountsView.as_view(), name='accounts'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
]
from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('', views.AccountsView.as_view(), name='accounts'),
    path('categories/save/', views.TransactionCategorySaveView.as_view(), name='category-save'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('payments/', views.PaymentsView.as_view(), name='payments'),
]
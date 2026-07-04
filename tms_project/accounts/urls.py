from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('', views.AccountsView.as_view(), name='accounts'),
    path('categories/save/', views.TransactionCategorySaveView.as_view(), name='category-save'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction-create'),

    # General Expenses urls
    path('expenses/', views.GeneralExpensesView.as_view(), name='general-expenses'),

]
from django.shortcuts import render
from django.views import View

# Create your views here.

class AccountsView(View):
    def get(self, request):
        return render(request, 'accounts/accounts.html')
    
class PaymentsView(View):
    def get(self, request):
        return render(request, 'accounts/payments.html')


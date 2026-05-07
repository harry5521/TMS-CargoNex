from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import NoCacheMixin

# Create your views here.

class DashboardView(LoginRequiredMixin, NoCacheMixin, View):
    def get(self, request):
        return render(request, 'dashboard/dashboard.html')
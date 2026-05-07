from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User
from core.mixins import NoCacheMixin

# Create your views here.

class LoginView(NoCacheMixin, View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        
        return render(request, 'authsystem/login.html')
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, f'You have logged in as User {user.username}.')
            # print(f'User {user.username} logged in successfully.')
            return redirect('core:dashboard')
    
        messages.error(request, 'Invalid username or password.')
        # print(f'Failed login attempt with username: {username}')
        return redirect('authsystem:login')

    
class LogoutView(LoginRequiredMixin, NoCacheMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('authsystem:login')
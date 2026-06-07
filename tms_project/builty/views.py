from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import Builty

# Create your views here.

class BuiltyListView(ListView):
    model = Builty
    template_name = 'operations/builty_lr.html'
    context_object_name = 'builty_list'
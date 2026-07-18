"""
URL configuration for tms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('tms/admin/', admin.site.urls),
    path('tms/auth/', include('authsystem.urls')),
    path('tms/', include('core.urls')),
    path('tms/customers/', include('customers.urls')),
    path('tms/builty/', include('builty.urls')),
    path('tms/accounts/', include('accounts.urls')),
    path('tms/payments/', include('payments.urls')),
    path("tms/drivers/", include("drivers.urls")),
    path("tms/vehicles/", include("vehicles.urls")),
]

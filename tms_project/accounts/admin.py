from django.contrib import admin
from .models import TransactionCategory, Transaction

# Register your models here.
admin.site.register(TransactionCategory)
admin.site.register(Transaction)
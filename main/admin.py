from django.contrib import admin
from .models import Instrument, InstrumentType, Account, Transaction

@admin.register(InstrumentType)
class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'instrument_type', 'current_price')
    list_filter = ('instrument_type',)
    search_fields = ('symbol', 'name')

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'transaction_type', 'volume', 'instrument', 'price', 'account')
    list_filter = ('transaction_type', 'date', 'account')

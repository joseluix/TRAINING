from django.db import models
from django.contrib.auth.models import User

class InstrumentType(models.Model):
    name = models.CharField(max_length=50, unique=True) # e.g. "Forex", "Stock", "Crypto"
    description = models.TextField(blank=True)
    
    # Future placeholders for calculation logic
    # lot_size_multiplier = ...
    # pip_value_calculation = ...

    def __str__(self):
        return self.name

class Instrument(models.Model):
    # ... (previous code)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True)
    current_price = models.DecimalField(max_digits=18, decimal_places=8) # Updated precision
    
    # Link to the dynamic type definition
    instrument_type = models.ForeignKey(InstrumentType, on_delete=models.PROTECT, related_name='instruments')
    
    # Instance specific data
    contract_size = models.DecimalField(max_digits=12, decimal_places=2, default=1.0)
    digits = models.IntegerField(default=2, help_text="Number of decimal places (e.g. 5 for EURUSD)") 
    quote_currency = models.CharField(max_length=10, blank=True, null=True)
    base_currency = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.symbol} ({self.instrument_type.name}) - {self.name}"

class Position(models.Model):
    id = models.AutoField(primary_key=True)
    account = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='positions')
    instrument = models.ForeignKey(Instrument, on_delete=models.PROTECT, related_name='positions')
    
    # Net Position Fields
    volume = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    average_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    
    is_open = models.BooleanField(default=True) # True if volume != 0
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "OPEN" if self.volume != 0 else "CLOSED"
        return f"POS-{self.id} {self.instrument.symbol} {self.volume} @ {self.average_price} [{status}]"

class TransactionType(models.Model):
    code = models.IntegerField(unique=True) # e.g. 100, 000
    name = models.CharField(max_length=50) # e.g. "Deposit", "Buy"
    category = models.CharField(max_length=20) # e.g. "Balance", "Trading"
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0.00) # Increased precision
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username}) - ${self.balance}"

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    
    # Common fields
    volume = models.DecimalField(max_digits=18, decimal_places=8, default=0) # Renamed from shares
    price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    
    date = models.DateTimeField(auto_now_add=True)

    # New Fields for Service Architecture
    commission = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    status = models.CharField(max_length=20, default='pending') # pending, completed, failed
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')

    def __str__(self):
        code = self.instrument.symbol if self.instrument else "CASH"
        return f"{self.transaction_type.name.upper()} {self.volume} {code} @ {self.price} [Status: {self.status}]"

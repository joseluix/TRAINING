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

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0.00) # Increased precision
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username}) - ${self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Common fields
    volume = models.DecimalField(max_digits=18, decimal_places=8, default=0) # Renamed from shares
    price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        code = self.instrument.symbol if self.instrument else "CASH"
        return f"{self.transaction_type.upper()} {self.volume} {code} @ {self.price}"

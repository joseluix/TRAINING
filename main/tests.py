from django.test import TestCase
from django.contrib.auth.models import User
from .models import Instrument, InstrumentType, Account, Transaction

class ModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create Instrument Type
        self.fx_type = InstrumentType.objects.create(name="Forex")
        
        # Create Instrument
        self.eurusd = Instrument.objects.create(
            symbol="EURUSD",
            name="Euro vs US Dollar",
            current_price=1.05,
            instrument_type=self.fx_type,
            contract_size=100000,
            quote_currency='USD',
            base_currency='EUR'
        )

    def test_account_creation(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        self.assertEqual(account.balance, 0.00)
        self.assertEqual(str(account), f"Main Trading Setup (testuser) - $0.00")

    def test_deposit_transaction(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        
        # Create Deposit
        dep = Transaction.objects.create(
            account=account,
            transaction_type='deposit',
            price=10000.00,
            volume=0
        )
        
        self.assertEqual(dep.transaction_type, 'deposit')
        self.assertIsNone(dep.instrument)
        self.assertEqual(str(dep), "DEPOSIT 0 CASH @ 10000.00") # Decimal precision will be higher now

    def test_buy_transaction(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        
        # Create Buy
        buy = Transaction.objects.create(
            account=account,
            instrument=self.eurusd,
            transaction_type='buy',
            volume=1.0, 
            price=1.0500
        )
        
        self.assertEqual(buy.transaction_type, 'buy')
        self.assertEqual(buy.instrument, self.eurusd)
        self.assertEqual(str(buy), "BUY 1.0 EURUSD @ 1.05000000")

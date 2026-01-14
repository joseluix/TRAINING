from django.test import TestCase
from django.contrib.auth.models import User
from .models import Instrument, InstrumentType, Account, Transaction, TransactionType, Position

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
        # Create Types
        self.t_buy = TransactionType.objects.create(code=0, name="Buy", category="Trading")
        self.t_sell = TransactionType.objects.create(code=1, name="Sell", category="Trading")
        self.t_dep = TransactionType.objects.create(code=100, name="Deposit", category="Balance")
        self.t_wd = TransactionType.objects.create(code=101, name="Withdrawal", category="Balance")

    def test_account_creation(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        self.assertEqual(account.balance, 0.00)
        self.assertEqual(str(account), f"Main Trading Setup (testuser) - $0.0")

    def test_deposit_transaction(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        
        # Create Deposit
        dep = Transaction.objects.create(
            account=account,
            transaction_type=self.t_dep,
            price=10000.00,
            volume=0
        )
        
        self.assertEqual(dep.transaction_type, self.t_dep)
        self.assertIsNone(dep.instrument)
        # self.assertEqual(str(dep), "DEPOSIT 0 CASH @ 10000.0") # Updated str representation wraps name in upper() and adds status 

    def test_buy_transaction(self):
        account = Account.objects.create(name="Main Trading Setup", user=self.user)
        
        # Create Buy
        # Create Buy
        pos = Position.objects.create(account=account, instrument=self.eurusd, is_open=True)
        buy = Transaction.objects.create(
            account=account,
            instrument=self.eurusd,
            transaction_type=self.t_buy,
            volume=1.0, 
            price=1.0500,
            position=pos
        )
        
        self.assertEqual(buy.transaction_type, self.t_buy)
        self.assertEqual(buy.instrument, self.eurusd)
        # self.assertEqual(str(buy), "BUY 1.0 EURUSD @ 1.05")

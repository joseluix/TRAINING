from django.test import TestCase
from django.contrib.auth.models import User
from .models import Account, Instrument, InstrumentType, Transaction, TransactionType
from .services import BalanceService, TradingService
from decimal import Decimal

class ServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pw')
        self.account = Account.objects.create(name="Test Account", user=self.user)
        self.fx_type = InstrumentType.objects.create(name="Forex")
        self.eurusd = Instrument.objects.create(
            symbol="EURUSD", 
            name="Euro", 
            current_price=1.1, 
            instrument_type=self.fx_type
        )
        # Create required types
        self.t_buy = TransactionType.objects.create(code=0, name="Buy", category="Trading")
        self.t_sell = TransactionType.objects.create(code=1, name="Sell", category="Trading")
        self.t_dep = TransactionType.objects.create(code=100, name="Deposit", category="Balance")
        self.t_wd = TransactionType.objects.create(code=101, name="Withdrawal", category="Balance")

    def test_balance_service_deposit(self):
        BalanceService.deposit(self.account.id, 100)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 100)
        
        # Check Transaction Record
        tx = Transaction.objects.last()
        self.assertEqual(tx.transaction_type, self.t_dep)
        self.assertEqual(tx.price, 100)

    def test_balance_service_withdraw_fail(self):
        with self.assertRaises(ValueError):
            BalanceService.withdraw(self.account.id, 100) # Balance is 0

    def test_trading_service_buy(self):
        # 1. Deposit Funds
        BalanceService.deposit(self.account.id, 1000)
        
        # 2. Execute Buy
        tx = TradingService.execute_trade(
            self.account.id, 
            "EURUSD", 
            "buy", 
            volume=100, 
            price_limit=1.1
        )
        
        self.account.refresh_from_db()
        
        # Cost = 100 * 1.1 = 110. Balance should be 1000 - 110 = 890
        self.assertEqual(self.account.balance, 890)
        self.assertEqual(tx.transaction_type, self.t_buy)
        self.assertEqual(tx.volume, 100)
        self.assertEqual(tx.price, Decimal('1.1'))

    def test_trading_service_insufficient_funds(self):
        # Balance 0
        with self.assertRaises(ValueError): # Should bubble up from BalanceService
            TradingService.execute_trade(
                self.account.id, "EURUSD", "buy", volume=1000, price_limit=1.1
            )

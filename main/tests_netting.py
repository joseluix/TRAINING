from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Account, Instrument, InstrumentType, TransactionType, Position
from .services import BalanceService, TradingService

class NettingTests(TestCase):
    def setUp(self):
        # Ensure TransactionTypes exist FIRST
        TransactionType.objects.get_or_create(code=0, defaults={'name': 'Buy', 'category': 'Trading'})
        TransactionType.objects.get_or_create(code=1, defaults={'name': 'Sell', 'category': 'Trading'})
        TransactionType.objects.get_or_create(code=100, defaults={'name': 'Deposit', 'category': 'Balance'})
        TransactionType.objects.get_or_create(code=101, defaults={'name': 'Withdraw', 'category': 'Balance'})

        # Setup Data
        self.user = User.objects.create_user(username='nettester', password='pw')
        self.account = Account.objects.create(name="Net Account", user=self.user)
        BalanceService.deposit(self.account.id, 10000) # Plenty of cash
        
        self.inst_type = InstrumentType.objects.create(name="Crypto")
        self.eth = Instrument.objects.create(
            symbol="ETHUSD", 
            name="Ethereum", 
            current_price=100, 
            instrument_type=self.inst_type
        )

    def test_long_accumulation(self):
        """Test simple Buy then Buy (Averaging)"""
        # 1. Buy 10 @ 100
        TradingService.execute_trade(self.account.id, "ETHUSD", "buy", 10, 100)
        pos = Position.objects.get(account=self.account, instrument=self.eth)
        self.assertEqual(pos.volume, 10)
        self.assertEqual(pos.average_price, 100)
        
        # 2. Buy 10 @ 110
        # Avg should be (1000 + 1100) / 20 = 105
        TradingService.execute_trade(self.account.id, "ETHUSD", "buy", 10, 110)
        pos.refresh_from_db()
        self.assertEqual(pos.volume, 20)
        self.assertEqual(pos.average_price, 105)

    def test_long_partial_close(self):
        """Test Buy then Partial Sell (Realize PnL)"""
        # 1. Buy 20 @ 100
        TradingService.execute_trade(self.account.id, "ETHUSD", "buy", 20, 100)
        
        # 2. Sell 10 @ 120 (Profit should be (120-100)*10 = 200)
        # Account Balance before: 10000 - 2000 = 8000
        # Account Balance after: 8000 + (120*10) = 9200? 
        # Wait, the logic is: Sell proceeds = 1200. Cost Basis release = 1000. Realized PnL = 200.
        # In Spot, you get the Cash. So Balance += 1200.
        
        TradingService.execute_trade(self.account.id, "ETHUSD", "sell", 10, 120)
        
        pos = Position.objects.get(account=self.account, instrument=self.eth)
        self.assertEqual(pos.volume, 10) # 20 - 10
        self.assertEqual(pos.average_price, 100) # Avg price doesn't change on reduction!
        
        self.account.refresh_from_db()
        # Verify Balance. 
        # Start 10000. Buy 2000. Bal 8000.
        # Sell 10 @ 120 = 1200. Bal 9200.
        self.assertEqual(self.account.balance, 9200)

    def test_flip_long_to_short(self):
        """Test Long 10, Sell 15 -> Short 5"""
        # 1. Buy 10 @ 100 (Cost 1000)
        TradingService.execute_trade(self.account.id, "ETHUSD", "buy", 10, 100)
        
        # 2. Sell 15 @ 110
        # - Close 10 @ 110 (Profit 100) -> Proceeds 1100.
        # - Open Short 5 @ 110 -> "Cost" or Margin Check. 
        # In our simplified logic: Shorting just sets volume neg, basic margin/fee logic.
        # Cashflow:
        #  - Get 1100 for the closed part.
        #  - What about the Short 5? Does it generate cash? (Selling borrowed stock).
        #    Usually Shorting GIVES you cash (Proceeds) but locks it as Collateral.
        #    Our current logic says:
        #    Else (flip): 
        #       - Close 10 part: Proceeds 1100.
        #       - Open 5 part: Proceeds 550?
        #       - Total Credit from Sell = 15 * 110 = 1650.
        #       - We deposited 1650.
        
        TradingService.execute_trade(self.account.id, "ETHUSD", "sell", 15, 110)
        
        pos = Position.objects.get(account=self.account, instrument=self.eth)
        self.assertEqual(pos.volume, -5)
        self.assertEqual(pos.average_price, 110)
        
        self.account.refresh_from_db()
        # Start 10000. Buy 1000 -> 9000.
        # Sell 15 @ 110:
        # - Close 10 part: Profit 100 -> Proceeds 1100. (9000 + 1100 = 10100)
        # - Open 5 part (Short): Cost 0.
        # Total Balance: 10100.
        self.assertEqual(self.account.balance, 10100)

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Account, Instrument, InstrumentType, TransactionType
from .services import BalanceService

class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apitest', password='pw')
        self.client.force_authenticate(user=self.user)
        
        self.account = Account.objects.create(name="API Account", user=self.user)
        self.inst_type = InstrumentType.objects.create(name="Forex")
        self.eurusd = Instrument.objects.create(
            symbol="EURUSD", name="Euro", current_price=1.1, instrument_type=self.inst_type
        )
        
        # Ensure Types exist
        TransactionType.objects.get_or_create(code=100, defaults={'name': 'Deposit', 'category': 'Balance'})
        TransactionType.objects.get_or_create(code=101, defaults={'name': 'Withdraw', 'category': 'Balance'})
        TransactionType.objects.get_or_create(code=0, defaults={'name': 'Buy', 'category': 'Trading'})
        
    def test_deposit(self):
        url = f'/api/accounts/{self.account.id}/deposit/'
        response = self.client.post(url, {'amount': 1000}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['balance']), 1000.0)

    def test_trade_flow(self):
        # 1. Deposit
        BalanceService.deposit(self.account.id, 200)
        
        # 2. Trade
        url = '/api/trading/'
        payload = {
            'account_id': self.account.id,
            'instrument_symbol': 'EURUSD',
            'direction': 'buy',
            'volume': 100,
            'price_limit': 1.1
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Cost = 100 * 1.1 = 110. Bal 200 - 110 = 90.
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 90)

    def test_trade_validation_error(self):
        url = '/api/trading/'
        payload = {
            # Missing volume
            'account_id': self.account.id,
            'instrument_symbol': 'EURUSD',
            'direction': 'buy',
            'price_limit': 1.1
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Account, Transaction
from .serializers import AccountSerializer, TradeActionSerializer, TransactionSerializer
from .services import BalanceService, TradingService

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Accounts and performing Balance operations.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users see only their own accounts
        return Account.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        amount = request.data.get('amount')
        try:
            account = BalanceService.deposit(pk, amount)
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def withdraw(self, request, pk=None):
        amount = request.data.get('amount')
        try:
            account = BalanceService.withdraw(pk, amount)
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TradingViewSet(viewsets.ViewSet):
    """
    ViewSet for executing Trades.
    Not a ModelViewSet because "Trade" isn't a direct CRUD on a single model 
    (it touches Position, Transaction, Balance).
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        serializer = TradeActionSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                # We assume the account ID is passed or we default to the user's first account
                # For now, let's require account_id in the body or query param
                # OR, simpler: just use the first account found for the user (Training wheels)
                account_id = request.data.get('account_id')
                if not account_id:
                     # Fallback for ease of use
                     account = Account.objects.filter(user=request.user).first()
                     if not account:
                         return Response({'error': 'No account found'}, status=status.HTTP_400_BAD_REQUEST)
                     account_id = account.id

                tx = TradingService.execute_trade(
                    account_id=account_id,
                    instrument_symbol=data['instrument_symbol'],
                    direction=data['direction'],
                    volume=data['volume'],
                    price_limit=data['price_limit']
                )
                
                # We return the Transaction Record
                return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"System Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

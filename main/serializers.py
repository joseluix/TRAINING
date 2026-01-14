from rest_framework import serializers
from .models import Account, Transaction, Instrument
from .services import BalanceService, TradingService

class AccountSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for Account details.
    """
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance']
        read_only_fields = ['balance']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'date', 'transaction_type', 'instrument', 'volume', 'price', 'commission', 'status']
        depth = 1 # To show related names


class TradeActionSerializer(serializers.Serializer):
    """
    Serializer for validating Trade Execution inputs.
    Does not write directly to DB, but passes data to TradingService.
    """
    instrument_symbol = serializers.CharField(max_length=20)
    direction = serializers.ChoiceField(choices=[('buy', 'Buy'), ('sell', 'Sell')])
    volume = serializers.DecimalField(max_digits=20, decimal_places=8)
    price_limit = serializers.DecimalField(max_digits=20, decimal_places=8)

    def validate_volume(self, value):
        if value <= 0:
            raise serializers.ValidationError("Volume must be positive")
        return value

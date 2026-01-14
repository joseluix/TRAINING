from django.db import transaction, models
from .models import Account, Transaction, Instrument, TransactionType, Position
from decimal import Decimal

class BalanceService:
    @staticmethod
    def _get_account_locked(account_id):
        """
        Helper to get an account with a row lock (SELECT FOR UPDATE).
        This ensures no other transaction can modify this account until the
        current transaction block finishes.
        """
        return Account.objects.select_for_update().get(id=account_id)

    @classmethod
    def deposit(cls, account_id, amount, description="Deposit"):
        """
        Adds funds to an account.
        This is an ATOMIC operation.
        """
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        with transaction.atomic():
            account = cls._get_account_locked(account_id)
            account.balance += amount
            account.save()

            # Create the record
            # Fetch type (Assumes it exists, created via fixtures/migrations)
            t_type = TransactionType.objects.get(code=100) 
            
            Transaction.objects.create(
                account=account,
                transaction_type=t_type,
                volume=0,
                price=amount,
                status='completed'
            )
            return account

    @classmethod
    def withdraw(cls, account_id, amount, description="Withdrawal"):
        """
        Removes funds from an account.
        This is an ATOMIC operation with Check.
        """
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")

        with transaction.atomic():
            account = cls._get_account_locked(account_id)
            
            if account.balance < amount:
                raise ValueError(f"Insufficient funds: Balance {account.balance} < {amount}")
            
            account.balance -= amount
            account.save()

            # Create the record
            t_type = TransactionType.objects.get(code=101)
            
            Transaction.objects.create(
                account=account,
                transaction_type=t_type,
                volume=0,
                price=amount,
                status='completed'
            )
            return account

class TradingService:
    @staticmethod
    def calculate_commission(account, instrument, volume, price):
        """
        Placeholder for commission logic.
        Future: Load from UserGroup/CommissionProfile.
        """
        # Example: Flat $1 per trade for now, or 0
        return Decimal("0.00")

    @classmethod
    def execute_trade(cls, account_id, instrument_symbol, direction, volume, price_limit=None):
        """
        Executes a Trade using Net Position Logic.
        - Buy updates position (increases Long or reduces Short).
        - Sell updates position (increases Short or reduces Long).
        - PnL is realized only when reducing exposure.
        - Average Price is updated only when increasing exposure.
        """
        direction = direction.lower()
        if direction not in ['buy', 'sell']:
            raise ValueError("Invalid direction. Use 'buy' or 'sell'.")
            
        volume = Decimal(str(volume))
        if volume <= 0:
            raise ValueError("Volume must be positive")
        
        if price_limit is None:
             raise ValueError("Price must be provided for execution")
        price = Decimal(str(price_limit))

        # Atomic Transaction
        with transaction.atomic():
            # Lock Account
            account = BalanceService._get_account_locked(account_id)
            
            try:
                instrument = Instrument.objects.get(symbol=instrument_symbol)
            except Instrument.DoesNotExist:
                 raise ValueError(f"Instrument {instrument_symbol} not found")

            # Get or Create Position (Locking it would be ideal, select_for_update hard on create)
            # For strictness we usually lock the position if it exists.
            position, created = Position.objects.select_for_update().get_or_create(
                account=account, 
                instrument=instrument,
                defaults={'volume': 0, 'average_price': 0}
            )
            
            # Helper for direction
            trade_vol = volume if direction == 'buy' else -volume
            current_vol = position.volume
            
            # Commission (Simple placeholder)
            commission = cls.calculate_commission(account, instrument, volume, price)
            
            # Logic Branching
            # Case 1: Increasing Position (or Flat) -> No PnL, Update Avg Price
            # (Same sign or current is 0)
            if (current_vol == 0) or (current_vol > 0 and trade_vol > 0) or (current_vol < 0 and trade_vol < 0):
                
                # Logic: Total Value / Total Vol
                # New Avg = ((CurVol * CurAvg) + (TradeVol * TradePrice)) / (CurVol + TradeVol)
                
                total_vol = current_vol + trade_vol
                # Avoid div by zero (though case says total_vol != 0 unless both 0)
                if total_vol != 0:
                     new_avg = ((current_vol * position.average_price) + (trade_vol * price)) / total_vol
                     position.average_price = abs(new_avg) # Always positive price
                else:
                     position.average_price = 0
                
                position.volume = total_vol
                position.is_open = (position.volume != 0)
                position.save()
                
                # Money Move: Cost of Trade
                # If Buying, we PAY (Price * Vol). If Selling Short, we GAIN/HOLD Collateral?
                # For Spot, usually you pay full value. for Margin, margin.
                # Assuming SPOT for BUY, and ignoring Short-Selling Cashflow nuances for now (or simplified).
                # Simplified: Move Cash = Trade Cost. 
                cost = volume * price
                if direction == 'buy':
                    BalanceService.withdraw(account_id, cost + commission, f"Buy {instrument_symbol}")
                else:
                    # Short Selling usually locks margin. checking funds...
                    # For simple model, we might just check free margin.
                    # Letting sell go through without cash deduction (naked short?) or margin check is risky.
                    # Added basic logic: Fee only.
                    BalanceService.withdraw(account_id, commission, f"Short {instrument_symbol}")

                realized_pnl = 0

            # Case 2: Reducing / Closing / Flipping
            else:
                # Store state before changes
                was_long = current_vol > 0
                reduction_vol = min(abs(current_vol), abs(trade_vol))
                remaining_trade_vol = abs(trade_vol) - reduction_vol
                
                # Calculate PnL on the Reduced Portion
                # PnL = (ExitPrice - EntryPrice) * Vol * Direction
                pos_sign = 1 if current_vol > 0 else -1
                pnl = (price - position.average_price) * reduction_vol * pos_sign
                realized_pnl = pnl
                
                # Money Logic Handling
                # We handle the "Close" and "Open" parts separately to ensure correctness.
                
                # Part A: Closing the Existing Position (Partial or Full)
                balance_change_close = Decimal(0)
                
                if was_long:
                    # Closing Long: You sold the asset. You get Price * Vol.
                    balance_change_close = price * reduction_vol
                else:
                    # Closing Short: You bought back. 
                    # Since you didn't get cash when opening, you just settle PnL.
                    # e.g. Short @ 100, Buy @ 90. PnL +10. You get +10.
                    # e.g. Short @ 100, Buy @ 110. PnL -10. You lose -10.
                    balance_change_close = pnl

                # Part B: Opening the New Position (If Flip)
                balance_change_open = Decimal(0)
                if remaining_trade_vol > 0:
                    # We are opening a new position on the OTHER side.
                    # If we were Long, now Shorting.
                    # If we were Short, now Long.
                    
                    if was_long: # Now Shorting
                        # Opening Short: No cost (simplified).
                        balance_change_open = 0
                    else: # Now Buying (Long)
                        # Opening Long: Pay Full Cost.
                        balance_change_open = -(price * remaining_trade_vol)

                # Total Net Cash Move
                # Note: commission is always subtracted.
                net_balance_change = balance_change_close + balance_change_open - commission
                
                if net_balance_change > 0:
                    BalanceService.deposit(account_id, net_balance_change, f"Trade {instrument_symbol} (Close/Flip)")
                elif net_balance_change < 0:
                    BalanceService.withdraw(account_id, abs(net_balance_change), f"Trade {instrument_symbol} (Close/Flip)")
                
                # Update Volume & Price
                if remaining_trade_vol > 0:
                    # Flipped
                    new_side_vol = remaining_trade_vol if trade_vol > 0 else -remaining_trade_vol
                    position.volume = new_side_vol
                    position.average_price = price
                else:
                    # Reduced / Closed
                    if was_long:
                        position.volume -= reduction_vol
                    else:
                        position.volume += reduction_vol # -10 + 5 = -5
                        
                position.is_open = (position.volume != 0)
                position.save()

            # Record Transaction
            t_code = 0 if direction == 'buy' else 1
            try:
                t_type = TransactionType.objects.get(code=t_code)
            except:
                # Fallback or auto-create for dev
                t_type, _ = TransactionType.objects.get_or_create(code=t_code, defaults={'name': direction, 'category': 'Trading'})

            tx = Transaction.objects.create(
                account=account,
                instrument=instrument,
                transaction_type=t_type,
                volume=volume,
                price=price,
                commission=commission,
                status='completed',
                position=position
            )
            return tx

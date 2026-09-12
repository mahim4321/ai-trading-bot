"""Backtesting framework for strategy validation"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from app.services.market import get_market_dataframe
from app.services.indicators import add_indicators
from app.services.strategy import generate_signal
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtest trading strategies on historical data"""
    
    def __init__(
        self,
        initial_capital: float = 1000.0,
        risk_per_trade: float = 0.01,
        max_open_positions: int = 5
    ):
        """
        Initialize backtest engine
        
        Args:
            initial_capital: Starting capital
            risk_per_trade: Risk per trade (1% = 0.01)
            max_open_positions: Maximum concurrent positions
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.max_open_positions = max_open_positions
        
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = [initial_capital]
        self.open_positions: Dict[str, Any] = {}
    
    async def run_backtest(
        self,
        symbol: str,
        interval: str = "5m",
        strategy_func: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            symbol: Trading pair
            interval: Timeframe
            strategy_func: Custom strategy function (optional)
        
        Returns:
            Backtest results
        """
        try:
            logger.info(f"Starting backtest for {symbol}...")
            
            # Fetch historical data
            df = await get_market_dataframe(symbol, interval, 500)
            
            # Add indicators
            df = add_indicators(df)
            
            # Iterate through each candle
            for idx in range(50, len(df)):  # Skip first 50 for indicators warmup
                current_row = df.iloc[idx]
                
                # Use custom strategy or default
                if strategy_func:
                    signal = strategy_func(df.iloc[:idx+1])
                else:
                    signal = generate_signal(df.iloc[:idx+1])
                
                # Process signal
                self._process_signal(
                    symbol=symbol,
                    signal=signal,
                    current_price=current_row["close"],
                    current_time=current_row["time"],
                    atr=current_row["atr"]
                )
            
            # Close all remaining positions
            for position in list(self.open_positions.values()):
                self._close_position(position, df.iloc[-1]["close"])
            
            # Calculate results
            results = self._calculate_results()
            logger.info(f"Backtest completed. Total Return: {results['total_return_percent']:.2f}%")
            
            return results
        
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise
    
    def _process_signal(
        self,
        symbol: str,
        signal: Dict[str, Any],
        current_price: float,
        current_time: datetime,
        atr: float
    ):
        """Process trading signal"""
        
        # Check stop loss and take profit
        self._check_exits(current_price)
        
        # Generate new signals
        if signal["signal"] == "BUY" and signal["confidence"] > 0.6:
            if len(self.open_positions) < self.max_open_positions:
                self._open_position(
                    symbol=symbol,
                    side="BUY",
                    entry_price=current_price,
                    atr=atr,
                    signal_score=signal["score"],
                    entry_time=current_time
                )
        
        elif signal["signal"] == "SELL" and signal["confidence"] > 0.6:
            # Close BUY positions
            for pos_key in list(self.open_positions.keys()):
                if self.open_positions[pos_key]["side"] == "BUY":
                    self._close_position(self.open_positions[pos_key], current_price)
    
    def _open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        atr: float,
        signal_score: float,
        entry_time: datetime
    ):
        """Open a new position"""
        try:
            from app.services.risk import (
                calculate_position_size,
                calculate_stop_loss,
                calculate_take_profit
            )
            
            # Calculate levels
            stop_loss = calculate_stop_loss(entry_price, atr)
            take_profit = calculate_take_profit(entry_price, stop_loss)
            quantity = calculate_position_size(self.capital, entry_price, stop_loss)
            
            if quantity <= 0:
                return
            
            position = {
                "symbol": symbol,
                "side": side,
                "entry_price": entry_price,
                "quantity": quantity,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "entry_time": entry_time,
                "signal_score": signal_score
            }
            
            pos_key = f"{symbol}_{len(self.open_positions)}"
            self.open_positions[pos_key] = position
            
            logger.debug(f"Position opened: {symbol} @ {entry_price}")
        
        except Exception as e:
            logger.error(f"Error opening position: {e}")
    
    def _close_position(self, position: Dict[str, Any], exit_price: float):
        """Close a position and calculate PnL"""
        try:
            # Calculate PnL
            if position["side"] == "BUY":
                pnl = (exit_price - position["entry_price"]) * position["quantity"]
            else:
                pnl = (position["entry_price"] - exit_price) * position["quantity"]
            
            pnl_percent = (pnl / (position["entry_price"] * position["quantity"])) * 100
            
            # Store trade
            trade = {
                **position,
                "exit_price": exit_price,
                "pnl": pnl,
                "pnl_percent": pnl_percent
            }
            
            self.trades.append(trade)
            
            # Update capital
            self.capital += pnl
            self.equity_curve.append(self.capital)
            
            # Remove from open positions
            pos_key = [k for k, v in self.open_positions.items() if v == position]
            if pos_key:
                del self.open_positions[pos_key[0]]
            
            logger.debug(f"Position closed: PnL={pnl:.2f}")
        
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def _check_exits(self, current_price: float):
        """Check for stop loss and take profit triggers"""
        for pos_key in list(self.open_positions.keys()):
            position = self.open_positions[pos_key]
            
            # Check stop loss
            if position["side"] == "BUY":
                if current_price <= position["stop_loss"]:
                    self._close_position(position, position["stop_loss"])
                    logger.debug(f"Stop loss hit: {position['symbol']}")
                
                elif current_price >= position["take_profit"]:
                    self._close_position(position, position["take_profit"])
                    logger.debug(f"Take profit hit: {position['symbol']}")
    
    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate backtest statistics"""
        
        total_trades = len(self.trades)
        
        if total_trades == 0:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "total_return_percent": 0
            }
        
        winning_trades = [t for t in self.trades if t["pnl"] > 0]
        losing_trades = [t for t in self.trades if t["pnl"] < 0]
        
        total_pnl = sum(t["pnl"] for t in self.trades)
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = sum(t["pnl"] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t["pnl"] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = abs(sum(t["pnl"] for t in winning_trades) / sum(t["pnl"] for t in losing_trades)) if losing_trades and sum(t["pnl"] for t in losing_trades) != 0 else 0
        
        # Calculate max drawdown
        max_drawdown = self._calculate_max_drawdown()
        
        return {
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_percent": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "initial_capital": self.initial_capital,
            "final_capital": round(self.capital, 2),
            "total_return_percent": round(total_return, 2),
            "max_drawdown_percent": round(max_drawdown, 2),
            "trades": self.trades
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return 0.0
        
        equity_array = pd.Series(self.equity_curve)
        running_max = equity_array.expanding().max()
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        return max_drawdown

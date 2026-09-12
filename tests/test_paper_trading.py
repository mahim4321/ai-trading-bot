"""Test suite for paper trading"""

import pytest
from app.executors.paper_executor import PaperTradingExecutor
from datetime import datetime


def test_paper_trading_initialization():
    """Test PaperTradingExecutor initialization"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    assert executor.capital == 1000.0
    assert executor.available_capital == 1000.0
    assert len(executor.open_positions) == 0
    assert len(executor.closed_trades) == 0


def test_open_buy_trade():
    """Test opening a buy trade"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    trade = executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=0.01,
        stop_loss=49000.0,
        take_profit=51000.0,
        signal_score=4.0
    )
    
    assert trade is not None
    assert trade["symbol"] == "BTCUSDT"
    assert trade["side"] == "BUY"
    assert trade["quantity"] == 0.01
    assert trade["entry_price"] == 50000.0
    assert len(executor.open_positions) == 1


def test_close_trade():
    """Test closing a trade"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    # Open trade
    executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=0.01,
        stop_loss=49000.0,
        take_profit=51000.0
    )
    
    initial_capital = executor.available_capital
    
    # Close trade with profit
    closed_trade = executor.close_trade(0, exit_price=51000.0)
    
    assert closed_trade is not None
    assert closed_trade["exit_price"] == 51000.0
    assert closed_trade["pnl"] == 100.0  # (51000 - 50000) * 0.01
    assert closed_trade["status"] == "CLOSED"
    assert len(executor.open_positions) == 0
    assert len(executor.closed_trades) == 1


def test_insufficient_capital():
    """Test opening trade with insufficient capital"""
    executor = PaperTradingExecutor(capital=100.0)
    
    trade = executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=1.0,  # Too large
        stop_loss=49000.0,
        take_profit=51000.0
    )
    
    assert trade is None


def test_statistics():
    """Test statistics calculation"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    # Open and close profitable trade
    executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=0.01,
        stop_loss=49000.0,
        take_profit=51000.0
    )
    executor.close_trade(0, exit_price=51000.0)
    
    # Open and close losing trade
    executor.open_buy_trade(
        symbol="ETHUSDT",
        entry_price=3000.0,
        quantity=0.1,
        stop_loss=2900.0,
        take_profit=3100.0
    )
    executor.close_trade(0, exit_price=2900.0)
    
    stats = executor.get_statistics()
    
    assert stats["total_trades"] == 2
    assert stats["winning_trades"] == 1
    assert stats["losing_trades"] == 1
    assert stats["win_rate_percent"] == 50.0


def test_check_stop_loss():
    """Test stop loss detection"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=0.01,
        stop_loss=49000.0,
        take_profit=51000.0
    )
    
    # Check if stop loss is triggered
    stopped_out = executor.check_stop_loss(48000.0)
    
    assert len(stopped_out) == 1


def test_check_take_profit():
    """Test take profit detection"""
    executor = PaperTradingExecutor(capital=1000.0)
    
    executor.open_buy_trade(
        symbol="BTCUSDT",
        entry_price=50000.0,
        quantity=0.01,
        stop_loss=49000.0,
        take_profit=51000.0
    )
    
    # Check if take profit is triggered
    profit_targets = executor.check_take_profit(52000.0)
    
    assert len(profit_targets) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""API endpoints for paper trading"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.executors.paper_executor import PaperTradingExecutor
from app.services.market import get_market_dataframe
from app.services.indicators import add_indicators
from app.services.strategy import generate_signal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/paper-trading", tags=["paper-trading"])

# Global paper trading instance
paper_trader = PaperTradingExecutor(capital=1000.0)


@router.post("/open-position")
async def open_position(
    symbol: str,
    entry_price: float,
    quantity: float,
    stop_loss: float,
    take_profit: float,
    signal_score: float = 0.0
):
    """Open a paper trading position"""
    try:
        trade = paper_trader.open_buy_trade(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            signal_score=signal_score
        )
        
        if not trade:
            raise HTTPException(status_code=400, detail="Failed to open position")
        
        return {
            "status": "success",
            "trade": trade,
            "available_capital": paper_trader.available_capital
        }
    
    except Exception as e:
        logger.error(f"Error opening position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/close-position/{trade_index}")
async def close_position(
    trade_index: int,
    exit_price: float,
    db: Session = Depends(get_db)
):
    """Close a paper trading position"""
    try:
        closed_trade = paper_trader.close_trade(trade_index, exit_price)
        
        if not closed_trade:
            raise HTTPException(status_code=400, detail="Failed to close position")
        
        # Save to database
        paper_trader.save_to_database(db, closed_trade)
        
        return {
            "status": "success",
            "trade": closed_trade,
            "available_capital": paper_trader.available_capital
        }
    
    except Exception as e:
        logger.error(f"Error closing position: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_open_positions():
    """Get all open paper trading positions"""
    return {
        "open_positions": paper_trader.open_positions,
        "count": len(paper_trader.open_positions),
        "available_capital": paper_trader.available_capital
    }


@router.get("/statistics")
async def get_paper_trading_stats():
    """Get paper trading statistics"""
    stats = paper_trader.get_statistics()
    return stats


@router.get("/history")
async def get_trade_history(limit: int = 100):
    """Get trade history"""
    return {
        "total_closed_trades": len(paper_trader.closed_trades),
        "trades": paper_trader.closed_trades[-limit:]
    }


@router.post("/auto-trade/{symbol}")
async def auto_trade(symbol: str, interval: str = "5m"):
    """Automatically execute paper trade based on signal"""
    try:
        # Get market data
        df = await get_market_dataframe(symbol, interval)
        
        # Add indicators
        df = add_indicators(df)
        
        # Generate signal
        signal = generate_signal(df)
        
        latest = df.iloc[-1]
        current_price = latest["close"]
        atr = latest["atr"]
        
        # Calculate levels
        levels = paper_trader.calculate_entry_levels(current_price, atr)
        
        # Open position if BUY signal
        if signal["signal"] == "BUY" and signal["confidence"] > 0.6:
            trade = paper_trader.open_buy_trade(
                symbol=symbol,
                entry_price=current_price,
                quantity=levels["position_size"],
                stop_loss=levels["stop_loss"],
                take_profit=levels["take_profit"],
                signal_score=signal["score"],
                strategy_name="Auto-Trade"
            )
            
            return {
                "status": "position_opened",
                "signal": signal["signal"],
                "confidence": signal["confidence"],
                "trade": trade,
                "entry_levels": levels
            }
        
        else:
            return {
                "status": "no_action",
                "signal": signal["signal"],
                "confidence": signal["confidence"],
                "reasons": signal["reasons"]
            }
    
    except Exception as e:
        logger.error(f"Error in auto-trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_paper_trading():
    """Reset paper trading account"""
    try:
        global paper_trader
        paper_trader = PaperTradingExecutor(capital=1000.0)
        
        return {
            "status": "reset_successful",
            "capital": 1000.0,
            "available_capital": 1000.0
        }
    
    except Exception as e:
        logger.error(f"Error resetting paper trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

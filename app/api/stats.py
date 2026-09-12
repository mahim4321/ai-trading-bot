"""API routes for statistics"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Trade
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
async def get_summary_stats(db: Session = Depends(get_db)):
    """Get overall trading statistics"""
    try:
        # Total trades
        total_trades = db.query(func.count(Trade.id)).scalar()
        
        # Closed trades
        closed_trades = db.query(Trade).filter(Trade.status == "CLOSED").all()
        
        if not closed_trades:
            return {
                "total_trades": total_trades,
                "closed_trades": 0,
                "open_trades": total_trades,
                "message": "No closed trades yet"
            }
        
        # Win/Loss counts
        winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl and t.pnl < 0]
        
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / len(closed_trades) * 100) if closed_trades else 0
        
        # PnL calculations
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl) if closed_trades else 0
        avg_pnl = total_pnl / len(closed_trades) if closed_trades else 0
        
        # Win/Loss averages
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades) if winning_trades else 0
        total_losses = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            "total_trades": total_trades,
            "closed_trades": len(closed_trades),
            "open_trades": total_trades - len(closed_trades),
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate_percent": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "average_pnl": round(avg_pnl, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2)
        }
    
    except Exception as e:
        logger.error(f"Error getting summary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/symbol/{symbol}")
async def get_symbol_stats(symbol: str, db: Session = Depends(get_db)):
    """Get statistics for a specific symbol"""
    try:
        symbol = symbol.upper()
        
        # Get all trades for symbol
        trades = db.query(Trade).filter(Trade.symbol == symbol).all()
        closed_trades = [t for t in trades if t.status == "CLOSED"]
        
        if not closed_trades:
            return {
                "symbol": symbol,
                "trades": 0,
                "message": "No closed trades for this symbol"
            }
        
        # Calculate stats
        winning = [t for t in closed_trades if t.pnl and t.pnl > 0]
        losing = [t for t in closed_trades if t.pnl and t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
        win_rate = len(winning) / len(closed_trades) * 100
        
        return {
            "symbol": symbol,
            "total_trades": len(closed_trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate_percent": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "average_pnl": round(total_pnl / len(closed_trades), 2),
            "avg_win": round(sum(t.pnl for t in winning) / len(winning) if winning else 0, 2),
            "avg_loss": round(sum(t.pnl for t in losing) / len(losing) if losing else 0, 2),
        }
    
    except Exception as e:
        logger.error(f"Error getting symbol stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily")
async def get_daily_stats(days: int = 7, db: Session = Depends(get_db)):
    """Get daily PnL statistics"""
    try:
        since = datetime.utcnow() - timedelta(days=days)
        trades = db.query(Trade).filter(
            Trade.created_at >= since,
            Trade.status == "CLOSED"
        ).all()
        
        # Group by day
        daily_pnl = {}
        for trade in trades:
            day = trade.created_at.date()
            if day not in daily_pnl:
                daily_pnl[day] = {"pnl": 0, "trades": 0}
            
            daily_pnl[day]["pnl"] += trade.pnl or 0
            daily_pnl[day]["trades"] += 1
        
        # Format response
        result = [
            {
                "date": day.isoformat(),
                "pnl": round(data["pnl"], 2),
                "trades": data["trades"]
            }
            for day, data in sorted(daily_pnl.items())
        ]
        
        return {
            "period_days": days,
            "daily_pnl": result,
            "total_pnl": round(sum(d["pnl"] for d in result), 2)
        }
    
    except Exception as e:
        logger.error(f"Error getting daily stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

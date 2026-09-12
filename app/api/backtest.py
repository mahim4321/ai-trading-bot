"""API endpoints for backtesting"""

from fastapi import APIRouter, HTTPException
from app.executors.backtest_engine import BacktestEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
async def run_backtest(
    symbol: str,
    interval: str = "5m",
    initial_capital: float = 1000.0,
    risk_per_trade: float = 0.01
):
    """Run backtest on historical data"""
    try:
        logger.info(f"Running backtest for {symbol}...")
        
        # Create backtest engine
        backtest = BacktestEngine(
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade
        )
        
        # Run backtest
        results = await backtest.run_backtest(symbol, interval)
        
        return {
            "status": "success",
            "symbol": symbol,
            "interval": interval,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_strategy(
    symbol: str,
    interval: str = "5m",
    initial_capital: float = 1000.0
):
    """Optimize strategy parameters"""
    try:
        logger.info(f"Optimizing strategy for {symbol}...")
        
        results = []
        
        # Test different risk levels
        for risk in [0.005, 0.01, 0.02, 0.03]:
            backtest = BacktestEngine(
                initial_capital=initial_capital,
                risk_per_trade=risk
            )
            
            result = await backtest.run_backtest(symbol, interval)
            result["risk_per_trade"] = risk
            results.append(result)
        
        # Sort by return
        results.sort(key=lambda x: x["total_return_percent"], reverse=True)
        
        return {
            "status": "success",
            "symbol": symbol,
            "results": results,
            "best_strategy": results[0] if results else None
        }
    
    except Exception as e:
        logger.error(f"Error optimizing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

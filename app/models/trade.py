"""Trade model for storing trade records"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from datetime import datetime
from app.database import Base


class Trade(Base):
    """Trade execution record"""
    
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Trade Info
    symbol = Column(String(20), index=True, nullable=False)
    side = Column(String(4), nullable=False)  # BUY or SELL
    
    # Price and Quantity
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    
    # Risk Management
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    
    # Performance
    pnl = Column(Float, nullable=True, default=0)
    pnl_percent = Column(Float, nullable=True, default=0)
    
    # Status
    status = Column(String(20), nullable=False)  # OPEN, CLOSED, CANCELLED
    
    # Strategy Info
    signal_score = Column(Float, nullable=True)
    strategy_name = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_trade_symbol_status', 'symbol', 'status'),
        Index('idx_trade_created_at', 'created_at'),
        Index('idx_trade_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Trade {self.symbol} {self.side} {self.status} PnL={self.pnl}>"

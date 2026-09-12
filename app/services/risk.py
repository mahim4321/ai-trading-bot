"""Risk management service"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_position_size(
    capital: float,
    entry_price: float,
    stop_loss: float,
    risk_percent: float = 0.01
) -> float:
    """
    Calculate optimal position size based on risk management
    
    Formula: Position Size = (Capital × Risk%) / (Entry Price - Stop Loss)
    
    Args:
        capital: Total trading capital
        entry_price: Price at which we enter
        stop_loss: Stop loss price
        risk_percent: Risk percentage per trade
    
    Returns:
        Position size (quantity)
    """
    risk_amount = capital * risk_percent
    price_risk = abs(entry_price - stop_loss)
    
    if price_risk <= 0:
        logger.warning("Invalid price risk calculated")
        return 0
    
    position_size = risk_amount / price_risk
    return round(position_size, 8)


def calculate_stop_loss(
    entry_price: float,
    atr: float,
    multiplier: float = 1.5
) -> float:
    """
    Calculate stop loss based on ATR
    
    Formula: Stop Loss = Entry Price - (ATR × Multiplier)
    
    Args:
        entry_price: Entry price
        atr: Average True Range
        multiplier: ATR multiplier
    
    Returns:
        Stop loss price
    """
    stop_loss = entry_price - (atr * multiplier)
    return round(stop_loss, 8)


def calculate_take_profit(
    entry_price: float,
    stop_loss: float,
    risk_reward_ratio: float = 2.0
) -> float:
    """
    Calculate take profit based on risk/reward ratio
    
    Formula: Take Profit = Entry Price + (Risk × Risk/Reward Ratio)
    
    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        risk_reward_ratio: Risk to reward ratio
    
    Returns:
        Take profit price
    """
    risk = abs(entry_price - stop_loss)
    take_profit = entry_price + (risk * risk_reward_ratio)
    return round(take_profit, 8)


def validate_trade_setup(
    capital: float,
    entry_price: float,
    stop_loss: float,
    take_profit: float
) -> Dict[str, Any]:
    """
    Validate trade setup for validity
    
    Args:
        capital: Available capital
        entry_price: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price
    
    Returns:
        Validation result
    """
    validation = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "metrics": {}
    }
    
    # Check stop loss is below entry for BUY
    if entry_price <= stop_loss:
        validation["is_valid"] = False
        validation["errors"].append("Stop loss must be below entry price for BUY")
    
    # Check take profit is above entry
    if entry_price >= take_profit:
        validation["is_valid"] = False
        validation["errors"].append("Take profit must be above entry price for BUY")
    
    # Calculate risk/reward
    if entry_price > stop_loss:
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        rr_ratio = reward / risk if risk > 0 else 0
        
        validation["metrics"]["risk"] = float(risk)
        validation["metrics"]["reward"] = float(reward)
        validation["metrics"]["risk_reward_ratio"] = float(rr_ratio)
        
        if rr_ratio < 1:
            validation["warnings"].append(
                f"Risk/Reward ratio is {rr_ratio:.2f}:1 (unfavorable)"
            )
    
    # Calculate position size
    position_size = calculate_position_size(capital, entry_price, stop_loss)
    potential_loss = position_size * (entry_price - stop_loss)
    
    validation["metrics"]["position_size"] = float(position_size)
    validation["metrics"]["potential_loss"] = float(potential_loss)
    validation["metrics"]["potential_loss_percent"] = float(
        (potential_loss / capital) * 100 if capital > 0 else 0
    )
    
    return validation


def check_daily_loss_limit(
    current_daily_loss: float,
    capital: float,
    max_loss_percent: float = 0.03
) -> bool:
    """
    Check if we've exceeded daily loss limit
    
    Args:
        current_daily_loss: Current day's PnL (negative for loss)
        capital: Total capital
        max_loss_percent: Max loss percentage
    
    Returns:
        True if within limit, False if exceeded
    """
    max_loss_amount = capital * max_loss_percent
    within_limit = abs(current_daily_loss) <= max_loss_amount
    
    if not within_limit:
        logger.warning(
            f"Daily loss limit exceeded: {abs(current_daily_loss):.2f} > {max_loss_amount:.2f}"
        )
    
    return within_limit

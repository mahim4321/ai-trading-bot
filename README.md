# AI Trading Bot - Complete Setup Guide

An intelligent cryptocurrency and stock trading bot with technical indicators, automated signals, risk management, paper trading, and backtesting.

## 🎯 Features

✅ **Technical Indicators**
- EMA (20, 50) - Trend analysis
- RSI (14) - Momentum
- MACD - Trend momentum
- ATR (14) - Volatility
- Bollinger Bands - Price levels
- OBV - Volume analysis

✅ **Trading Capabilities**
- Automated signal generation (BUY/SELL/HOLD)
- Paper trading (simulated, no real money)
- Live trading (Binance integration)
- Backtesting framework
- Strategy optimization

✅ **Risk Management**
- Dynamic position sizing
- Stop loss calculation (ATR-based)
- Take profit levels (risk/reward ratio)
- Daily loss limits
- Maximum open positions control

✅ **Analytics & Reporting**
- Win rate tracking
- Profit factor calculation
- Drawdown analysis
- Daily/symbol-based statistics
- Performance metrics

✅ **API & Integration**
- REST API with FastAPI
- Swagger documentation
- PostgreSQL database
- Real-time market data
- WebSocket support (optional)

---

## 📦 Project Structure

```
ai-trading-bot/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Settings management
│   ├── database.py            # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── candle.py          # OHLCV data
│   │   └── trade.py           # Trade records
│   ├── services/              # Business logic
│   │   ├── binance.py         # Market data
│   │   ├── market.py          # Data processing
│   │   ├── indicators.py      # Technical analysis
│   │   ├── strategy.py        # Signal generation
│   │   └── risk.py            # Risk management
│   ├── api/                   # API endpoints
│   │   ├── signals.py         # Trading signals
│   │   ├── trades.py          # Trade management
│   │   ├── stats.py           # Statistics
│   │   ├── paper_trading.py   # Paper trading
│   │   └── backtest.py        # Backtesting
│   ├── executors/             # Trade execution
│   │   ├── paper_executor.py  # Paper trading
│   │   └── backtest_engine.py # Backtest engine
│   └── workers/               # Background tasks
│       └── market_collector.py# Data collection
├── tests/                     # Test suite
│   ├── test_paper_trading.py
│   ├── test_strategy.py
│   ├── test_risk.py
│   └── conftest.py
├── requirements.txt           # Dependencies
├── docker-compose.yml         # Docker setup
├── Dockerfile                 # Container image
├── .env.example              # Config template
├── README.md                 # This file
├── INSTALL.md                # Installation guide
└── QUICKSTART.md             # Quick reference
```

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/mahim4321/ai-trading-bot.git
cd ai-trading-bot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Database
```bash
# Using Docker (recommended)
docker-compose up -d

# Or manually setup PostgreSQL
```

### 3. Configuration
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Application
```bash
uvicorn app.main:app --reload
```

### 5. Access API
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## 📊 API Endpoints

### Signals
```
GET /api/signal/{symbol}?interval=5m
→ Get trading signal with confidence and indicators

GET /api/indicators/{symbol}?interval=5m
→ Get all technical indicators for a symbol
```

**Example Response:**
```json
{
  "symbol": "BTCUSDT",
  "signal": "BUY",
  "confidence": 0.85,
  "score": 4,
  "price": 43250.50,
  "indicators": {
    "rsi": 65.5,
    "ema_fast": 43200,
    "ema_slow": 42800,
    "macd": 450.5
  }
}
```

### Trades
```
GET /api/trades/
→ List all trades with filtering

GET /api/trades/{trade_id}
→ Get specific trade details

GET /api/trades/symbol/{symbol}
→ Get all trades for a symbol
```

### Statistics
```
GET /api/stats/summary
→ Overall trading statistics

GET /api/stats/symbol/{symbol}
→ Symbol-specific statistics

GET /api/stats/daily?days=7
→ Daily PnL statistics
```

### Paper Trading
```
POST /api/paper-trading/open-position
→ Open a simulated trade

POST /api/paper-trading/close-position/{index}
→ Close a simulated trade

GET /api/paper-trading/statistics
→ Paper trading performance

POST /api/paper-trading/auto-trade/{symbol}
→ Automatically trade based on signals
```

### Backtesting
```
POST /api/backtest/run?symbol=BTCUSDT
→ Run backtest on historical data

POST /api/backtest/optimize?symbol=BTCUSDT
→ Optimize strategy parameters
```

---

## ⚙️ Configuration

### Environment Variables (.env)

**Database:**
```env
DATABASE_URL=postgresql+psycopg2://trader:trader@localhost:5432/trading
```

**API Keys:**
```env
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
ALPHA_VANTAGE_API_KEY=your_key
```

**Trading:**
```env
TRADING_MODE=paper        # paper or live
DEFAULT_SYMBOL=BTCUSDT
RISK_PER_TRADE=0.01       # 1% per trade
MAX_DAILY_LOSS=0.03       # 3% daily max
MAX_OPEN_POSITIONS=5
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Tests
```bash
pytest tests/test_paper_trading.py -v
pytest tests/test_strategy.py::test_generate_signal
```

### Coverage Report
```bash
pytest --cov=app tests/
```

---

## 📈 Strategy Guide

### Signal Generation
The bot uses a scoring system:
- **BUY**: Score ≥ 3 (strong bullish signals)
- **SELL**: Score ≤ -3 (strong bearish signals)
- **HOLD**: Score between -2 and 2

### Risk Management Formula

**Position Size:**
```
Position = (Capital × Risk%) / (Entry - Stop Loss)
```

**Stop Loss (ATR-based):**
```
Stop Loss = Entry Price - (ATR × 1.5)
```

**Take Profit (Risk/Reward):**
```
Take Profit = Entry + (Risk × Ratio)
```

### Example Trade
```
Capital:        $1,000
Entry Price:    $50,000
Stop Loss:      $49,000 (1% risk)
Take Profit:    $52,000 (2:1 RR)
Position Size:  0.01 BTC
Risk Amount:    $10
```

---

## 📊 Performance Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Win Rate | Wins / Total | > 50% |
| Profit Factor | Total Wins / Total Losses | > 1.5 |
| Sharpe Ratio | Return / Volatility | > 1.0 |
| Max Drawdown | Peak to Trough % | < 20% |
| Return | (Final - Initial) / Initial | > 0% |

---

## 🔄 Paper Trading Workflow

1. **Get Signal**
   ```bash
   curl http://localhost:8000/api/signal/BTCUSDT
   ```

2. **Open Position** (if BUY signal)
   ```bash
   curl -X POST http://localhost:8000/api/paper-trading/open-position \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "BTCUSDT",
       "entry_price": 50000,
       "quantity": 0.01,
       "stop_loss": 49000,
       "take_profit": 51000
     }'
   ```

3. **Monitor Position**
   ```bash
   curl http://localhost:8000/api/paper-trading/positions
   ```

4. **Close Position** (on exit signal)
   ```bash
   curl -X POST http://localhost:8000/api/paper-trading/close-position/0 \
     -H "Content-Type: application/json" \
     -d '{"exit_price": 51000}'
   ```

5. **Review Statistics**
   ```bash
   curl http://localhost:8000/api/paper-trading/statistics
   ```

---

## 🧬 Backtesting

### Run Backtest
```bash
curl -X POST http://localhost:8000/api/backtest/run?symbol=BTCUSDT
```

### Optimize Strategy
```bash
curl -X POST http://localhost:8000/api/backtest/optimize?symbol=BTCUSDT
```

**Response includes:**
- Total trades
- Win rate
- Profit factor
- Max drawdown
- Return percentage

---

## 🔐 Security Best Practices

1. **Never commit .env** - Use .env.example template
2. **Rotate API Keys** - Change regularly
3. **Use IP Whitelisting** - On Binance API
4. **Test First** - Always use paper trading
5. **Monitor Closely** - Watch bot performance
6. **Start Small** - Begin with small capital
7. **Keep Updated** - Regular security patches

---

## ⚠️ Disclaimer

**Trading involves substantial risk of loss.**

- This bot is provided AS-IS without warranty
- Past performance ≠ future results
- Start with paper trading
- Never risk more than you can afford to lose
- Test strategies thoroughly before live trading
- Monitor the bot regularly
- Understand the strategy before deploying

---

## 🆘 Troubleshooting

### Port 8000 Already in Use
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose up -d
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### API Key Invalid
- Verify credentials in .env
- Check API key permissions on exchange
- Ensure IP whitelisting is correct

---

## 📚 Additional Resources

- **Installation Guide**: See [INSTALL.md](INSTALL.md)
- **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)
- **API Docs**: http://localhost:8000/docs (when running)
- **FastAPI**: https://fastapi.tiangolo.com/
- **Technical Analysis**: https://github.com/bukosabino/ta
- **Binance API**: https://binance-docs.github.io/

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check README.md and INSTALL.md
- **API Help**: Visit /docs endpoint when running

---

**Created with ❤️ for traders**

**Status**: ✅ Production Ready | **Version**: 1.0.0

# Installation and Setup Guide

## System Requirements

- Python 3.9 or higher
- PostgreSQL 14 or higher (or Docker)
- 2GB RAM minimum
- Internet connection for API calls

---

## Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/mahim4321/ai-trading-bot.git
cd ai-trading-bot
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
```bash
# Option A: Using Docker (Recommended)
docker-compose up -d

# Option B: Manual PostgreSQL
# Create database and user in PostgreSQL
```

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env file with your settings
```

### 6. Run Application
```bash
uvicorn app.main:app --reload
```

### 7. Access API
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Detailed Setup Instructions

### Windows

#### Install Python
1. Download from python.org
2. Check "Add Python to PATH"
3. Install

#### Install PostgreSQL
1. Download from postgresql.org
2. Remember password for 'postgres' user
3. Install

#### Setup Trading Bot
```bash
# Clone repo
git clone https://github.com/mahim4321/ai-trading-bot.git
cd ai-trading-bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database
# Open pgAdmin or psql and run:
# CREATE DATABASE trading;
# CREATE USER trader WITH PASSWORD 'trader';
# GRANT ALL PRIVILEGES ON DATABASE trading TO trader;

# Configure
copy .env.example .env
# Edit .env with notepad

# Run
uvicorn app.main:app --reload
```

---

### Mac/Linux

#### Install Python
```bash
# Mac (using Homebrew)
brew install python3

# Ubuntu/Debian
sudo apt-get install python3 python3-venv
```

#### Install PostgreSQL
```bash
# Mac
brew install postgresql@14

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

#### Setup Trading Bot
```bash
# Clone repo
git clone https://github.com/mahim4321/ai-trading-bot.git
cd ai-trading-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
sudo -u postgres psql
CREATE DATABASE trading;
CREATE USER trader WITH PASSWORD 'trader';
GRANT ALL PRIVILEGES ON DATABASE trading TO trader;
\q

# Configure
cp .env.example .env
nano .env  # or use your preferred editor

# Run
uvicorn app.main:app --reload
```

---

## Configuration (.env)

### Required Settings
```env
# Database Connection
DATABASE_URL=postgresql+psycopg2://trader:trader@localhost:5432/trading

# API Keys (get from Binance/AlphaVantage)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
ALPHA_VANTAGE_API_KEY=your_api_key
```

### Trading Settings
```env
# Mode: paper (simulated) or live (real)
TRADING_MODE=paper

# Default trading pair
DEFAULT_SYMBOL=BTCUSDT

# Risk management
RISK_PER_TRADE=0.01      # 1% per trade
MAX_DAILY_LOSS=0.03      # 3% max daily loss
MAX_OPEN_POSITIONS=5     # Max concurrent trades
```

### API Settings
```env
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False
```

---

## Getting API Keys

### Binance
1. Go to https://www.binance.com
2. Create account
3. Enable 2FA
4. API Management → Create API Key
5. Generate API Key and Secret
6. Copy to .env file

### AlphaVantage
1. Go to https://www.alphavantage.co
2. Sign up for free account
3. Get API Key from dashboard
4. Copy to .env file

---

## Verify Installation

```bash
# Check if application starts
uvicorn app.main:app --reload

# In another terminal, test API
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"..."}
```

---

## Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### "Connection refused" (Database)
```bash
# Check if PostgreSQL is running
# Windows: Services → PostgreSQL
# Mac: brew services list
# Linux: sudo service postgresql status

# Or use Docker
docker-compose up -d
```

### Port 8000 Already in Use
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Verify credentials are correct

---

## Next Steps

1. ✅ Get API Keys (Binance/AlphaVantage)
2. ✅ Complete .env configuration
3. ✅ Start application
4. ✅ Access API documentation
5. ✅ Test endpoints
6. ✅ Try paper trading
7. ✅ Run backtest
8. ✅ Deploy to production

---

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Check README.md for detailed info
- API Docs: http://localhost:8000/docs (when running)

---

**Happy Trading! 🚀**

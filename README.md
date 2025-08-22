
# NIFTY 100 Trading Dashboard

A production-ready Streamlit dashboard that scans all NIFTY 100 constituents daily and outputs buy signals from eight trading strategies, then recommends the strongest strategy per stock based on historical performance.

## Features

- **Real-time Data**: Fetches daily OHLCV data for all NIFTY 100 stocks using yfinance
- **8 Trading Strategies**: Implements sophisticated trading strategies combining technical indicators
- **Performance Analytics**: Comprehensive backtesting with win ratio, profit factor, and risk metrics
- **Interactive Dashboard**: Modern Streamlit interface with filtering, sorting, and detailed analysis
- **Caching & Performance**: SQLite-based caching with incremental updates for production use
- **Export Functionality**: CSV export of daily signals and performance metrics

## Trading Strategies

1. **BB Signal + 513**: Bollinger Bands breakout combined with SMA5/13 crossover
2. **SMA 513 Crossover**: Simple momentum strategy using SMA5 crossing above SMA13
3. **MACD Cross**: MACD line crossing above signal line with negative MACD filter
4. **Dip Buy + 513**: -4% daily return with SMA5 > SMA13 confirmation
5. **MACD + Volume**: MACD bullish with high volume participation
6. **RSI + ADX**: RSI recovery from oversold with trend strength confirmation
7. **BB + 513 + RSI**: Multi-indicator strategy for early upswing detection
8. **BB + 513 + ADX**: Bollinger band rebound with trend strength

## Technical Indicators

- **Moving Averages**: SMA(5, 13, 50, 200), EMA(10, 30)
- **Momentum**: RSI(14), MACD(12, 26, 9)
- **Volatility**: Bollinger Bands(20, 2σ), ATR(14)
- **Trend**: ADX(14), +DI, -DI
- **Volume**: 20-period moving average, volume ratios

## Performance Metrics

- **Win Ratio**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profits to gross losses  
- **Expectancy**: Average profit per trade
- **Sharpe Ratio**: Risk-adjusted returns (annualized)
- **Maximum Drawdown**: Largest peak-to-trough decline
- **CAGR**: Compound Annual Growth Rate
- **Trades per Year**: Trading frequency
- **Last 12 Month Return**: Recent performance

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd nifty100-trading-dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

4. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:8501`

### Data Initialization

On first run, the dashboard will:
- Download historical data for all NIFTY 100 stocks (this may take 5-10 minutes)
- Create SQLite database for caching (`market_data.db`)
- Calculate technical indicators for all stocks
- Generate backtest results

Subsequent runs will use cached data and only fetch recent updates.

## Usage Guide

### Main Dashboard

1. **Stock Overview Tab**: 
   - View all NIFTY 100 stocks with current signals
   - Filter by sector, price, or signal presence
   - Export results to CSV

2. **Detailed Analysis Tab**:
   - Select individual stocks for deep analysis
   - Interactive price charts with all indicators
   - Strategy performance comparison table
   - Signal quality assessment

3. **Global Analytics Tab**:
   - Signal distribution across strategies and sectors
   - Top performing stocks by strategy score
   - Market-wide statistics

### Filtering Options

- **Sector Filter**: Focus on specific market sectors
- **Signal Filter**: Show only stocks with active BUY signals
- **Price Filter**: Set minimum price thresholds
- **Performance Filters**: Sort by win ratio, profit factor, etc.

### Strategy Ranking

Each stock gets a **Strategy Score** based on:
- **Win Ratio (50% weight)**: Historical success rate
- **Profit Factor (30% weight)**: Risk-reward profile  
- **12-Month Return (20% weight)**: Recent performance

## Configuration

### Backtesting Parameters

Edit `app.py` to modify backtesting settings:

```python
self.backtester = Backtester(
    entry_method="next_open",     # "next_open" or "same_close"
    exit_method="time_based",     # "time_based" or "signal_based"  
    hold_days=10,                 # Default holding period
    transaction_cost=0.001,       # 0.1% per trade
    slippage=0.0005              # 0.05% slippage
)
```

### Data Update Schedule

For production deployment, set up automated data updates:

**Using cron (Linux/Mac)**:
```bash
# Update data daily at 6:30 PM IST
30 18 * * 1-5 cd /path/to/dashboard && python -c "from data_loader import DataLoader; DataLoader().refresh_all_data()"
```

**Using Windows Task Scheduler**:
Create a batch file to run the data update and schedule it daily.

## File Structure

```
├── app.py                 # Main Streamlit application
├── data_loader.py         # Data fetching and caching
├── indicators.py          # Technical indicator calculations  
├── strategies.py          # Trading strategy implementations
├── backtest.py           # Backtesting and performance metrics
├── nifty_100_stocks.csv  # NIFTY 100 constituent list
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── market_data.db        # SQLite database (created on first run)
└── data_cache/           # Directory for cached data files
```

## Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment

**Streamlit Cloud**:
1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with automatic updates

**Docker**:
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**VPS/Cloud Server**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run with production settings
streamlit run app.py --server.port 8501 --server.headless true
```

## Performance Optimization

### Caching Strategy
- SQLite database stores OHLCV data with incremental updates
- Session state caching for indicator calculations  
- Lazy loading of backtest results
- Compressed data storage using Parquet (optional)

### Scalability Features
- Parallel data fetching using ThreadPoolExecutor
- Async data updates with rate limiting
- Efficient indicator calculation using pandas-ta
- Memory-optimized data structures

## API Rate Limits

**yfinance Limitations**:
- ~2000 requests per hour per IP
- Built-in retry logic with exponential backoff
- Automatic rate limiting between requests

For higher volume requirements, consider:
- Yahoo Finance API (paid)
- Alpha Vantage API
- Quandl/NASDAQ Data Link
- NSE official data feeds

## Troubleshooting

### Common Issues

1. **Data Loading Errors**:
   ```bash
   # Clear cache and retry
   rm market_data.db
   rm -rf data_cache/
   ```

2. **Missing Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Memory Issues**:
   - Reduce number of stocks processed simultaneously
   - Clear browser cache
   - Restart Streamlit server

4. **Slow Performance**:
   - Check internet connection
   - Verify SQLite database integrity
   - Monitor system resources

### Debug Mode

Run with debug logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Disclaimer

**Important**: This dashboard is for educational and research purposes only. It is not intended as financial advice. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

Always:
- Conduct your own research
- Consult with qualified financial advisors  
- Use proper risk management
- Test strategies thoroughly before live trading
- Never risk more than you can afford to lose

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Review the troubleshooting guide
- Check existing discussions and documentation

---

**Happy Trading! 📈**

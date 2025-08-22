
"""
Simple test script to verify the dashboard components work
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_data_loader():
    """Test data loader functionality"""
    try:
        from data_loader import DataLoader
        loader = DataLoader()

        # Test symbol loading
        symbols = loader.load_nifty100_symbols()
        print(f"✅ Loaded {len(symbols)} NIFTY 100 symbols")

        # Test data fetching for one symbol
        test_symbol = "RELIANCE.NS"
        df = loader.fetch_stock_data(test_symbol, period="1y")
        if df is not None and len(df) > 100:
            print(f"✅ Successfully fetched data for {test_symbol}: {len(df)} records")
        else:
            print(f"❌ Failed to fetch data for {test_symbol}")

        return True
    except Exception as e:
        print(f"❌ Data loader test failed: {e}")
        return False

def test_indicators():
    """Test technical indicators"""
    try:
        from indicators import TechnicalIndicators

        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        np.random.seed(42)

        price = 100
        prices = []
        volumes = []

        for i in range(200):
            price += np.random.normal(0, 2)
            prices.append(max(price, 10))  # Keep price positive
            volumes.append(np.random.randint(100000, 1000000))

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
            'Close': prices,
            'Volume': volumes
        })
        df.set_index('Date', inplace=True)

        indicators = TechnicalIndicators()
        df_with_indicators = indicators.calculate_all_indicators(df)

        # Check if indicators were calculated
        required_indicators = ['SMA_5', 'SMA_13', 'RSI', 'MACD', 'BB_Upper']
        missing_indicators = [ind for ind in required_indicators if ind not in df_with_indicators.columns]

        if not missing_indicators:
            print("✅ All technical indicators calculated successfully")
            return True
        else:
            print(f"❌ Missing indicators: {missing_indicators}")
            return False

    except Exception as e:
        print(f"❌ Indicators test failed: {e}")
        return False

def test_strategies():
    """Test trading strategies"""
    try:
        from strategies import TradingStrategies
        from indicators import TechnicalIndicators

        # Use the same sample data as indicators test
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        np.random.seed(42)

        price = 100
        prices = []
        volumes = []

        for i in range(200):
            price += np.random.normal(0, 2)
            prices.append(max(price, 10))
            volumes.append(np.random.randint(100000, 1000000))

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
            'Close': prices,
            'Volume': volumes
        })
        df.set_index('Date', inplace=True)

        # Calculate indicators first
        indicators = TechnicalIndicators()
        df_with_indicators = indicators.calculate_all_indicators(df)

        # Test strategies
        strategies = TradingStrategies()
        all_signals = strategies.generate_all_signals(df_with_indicators)

        signal_counts = {strategy: signals.sum() for strategy, signals in all_signals.items()}
        print(f"✅ Generated signals for {len(all_signals)} strategies")
        print(f"   Signal counts: {signal_counts}")

        return True

    except Exception as e:
        print(f"❌ Strategies test failed: {e}")
        return False

def test_backtest():
    """Test backtesting functionality"""
    try:
        from backtest import Backtester
        from strategies import TradingStrategies
        from indicators import TechnicalIndicators

        # Create sample data with indicators
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        np.random.seed(42)

        price = 100
        prices = []
        volumes = []

        for i in range(200):
            price += np.random.normal(0, 2)
            prices.append(max(price, 10))
            volumes.append(np.random.randint(100000, 1000000))

        df = pd.DataFrame({
            'Date': dates,
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
            'Close': prices,
            'Volume': volumes
        })
        df.set_index('Date', inplace=True)

        # Calculate indicators and signals
        indicators = TechnicalIndicators()
        df_with_indicators = indicators.calculate_all_indicators(df)

        strategies = TradingStrategies()
        all_signals = strategies.generate_all_signals(df_with_indicators)

        # Run backtest
        backtester = Backtester()
        backtest_results = backtester.backtest_all_strategies(df_with_indicators, all_signals)

        print(f"✅ Backtesting completed for {len(backtest_results)} strategies")

        # Show sample results
        for strategy, results in list(backtest_results.items())[:2]:
            print(f"   {strategy}: {results['total_trades']} trades, {results['win_ratio']:.2%} win rate")

        return True

    except Exception as e:
        print(f"❌ Backtest test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running NIFTY 100 Trading Dashboard Tests\n")

    tests = [
        ("Data Loader", test_data_loader),
        ("Technical Indicators", test_indicators),  
        ("Trading Strategies", test_strategies),
        ("Backtesting", test_backtest)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Dashboard is ready to run.")
        print("\n🚀 To start the dashboard, run: streamlit run app.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

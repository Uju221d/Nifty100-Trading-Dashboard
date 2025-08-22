
"""
Data Loader Module for NIFTY 100 Trading Dashboard
Handles fetching, caching, and updating OHLCV data for all stocks
"""

import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Dict, List, Optional, Tuple
import json

class DataLoader:
    def __init__(self, cache_dir: str = "data_cache", db_path: str = "market_data.db"):
        self.cache_dir = cache_dir
        self.db_path = db_path
        self.logger = self._setup_logger()
        self._init_cache_dir()
        self._init_database()

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('DataLoader')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _init_cache_dir(self):
        """Initialize cache directory"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _init_database(self):
        """Initialize SQLite database for caching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create table for OHLCV data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adj_close REAL,
                updated_at TEXT,
                PRIMARY KEY (symbol, date)
            )
        """)

        # Create table for metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                symbol TEXT PRIMARY KEY,
                last_update TEXT,
                data_start_date TEXT,
                data_end_date TEXT
            )
        """)

        conn.commit()
        conn.close()

    def load_nifty100_symbols(self) -> List[Dict]:
        """Load NIFTY 100 symbols from CSV file"""
        try:
            df = pd.read_csv('nifty_100_stocks.csv')
            return df.to_dict('records')
        except FileNotFoundError:
            self.logger.error("NIFTY 100 stocks CSV file not found")
            return []

    def get_cached_data(self, symbol: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Retrieve cached data from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM ohlcv_data 
            WHERE symbol = ? AND date >= ? AND date <= ?
            ORDER BY date
        """
        try:
            df = pd.read_sql_query(query, conn, params=(symbol, start_date, end_date))
            if not df.empty:
                df['Date'] = pd.to_datetime(df['date'])
                df.set_index('Date', inplace=True)
                df = df[['open', 'high', 'low', 'close', 'volume', 'adj_close']]
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
                return df
        except Exception as e:
            self.logger.error(f"Error retrieving cached data for {symbol}: {e}")
        finally:
            conn.close()
        return None

    def cache_data(self, symbol: str, df: pd.DataFrame):
        """Cache data to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Prepare data for insertion
            df_reset = df.reset_index()
            df_reset['symbol'] = symbol
            df_reset['date'] = df_reset['Date'].dt.strftime('%Y-%m-%d')
            df_reset['updated_at'] = datetime.now().isoformat()

            # Insert or replace data
            for _, row in df_reset.iterrows():
                cursor.execute("""
                    INSERT OR REPLACE INTO ohlcv_data 
                    (symbol, date, open, high, low, close, volume, adj_close, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['symbol'], row['date'], row['Open'], row['High'], 
                    row['Low'], row['Close'], row['Volume'], 
                    row.get('Adj Close', row['Close']), row['updated_at']
                ))

            # Update metadata
            start_date = df_reset['date'].min()
            end_date = df_reset['date'].max()
            cursor.execute("""
                INSERT OR REPLACE INTO metadata 
                (symbol, last_update, data_start_date, data_end_date)
                VALUES (?, ?, ?, ?)
            """, (symbol, datetime.now().isoformat(), start_date, end_date))

            conn.commit()
            self.logger.info(f"Cached data for {symbol}: {len(df)} records")

        except Exception as e:
            self.logger.error(f"Error caching data for {symbol}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def fetch_stock_data(self, symbol: str, period: str = "10y", 
                        max_retries: int = 3, delay: float = 1.0) -> Optional[pd.DataFrame]:
        """Fetch stock data with retry logic and rate limiting"""
        for attempt in range(max_retries):
            try:
                # Add delay to respect rate limits
                time.sleep(delay)

                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, auto_adjust=True)

                if not df.empty:
                    # Clean data
                    df = df.dropna()
                    df = df[df['Volume'] > 0]  # Remove zero volume days
                    return df
                else:
                    self.logger.warning(f"No data returned for {symbol}")

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {symbol}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff

        return None

    def update_stock_data(self, symbol: str, incremental: bool = True) -> Optional[pd.DataFrame]:
        """Update stock data incrementally or full refresh"""
        try:
            if incremental:
                # Try to get last update date
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT data_end_date FROM metadata WHERE symbol = ?', (symbol,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    last_date = datetime.strptime(result[0], '%Y-%m-%d')
                    days_since = (datetime.now() - last_date).days

                    if days_since <= 1:
                        # Data is up to date
                        return self.get_cached_data(symbol, 
                                                  (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                                                  datetime.now().strftime('%Y-%m-%d'))

                    # Fetch only recent data
                    ticker = yf.Ticker(symbol)
                    start_date = (last_date - timedelta(days=5)).strftime('%Y-%m-%d')
                    df_new = ticker.history(start=start_date, auto_adjust=True)

                    if not df_new.empty:
                        self.cache_data(symbol, df_new)

            # Full refresh or initial load
            df = self.fetch_stock_data(symbol)
            if df is not None:
                self.cache_data(symbol, df)
                return df

        except Exception as e:
            self.logger.error(f"Error updating data for {symbol}: {e}")

        return None

    def batch_update_stocks(self, symbols: List[str], max_workers: int = 5) -> Dict[str, pd.DataFrame]:
        """Update multiple stocks in parallel"""
        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.update_stock_data, symbol): symbol 
                for symbol in symbols
            }

            # Collect results
            for future in future_to_symbol:
                symbol = future_to_symbol[future]
                try:
                    df = future.result(timeout=60)  # 60 second timeout per stock
                    if df is not None:
                        results[symbol] = df
                        self.logger.info(f"Successfully updated {symbol}")
                    else:
                        self.logger.warning(f"Failed to update {symbol}")
                except Exception as e:
                    self.logger.error(f"Error processing {symbol}: {e}")

        return results

    def get_latest_data(self, symbol: str, days: int = 252) -> Optional[pd.DataFrame]:
        """Get latest data for a symbol"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Try cache first
        cached_data = self.get_cached_data(symbol, start_date, end_date)
        if cached_data is not None and len(cached_data) > 50:  # Reasonable amount of data
            return cached_data

        # Fetch new data
        return self.update_stock_data(symbol)

    def refresh_all_data(self):
        """Refresh data for all NIFTY 100 stocks"""
        symbols_data = self.load_nifty100_symbols()
        symbols = [stock['symbol'] for stock in symbols_data]

        self.logger.info(f"Starting data refresh for {len(symbols)} symbols")
        results = self.batch_update_stocks(symbols, max_workers=3)

        success_count = len(results)
        self.logger.info(f"Successfully updated {success_count}/{len(symbols)} symbols")

        return results


"""
Technical Indicators Module for NIFTY 100 Trading Dashboard
Computes all required technical indicators using pandas_ta
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

class TechnicalIndicators:
    def __init__(self):
        self.indicators = {}

    def calculate_sma(self, df: pd.DataFrame, periods: list = [5, 13, 50, 200]) -> Dict[str, pd.Series]:
        """Calculate Simple Moving Averages"""
        sma_dict = {}
        for period in periods:
            sma_dict[f'SMA_{period}'] = ta.sma(df['Close'], length=period)
        return sma_dict

    def calculate_ema(self, df: pd.DataFrame, periods: list = [10, 30]) -> Dict[str, pd.Series]:
        """Calculate Exponential Moving Averages"""
        ema_dict = {}
        for period in periods:
            ema_dict[f'EMA_{period}'] = ta.ema(df['Close'], length=period)
        return ema_dict

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        return ta.rsi(df['Close'], length=period)

    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        macd_data = ta.macd(df['Close'], fast=fast, slow=slow, signal=signal)
        return {
            'MACD': macd_data[f'MACD_{fast}_{slow}_{signal}'],
            'MACD_Signal': macd_data[f'MACDs_{fast}_{slow}_{signal}'],
            'MACD_Histogram': macd_data[f'MACDh_{fast}_{slow}_{signal}']
        }

    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std: float = 2.0) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        bb_data = ta.bbands(df['Close'], length=period, std=std)

        # Calculate %B indicator
        bb_upper = bb_data[f'BBU_{period}_{std}']
        bb_lower = bb_data[f'BBL_{period}_{std}']
        bb_mid = bb_data[f'BBM_{period}_{std}']

        percent_b = (df['Close'] - bb_lower) / (bb_upper - bb_lower)

        return {
            'BB_Upper': bb_upper,
            'BB_Mid': bb_mid,
            'BB_Lower': bb_lower,
            'BB_Width': (bb_upper - bb_lower) / bb_mid,
            'Percent_B': percent_b
        }

    def calculate_adx(self, df: pd.DataFrame, period: int = 14) -> Dict[str, pd.Series]:
        """Calculate Average Directional Index (ADX)"""
        adx_data = ta.adx(df['High'], df['Low'], df['Close'], length=period)
        return {
            'ADX': adx_data[f'ADX_{period}'],
            'DI_Plus': adx_data[f'DMP_{period}'],
            'DI_Minus': adx_data[f'DMN_{period}']
        }

    def calculate_volume_indicators(self, df: pd.DataFrame, period: int = 20) -> Dict[str, pd.Series]:
        """Calculate Volume-based indicators"""
        vol_ma = ta.sma(df['Volume'], length=period)
        vol_ratio = df['Volume'] / vol_ma

        return {
            'Volume_MA': vol_ma,
            'Volume_Ratio': vol_ratio
        }

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all indicators and return enhanced dataframe"""
        if df is None or df.empty:
            return None

        # Make a copy to avoid modifying original
        result_df = df.copy()

        try:
            # Moving Averages
            sma_dict = self.calculate_sma(df)
            for key, value in sma_dict.items():
                result_df[key] = value

            ema_dict = self.calculate_ema(df)
            for key, value in ema_dict.items():
                result_df[key] = value

            # RSI
            result_df['RSI'] = self.calculate_rsi(df)

            # MACD
            macd_dict = self.calculate_macd(df)
            for key, value in macd_dict.items():
                result_df[key] = value

            # Bollinger Bands
            bb_dict = self.calculate_bollinger_bands(df)
            for key, value in bb_dict.items():
                result_df[key] = value

            # ADX
            adx_dict = self.calculate_adx(df)
            for key, value in adx_dict.items():
                result_df[key] = value

            # Volume Indicators
            vol_dict = self.calculate_volume_indicators(df)
            for key, value in vol_dict.items():
                result_df[key] = value

            # Additional derived indicators
            result_df['Daily_Return'] = result_df['Close'].pct_change()
            result_df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)

            return result_df

        except Exception as e:
            print(f"Error calculating indicators: {e}")
            return df

    def get_latest_indicator_values(self, df: pd.DataFrame) -> Dict:
        """Get latest values of all indicators"""
        if df is None or df.empty:
            return {}

        latest = df.iloc[-1]

        indicators = {
            'Close': latest.get('Close', 0),
            'Volume': latest.get('Volume', 0),
            'Daily_Return': latest.get('Daily_Return', 0),
            'SMA_5': latest.get('SMA_5', 0),
            'SMA_13': latest.get('SMA_13', 0),
            'SMA_50': latest.get('SMA_50', 0),
            'SMA_200': latest.get('SMA_200', 0),
            'EMA_10': latest.get('EMA_10', 0),
            'EMA_30': latest.get('EMA_30', 0),
            'RSI': latest.get('RSI', 50),
            'MACD': latest.get('MACD', 0),
            'MACD_Signal': latest.get('MACD_Signal', 0),
            'MACD_Histogram': latest.get('MACD_Histogram', 0),
            'BB_Upper': latest.get('BB_Upper', 0),
            'BB_Mid': latest.get('BB_Mid', 0),
            'BB_Lower': latest.get('BB_Lower', 0),
            'Percent_B': latest.get('Percent_B', 0.5),
            'BB_Width': latest.get('BB_Width', 0),
            'ADX': latest.get('ADX', 20),
            'DI_Plus': latest.get('DI_Plus', 20),
            'DI_Minus': latest.get('DI_Minus', 20),
            'Volume_MA': latest.get('Volume_MA', 0),
            'Volume_Ratio': latest.get('Volume_Ratio', 1),
            'ATR': latest.get('ATR', 0)
        }

        return indicators

    def check_crossover(self, series1: pd.Series, series2: pd.Series, lookback: int = 1) -> bool:
        """Check if series1 crosses above series2 in the last 'lookback' periods"""
        if len(series1) < lookback + 1 or len(series2) < lookback + 1:
            return False

        # Current: series1 > series2
        # Previous: series1 <= series2
        current_above = series1.iloc[-1] > series2.iloc[-1]

        for i in range(1, lookback + 1):
            if series1.iloc[-1-i] > series2.iloc[-1-i]:
                return False  # Was already above

        return current_above

    def check_crossunder(self, series1: pd.Series, series2: pd.Series, lookback: int = 1) -> bool:
        """Check if series1 crosses below series2 in the last 'lookback' periods"""
        if len(series1) < lookback + 1 or len(series2) < lookback + 1:
            return False

        # Current: series1 < series2
        # Previous: series1 >= series2
        current_below = series1.iloc[-1] < series2.iloc[-1]

        for i in range(1, lookback + 1):
            if series1.iloc[-1-i] < series2.iloc[-1-i]:
                return False  # Was already below

        return current_below

    def get_trend_strength(self, df: pd.DataFrame) -> str:
        """Determine overall trend strength"""
        if df is None or len(df) < 50:
            return "Unknown"

        try:
            latest = df.iloc[-1]
            close = latest['Close']
            sma_50 = latest.get('SMA_50', close)
            sma_200 = latest.get('SMA_200', close)
            adx = latest.get('ADX', 20)

            # Trend direction
            if close > sma_50 > sma_200:
                trend_dir = "Uptrend"
            elif close < sma_50 < sma_200:
                trend_dir = "Downtrend"
            else:
                trend_dir = "Sideways"

            # Trend strength based on ADX
            if adx > 40:
                strength = "Very Strong"
            elif adx > 25:
                strength = "Strong"
            elif adx > 20:
                strength = "Moderate"
            else:
                strength = "Weak"

            return f"{trend_dir} ({strength})"

        except Exception:
            return "Unknown"

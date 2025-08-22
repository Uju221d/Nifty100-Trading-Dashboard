
"""
Trading Strategies Module for NIFTY 100 Trading Dashboard
Implements 8 trading strategies for generating BUY signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class TradingStrategies:
    def __init__(self):
        self.strategy_names = [
            "BB_Signal_513",
            "SMA_513_Crossover", 
            "MACD_Cross",
            "Dip_Buy_513",
            "MACD_Volume",
            "RSI_ADX_Signal",
            "BB_513_RSI",
            "BB_513_ADX"
        ]

    def bb_signal_513(self, df: pd.DataFrame, window: int = 3) -> pd.Series:
        """
        BB Signal + 513: 
        Condition A: Close crosses up through bb_lower OR %b < 0.05
        Condition B: SMA5 crosses above SMA13
        BUY when A AND B occur within a 3-bar window
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            close = df['Close']
            bb_lower = df['BB_Lower']
            percent_b = df['Percent_B']
            sma5 = df['SMA_5']
            sma13 = df['SMA_13']

            # Condition A: Close crosses above BB lower OR %B < 0.05
            condition_a1 = (close > bb_lower) & (close.shift(1) <= bb_lower.shift(1))
            condition_a2 = percent_b < 0.05
            condition_a = condition_a1 | condition_a2

            # Condition B: SMA5 crosses above SMA13
            condition_b = (sma5 > sma13) & (sma5.shift(1) <= sma13.shift(1))

            # Check for both conditions within window
            for i in range(window, len(df)):
                if condition_a.iloc[i-window:i+1].any() and condition_b.iloc[i-window:i+1].any():
                    signals.iloc[i] = True

            return signals

        except Exception as e:
            print(f"Error in bb_signal_513: {e}")
            return signals

    def sma_513_crossover(self, df: pd.DataFrame) -> pd.Series:
        """
        513 Crossover Signal: SMA5 crosses above SMA13
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 20:
            return signals

        try:
            sma5 = df['SMA_5']
            sma13 = df['SMA_13']

            # SMA5 crosses above SMA13
            signals = (sma5 > sma13) & (sma5.shift(1) <= sma13.shift(1))

            return signals

        except Exception as e:
            print(f"Error in sma_513_crossover: {e}")
            return signals

    def macd_cross(self, df: pd.DataFrame, require_negative: bool = True) -> pd.Series:
        """
        MACD Cross: MACD line crosses above Signal line
        Optional filter: MACD < 0 prior to cross
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            macd = df['MACD']
            macd_signal = df['MACD_Signal']

            # MACD crosses above signal line
            cross_condition = (macd > macd_signal) & (macd.shift(1) <= macd_signal.shift(1))

            if require_negative:
                # Additional filter: MACD was negative before cross
                negative_condition = macd.shift(1) < 0
                signals = cross_condition & negative_condition
            else:
                signals = cross_condition

            return signals

        except Exception as e:
            print(f"Error in macd_cross: {e}")
            return signals

    def dip_buy_513(self, df: pd.DataFrame, dip_threshold: float = -0.04) -> pd.Series:
        """
        -4% Signal & 513 Crossover: Daily return <= -4% today AND SMA5 > SMA13 by close
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 20:
            return signals

        try:
            daily_return = df['Daily_Return']
            sma5 = df['SMA_5']
            sma13 = df['SMA_13']

            # Daily return <= -4% AND SMA5 > SMA13
            dip_condition = daily_return <= dip_threshold
            momentum_condition = sma5 > sma13

            signals = dip_condition & momentum_condition

            return signals

        except Exception as e:
            print(f"Error in dip_buy_513: {e}")
            return signals

    def macd_volume(self, df: pd.DataFrame, volume_multiplier: float = 1.2) -> pd.Series:
        """
        MACD+Vol Signal: MACD line > Signal AND Volume > 1.2 × vol_ma20
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            macd = df['MACD']
            macd_signal = df['MACD_Signal']
            volume_ratio = df['Volume_Ratio']

            # MACD > Signal AND Volume > threshold
            macd_condition = macd > macd_signal
            volume_condition = volume_ratio > volume_multiplier

            signals = macd_condition & volume_condition

            return signals

        except Exception as e:
            print(f"Error in macd_volume: {e}")
            return signals

    def rsi_adx_signal(self, df: pd.DataFrame, rsi_low: float = 30, adx_min: float = 20) -> pd.Series:
        """
        RSI+ADX Signal: RSI rises from <30 to >30 within last 2 bars AND ADX > 20 AND +DI > -DI
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            rsi = df['RSI']
            adx = df['ADX']
            di_plus = df['DI_Plus']
            di_minus = df['DI_Minus']

            # RSI crosses above 30 (was below 30 in last 2 bars)
            rsi_current = rsi > rsi_low
            rsi_was_low = (rsi.shift(1) < rsi_low) | (rsi.shift(2) < rsi_low)
            rsi_condition = rsi_current & rsi_was_low

            # ADX > 20 AND +DI > -DI
            adx_condition = adx > adx_min
            di_condition = di_plus > di_minus

            signals = rsi_condition & adx_condition & di_condition

            return signals

        except Exception as e:
            print(f"Error in rsi_adx_signal: {e}")
            return signals

    def bb_513_rsi(self, df: pd.DataFrame) -> pd.Series:
        """
        BB + 513 + RSI: Close < bb_mid and %b < 0.2 AND SMA5 > SMA13 AND RSI between 45-60
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            close = df['Close']
            bb_mid = df['BB_Mid']
            percent_b = df['Percent_B']
            sma5 = df['SMA_5']
            sma13 = df['SMA_13']
            rsi = df['RSI']

            # Near bands condition
            bb_condition = (close < bb_mid) & (percent_b < 0.2)

            # SMA5 > SMA13
            sma_condition = sma5 > sma13

            # RSI between 45-60
            rsi_condition = (rsi >= 45) & (rsi <= 60)

            signals = bb_condition & sma_condition & rsi_condition

            return signals

        except Exception as e:
            print(f"Error in bb_513_rsi: {e}")
            return signals

    def bb_513_adx(self, df: pd.DataFrame, adx_min: float = 18) -> pd.Series:
        """
        BB + 513 + ADX: Close rebounds above bb_lower within last 2 bars AND SMA5 > SMA13 AND ADX > 18
        """
        signals = pd.Series(False, index=df.index)

        if len(df) < 50:
            return signals

        try:
            close = df['Close']
            bb_lower = df['BB_Lower']
            sma5 = df['SMA_5']
            sma13 = df['SMA_13']
            adx = df['ADX']

            # Close rebounds above BB lower within last 2 bars
            rebound_condition = (close > bb_lower) & (
                (close.shift(1) <= bb_lower.shift(1)) | 
                (close.shift(2) <= bb_lower.shift(2))
            )

            # SMA5 > SMA13
            sma_condition = sma5 > sma13

            # ADX > 18
            adx_condition = adx > adx_min

            signals = rebound_condition & sma_condition & adx_condition

            return signals

        except Exception as e:
            print(f"Error in bb_513_adx: {e}")
            return signals

    def generate_all_signals(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Generate signals for all strategies"""
        signals = {}

        if df is None or df.empty:
            return signals

        try:
            signals['BB_Signal_513'] = self.bb_signal_513(df)
            signals['SMA_513_Crossover'] = self.sma_513_crossover(df)
            signals['MACD_Cross'] = self.macd_cross(df)
            signals['Dip_Buy_513'] = self.dip_buy_513(df)
            signals['MACD_Volume'] = self.macd_volume(df)
            signals['RSI_ADX_Signal'] = self.rsi_adx_signal(df)
            signals['BB_513_RSI'] = self.bb_513_rsi(df)
            signals['BB_513_ADX'] = self.bb_513_adx(df)

            return signals

        except Exception as e:
            print(f"Error generating signals: {e}")
            return {}

    def get_latest_signals(self, df: pd.DataFrame) -> Dict[str, bool]:
        """Get latest signals for all strategies"""
        all_signals = self.generate_all_signals(df)
        latest_signals = {}

        for strategy, signals in all_signals.items():
            if not signals.empty:
                latest_signals[strategy] = bool(signals.iloc[-1])
            else:
                latest_signals[strategy] = False

        return latest_signals

    def get_signal_summary(self, df: pd.DataFrame, days_back: int = 1) -> Dict:
        """Get summary of signals in recent days"""
        all_signals = self.generate_all_signals(df)

        summary = {
            'total_signals_today': 0,
            'active_strategies': [],
            'signal_details': {}
        }

        for strategy, signals in all_signals.items():
            if not signals.empty:
                recent_signals = signals.iloc[-days_back:].sum()
                summary['signal_details'][strategy] = {
                    'signals_count': int(recent_signals),
                    'latest_signal': bool(signals.iloc[-1])
                }

                if signals.iloc[-1]:
                    summary['total_signals_today'] += 1
                    summary['active_strategies'].append(strategy)

        return summary

    def validate_signal_quality(self, df: pd.DataFrame, strategy: str) -> Dict:
        """Validate signal quality with additional checks"""
        quality_score = 0
        reasons = []

        try:
            latest = df.iloc[-1]

            # Volume check
            volume_ratio = latest.get('Volume_Ratio', 1)
            if volume_ratio > 1.5:
                quality_score += 2
                reasons.append("High volume confirmation")
            elif volume_ratio > 1.0:
                quality_score += 1
                reasons.append("Above average volume")

            # Trend alignment
            close = latest['Close']
            sma_50 = latest.get('SMA_50', close)
            if close > sma_50:
                quality_score += 1
                reasons.append("Above 50-day SMA")

            # RSI not overbought
            rsi = latest.get('RSI', 50)
            if rsi < 70:
                quality_score += 1
                reasons.append("RSI not overbought")

            # ADX strength
            adx = latest.get('ADX', 20)
            if adx > 25:
                quality_score += 1
                reasons.append("Strong trend (ADX)")

            return {
                'quality_score': quality_score,
                'max_score': 5,
                'reasons': reasons,
                'grade': 'A' if quality_score >= 4 else 'B' if quality_score >= 2 else 'C'
            }

        except Exception as e:
            return {
                'quality_score': 0,
                'max_score': 5,
                'reasons': [f"Error: {str(e)}"],
                'grade': 'D'
            }

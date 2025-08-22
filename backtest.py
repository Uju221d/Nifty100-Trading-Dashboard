
"""
Backtesting Module for NIFTY 100 Trading Dashboard
Implements backtesting logic for all trading strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class Backtester:
    def __init__(self, 
                 entry_method: str = "next_open",  # "next_open" or "same_close"
                 exit_method: str = "time_based",  # "time_based" or "signal_based"
                 hold_days: int = 10,
                 transaction_cost: float = 0.001,  # 0.1% (10 bps)
                 slippage: float = 0.0005):  # 0.05% (5 bps)

        self.entry_method = entry_method
        self.exit_method = exit_method
        self.hold_days = hold_days
        self.transaction_cost = transaction_cost
        self.slippage = slippage

    def calculate_entry_price(self, df: pd.DataFrame, signal_idx: int) -> float:
        """Calculate entry price based on entry method"""
        try:
            if self.entry_method == "next_open":
                if signal_idx + 1 < len(df):
                    entry_price = df.iloc[signal_idx + 1]['Open']
                else:
                    return None  # Cannot enter after last bar
            else:  # same_close
                entry_price = df.iloc[signal_idx]['Close']

            # Apply slippage (assuming we pay slippage on entry)
            entry_price *= (1 + self.slippage)
            return entry_price

        except Exception:
            return None

    def calculate_exit_price(self, df: pd.DataFrame, entry_idx: int, entry_price: float) -> Tuple[float, int, str]:
        """Calculate exit price and reason"""
        try:
            # Determine exit index
            if self.entry_method == "next_open":
                start_idx = entry_idx + 1
            else:
                start_idx = entry_idx

            exit_idx = min(start_idx + self.hold_days, len(df) - 1)

            # Get exit price
            if self.exit_method == "time_based":
                exit_price = df.iloc[exit_idx]['Close']
                exit_reason = "Time-based"
            else:
                # For now, implement simple time-based exit
                # Can be extended for signal-based exits
                exit_price = df.iloc[exit_idx]['Close']
                exit_reason = "Time-based"

            # Apply slippage (we pay slippage on exit too)
            exit_price *= (1 - self.slippage)

            return exit_price, exit_idx, exit_reason

        except Exception:
            return None, None, "Error"

    def calculate_trade_metrics(self, entry_price: float, exit_price: float, 
                              entry_date: str, exit_date: str) -> Dict:
        """Calculate metrics for a single trade"""
        if entry_price is None or exit_price is None:
            return None

        # Calculate returns
        gross_return = (exit_price - entry_price) / entry_price

        # Apply transaction costs
        total_cost = 2 * self.transaction_cost  # Entry + Exit
        net_return = gross_return - total_cost

        # Calculate hold days
        try:
            entry_dt = pd.to_datetime(entry_date)
            exit_dt = pd.to_datetime(exit_date)
            hold_days = (exit_dt - entry_dt).days
        except:
            hold_days = self.hold_days

        return {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'entry_date': entry_date,
            'exit_date': exit_date,
            'gross_return': gross_return,
            'net_return': net_return,
            'hold_days': hold_days,
            'trade_pnl': net_return * 100  # Percentage
        }

    def backtest_strategy(self, df: pd.DataFrame, signals: pd.Series, 
                         strategy_name: str) -> Dict:
        """Backtest a single strategy"""
        if df is None or df.empty or signals.empty:
            return self._empty_backtest_result(strategy_name)

        trades = []
        signal_dates = df.index[signals].tolist()

        # Process each signal
        for i, signal_date in enumerate(signal_dates):
            signal_idx = df.index.get_loc(signal_date)

            # Calculate entry
            entry_price = self.calculate_entry_price(df, signal_idx)
            if entry_price is None:
                continue

            # Calculate exit
            exit_price, exit_idx, exit_reason = self.calculate_exit_price(
                df, signal_idx, entry_price)
            if exit_price is None:
                continue

            # Get dates
            if self.entry_method == "next_open" and signal_idx + 1 < len(df):
                entry_date = df.index[signal_idx + 1]
            else:
                entry_date = signal_date

            exit_date = df.index[exit_idx]

            # Calculate trade metrics
            trade_metrics = self.calculate_trade_metrics(
                entry_price, exit_price, entry_date, exit_date)

            if trade_metrics:
                trade_metrics['signal_date'] = signal_date
                trade_metrics['strategy'] = strategy_name
                trades.append(trade_metrics)

        # Calculate strategy performance
        return self._calculate_strategy_performance(trades, strategy_name, df)

    def _calculate_strategy_performance(self, trades: List[Dict], 
                                     strategy_name: str, df: pd.DataFrame) -> Dict:
        """Calculate overall strategy performance metrics"""
        if not trades:
            return self._empty_backtest_result(strategy_name)

        # Convert to DataFrame for easier calculations
        trades_df = pd.DataFrame(trades)

        # Basic metrics
        total_trades = len(trades)
        winning_trades = len(trades_df[trades_df['net_return'] > 0])
        losing_trades = len(trades_df[trades_df['net_return'] < 0])

        # Win ratio
        win_ratio = winning_trades / total_trades if total_trades > 0 else 0

        # Return metrics
        avg_return = trades_df['net_return'].mean()
        total_return = trades_df['net_return'].sum()

        # Win/Loss analysis
        winning_returns = trades_df[trades_df['net_return'] > 0]['net_return']
        losing_returns = trades_df[trades_df['net_return'] < 0]['net_return']

        avg_win = winning_returns.mean() if len(winning_returns) > 0 else 0
        avg_loss = losing_returns.mean() if len(losing_returns) > 0 else 0

        # Profit factor
        total_wins = winning_returns.sum() if len(winning_returns) > 0 else 0
        total_losses = abs(losing_returns.sum()) if len(losing_returns) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')

        # Risk metrics
        returns_std = trades_df['net_return'].std()
        max_drawdown = self._calculate_max_drawdown(trades_df['net_return'])

        # Sharpe ratio (annualized)
        avg_hold_days = trades_df['hold_days'].mean()
        if returns_std > 0 and avg_hold_days > 0:
            # Approximate annualization
            periods_per_year = 252 / avg_hold_days
            sharpe_ratio = (avg_return * np.sqrt(periods_per_year)) / returns_std
        else:
            sharpe_ratio = 0

        # Time-based metrics
        total_hold_days = trades_df['hold_days'].sum()
        trades_per_year = total_trades * 252 / len(df) if len(df) > 0 else 0

        # Recent performance (last 12 months)
        recent_date = df.index[-1] - timedelta(days=365)
        recent_trades = trades_df[pd.to_datetime(trades_df['entry_date']) >= recent_date]
        ltm_return = recent_trades['net_return'].sum() if len(recent_trades) > 0 else 0

        # CAGR calculation (approximate)
        if len(df) > 252:  # At least 1 year of data
            years = len(df) / 252
            cagr = ((1 + total_return) ** (1/years)) - 1 if total_return > -1 else -1
        else:
            cagr = 0

        return {
            'strategy_name': strategy_name,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_ratio': win_ratio,
            'avg_return': avg_return,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_hold_days': avg_hold_days,
            'trades_per_year': trades_per_year,
            'ltm_return': ltm_return,
            'cagr': cagr,
            'trades': trades
        }

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown from returns series"""
        try:
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            return drawdown.min()
        except:
            return 0

    def _empty_backtest_result(self, strategy_name: str) -> Dict:
        """Return empty backtest result structure"""
        return {
            'strategy_name': strategy_name,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_ratio': 0,
            'avg_return': 0,
            'total_return': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'avg_hold_days': 0,
            'trades_per_year': 0,
            'ltm_return': 0,
            'cagr': 0,
            'trades': []
        }

    def backtest_all_strategies(self, df: pd.DataFrame, 
                              all_signals: Dict[str, pd.Series]) -> Dict[str, Dict]:
        """Backtest all strategies and return results"""
        results = {}

        for strategy_name, signals in all_signals.items():
            try:
                result = self.backtest_strategy(df, signals, strategy_name)
                results[strategy_name] = result
            except Exception as e:
                print(f"Error backtesting {strategy_name}: {e}")
                results[strategy_name] = self._empty_backtest_result(strategy_name)

        return results

    def rank_strategies(self, backtest_results: Dict[str, Dict], 
                       win_ratio_weight: float = 0.5,
                       profit_factor_weight: float = 0.3,
                       ltm_return_weight: float = 0.2) -> List[Tuple[str, float]]:
        """Rank strategies based on weighted performance metrics"""
        strategy_scores = []

        for strategy_name, results in backtest_results.items():
            if results['total_trades'] == 0:
                score = 0
            else:
                # Normalize metrics for scoring
                win_ratio = results['win_ratio']
                profit_factor = min(results['profit_factor'], 5.0) / 5.0  # Cap at 5
                ltm_return = max(min(results['ltm_return'], 1.0), -1.0)  # Cap between -100% and 100%

                # Calculate weighted score
                score = (win_ratio * win_ratio_weight + 
                        profit_factor * profit_factor_weight + 
                        (ltm_return + 1) / 2 * ltm_return_weight)  # Normalize LTM to 0-1

            strategy_scores.append((strategy_name, score))

        # Sort by score descending
        strategy_scores.sort(key=lambda x: x[1], reverse=True)
        return strategy_scores

    def get_best_strategy(self, backtest_results: Dict[str, Dict]) -> Tuple[str, Dict]:
        """Get the best performing strategy"""
        ranked_strategies = self.rank_strategies(backtest_results)

        if ranked_strategies:
            best_strategy_name = ranked_strategies[0][0]
            return best_strategy_name, backtest_results[best_strategy_name]
        else:
            return None, None

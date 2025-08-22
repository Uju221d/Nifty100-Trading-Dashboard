
"""
NIFTY 100 Trading Dashboard - Main Streamlit Application
Production-ready dashboard for trading signal analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from data_loader import DataLoader
from indicators import TechnicalIndicators
from strategies import TradingStrategies
from backtest import Backtester

# Page configuration
st.set_page_config(
    page_title="NIFTY 100 Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .signal-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        margin: 0.1rem;
    }
    .signal-buy {
        background-color: #28a745;
        color: white;
    }
    .signal-none {
        background-color: #6c757d;
        color: white;
    }
    .recommended-strategy {
        background-color: #007bff;
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    def __init__(self):
        self.data_loader = DataLoader()
        self.indicators = TechnicalIndicators()
        self.strategies = TradingStrategies()
        self.backtester = Backtester()

        # Initialize session state
        if 'data_cache' not in st.session_state:
            st.session_state.data_cache = {}
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
        if 'backtest_cache' not in st.session_state:
            st.session_state.backtest_cache = {}

    def load_and_cache_data(self, symbols: list, force_refresh: bool = False):
        """Load and cache data for all symbols"""
        if force_refresh or not st.session_state.data_cache:
            with st.spinner(f"Loading data for {len(symbols)} stocks..."):
                progress_bar = st.progress(0)

                for i, symbol_info in enumerate(symbols):
                    symbol = symbol_info['symbol']
                    df = self.data_loader.get_latest_data(symbol)

                    if df is not None and len(df) > 100:
                        # Calculate indicators
                        df_with_indicators = self.indicators.calculate_all_indicators(df)
                        st.session_state.data_cache[symbol] = {
                            'data': df_with_indicators,
                            'company': symbol_info['company'],
                            'sector': symbol_info['sector']
                        }

                    progress_bar.progress((i + 1) / len(symbols))

                st.session_state.last_update = datetime.now()
                st.success(f"Loaded data for {len(st.session_state.data_cache)} stocks")

    def calculate_signals_and_backtest(self, symbol: str):
        """Calculate signals and backtest for a symbol"""
        if symbol not in st.session_state.data_cache:
            return None, None

        df = st.session_state.data_cache[symbol]['data']

        # Generate signals
        all_signals = self.strategies.generate_all_signals(df)
        latest_signals = self.strategies.get_latest_signals(df)

        # Backtest strategies
        backtest_results = self.backtester.backtest_all_strategies(df, all_signals)

        return latest_signals, backtest_results

    def get_recommended_strategy(self, backtest_results):
        """Get recommended strategy based on ranking"""
        if not backtest_results:
            return None, 0

        ranked = self.backtester.rank_strategies(backtest_results)
        if ranked:
            return ranked[0][0], ranked[0][1]
        return None, 0

    def create_stock_summary_table(self):
        """Create main summary table for all stocks"""
        summary_data = []

        for symbol, cache_data in st.session_state.data_cache.items():
            try:
                df = cache_data['data']
                latest = df.iloc[-1]

                # Get signals and backtest
                latest_signals, backtest_results = self.calculate_signals_and_backtest(symbol)

                if latest_signals and backtest_results:
                    # Count active signals
                    active_signals = [k for k, v in latest_signals.items() if v]
                    signal_count = len(active_signals)

                    # Get recommended strategy
                    recommended_strategy, strategy_score = self.get_recommended_strategy(backtest_results)

                    # Get performance metrics for recommended strategy
                    if recommended_strategy and recommended_strategy in backtest_results:
                        rec_results = backtest_results[recommended_strategy]
                        win_ratio = rec_results['win_ratio']
                        profit_factor = rec_results['profit_factor']
                        trades_per_year = rec_results['trades_per_year']
                        ltm_return = rec_results['ltm_return']
                    else:
                        win_ratio = profit_factor = trades_per_year = ltm_return = 0

                    summary_data.append({
                        'Symbol': symbol.replace('.NS', ''),
                        'Company': cache_data['company'],
                        'Sector': cache_data['sector'],
                        'Price': f"₹{latest['Close']:.2f}",
                        'Change %': f"{latest.get('Daily_Return', 0)*100:.2f}%",
                        'Signals Today': signal_count,
                        'Active Strategies': ', '.join(active_signals[:2]) + ('...' if len(active_signals) > 2 else ''),
                        'Recommended Strategy': recommended_strategy or 'None',
                        'Strategy Score': f"{strategy_score:.3f}",
                        'Win %': f"{win_ratio*100:.1f}%",
                        'Profit Factor': f"{profit_factor:.2f}",
                        'Trades/Year': f"{trades_per_year:.1f}",
                        'LTM Return': f"{ltm_return*100:.1f}%"
                    })

            except Exception as e:
                st.error(f"Error processing {symbol}: {e}")

        return pd.DataFrame(summary_data)

    def create_price_chart(self, symbol: str):
        """Create interactive price chart with indicators"""
        if symbol not in st.session_state.data_cache:
            return None

        df = st.session_state.data_cache[symbol]['data']
        company_name = st.session_state.data_cache[symbol]['company']

        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(f'{company_name} ({symbol})', 'MACD', 'RSI', 'Volume'),
            vertical_spacing=0.05,
            row_heights=[0.5, 0.2, 0.15, 0.15]
        )

        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price'
            ),
            row=1, col=1
        )

        # Bollinger Bands
        if 'BB_Upper' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Upper'], 
                          line=dict(color='gray', width=1), name='BB Upper'),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Lower'], 
                          line=dict(color='gray', width=1), name='BB Lower'),
                row=1, col=1
            )

        # Moving averages
        for sma in ['SMA_5', 'SMA_13', 'SMA_50', 'SMA_200']:
            if sma in df.columns:
                color = {'SMA_5': 'blue', 'SMA_13': 'red', 'SMA_50': 'green', 'SMA_200': 'purple'}[sma]
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[sma], 
                              line=dict(color=color, width=1), name=sma),
                    row=1, col=1
                )

        # MACD
        if 'MACD' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD'], 
                          line=dict(color='blue'), name='MACD'),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD_Signal'], 
                          line=dict(color='red'), name='Signal'),
                row=2, col=1
            )

        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['RSI'], 
                          line=dict(color='purple'), name='RSI'),
                row=3, col=1
            )
            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

        # Volume
        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'], name='Volume', 
                   marker_color='lightblue'),
            row=4, col=1
        )

        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"{company_name} Technical Analysis"
        )

        # Remove x-axis labels for all but bottom subplot
        fig.update_xaxes(showticklabels=False, row=1, col=1)
        fig.update_xaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(showticklabels=False, row=3, col=1)

        return fig

    def show_stock_detail(self, symbol: str):
        """Show detailed view for a specific stock"""
        if symbol not in st.session_state.data_cache:
            st.error(f"No data available for {symbol}")
            return

        cache_data = st.session_state.data_cache[symbol]
        df = cache_data['data']
        company_name = cache_data['company']
        sector = cache_data['sector']

        st.markdown(f"### {company_name} ({symbol}) - {sector}")

        # Get latest data
        latest = df.iloc[-1]
        latest_signals, backtest_results = self.calculate_signals_and_backtest(symbol)

        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Current Price", f"₹{latest['Close']:.2f}", 
                     f"{latest.get('Daily_Return', 0)*100:.2f}%")

        with col2:
            rsi = latest.get('RSI', 50)
            st.metric("RSI", f"{rsi:.1f}", 
                     "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral")

        with col3:
            volume_ratio = latest.get('Volume_Ratio', 1)
            st.metric("Volume Ratio", f"{volume_ratio:.2f}",
                     "High" if volume_ratio > 1.5 else "Normal")

        with col4:
            adx = latest.get('ADX', 20)
            st.metric("ADX (Trend Strength)", f"{adx:.1f}",
                     "Strong" if adx > 25 else "Weak")

        # Chart
        fig = self.create_price_chart(symbol)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Strategy performance table
        if backtest_results:
            st.markdown("#### Strategy Performance Comparison")

            strategy_data = []
            for strategy, results in backtest_results.items():
                strategy_data.append({
                    'Strategy': strategy,
                    'Signal Today': '✅' if latest_signals.get(strategy, False) else '❌',
                    'Total Trades': results['total_trades'],
                    'Win Ratio': f"{results['win_ratio']*100:.1f}%",
                    'Profit Factor': f"{results['profit_factor']:.2f}",
                    'Avg Return': f"{results['avg_return']*100:.2f}%",
                    'Max Drawdown': f"{results['max_drawdown']*100:.2f}%",
                    'Sharpe Ratio': f"{results['sharpe_ratio']:.2f}",
                    'Trades/Year': f"{results['trades_per_year']:.1f}",
                    'LTM Return': f"{results['ltm_return']*100:.1f}%"
                })

            strategy_df = pd.DataFrame(strategy_data)
            st.dataframe(strategy_df, use_container_width=True)

    def run_dashboard(self):
        """Main dashboard function"""
        st.markdown('<div class="main-header">📈 NIFTY 100 Trading Dashboard</div>', 
                   unsafe_allow_html=True)

        # Sidebar controls
        st.sidebar.markdown("## Controls")

        # Data refresh
        if st.sidebar.button("Refresh Data", type="primary"):
            st.session_state.data_cache = {}
            st.session_state.backtest_cache = {}
            st.rerun()

        # Load stock symbols
        symbols_data = self.data_loader.load_nifty100_symbols()

        # Initialize data
        if not st.session_state.data_cache:
            self.load_and_cache_data(symbols_data)

        # Filters
        st.sidebar.markdown("## Filters")

        # Sector filter
        sectors = sorted(set([s['sector'] for s in symbols_data]))
        selected_sectors = st.sidebar.multiselect("Select Sectors", sectors, default=sectors)

        # Signal filter
        signals_only = st.sidebar.checkbox("Show only stocks with signals today")

        # Price filter
        min_price = st.sidebar.number_input("Minimum Price (₹)", min_value=0.0, value=0.0)

        # Last update time
        if st.session_state.last_update:
            st.sidebar.markdown(f"**Last Updated:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

        # Main content
        tab1, tab2, tab3 = st.tabs(["📊 Stock Overview", "📈 Detailed Analysis", "📋 Global Analytics"])

        with tab1:
            st.markdown("### Stock Summary Table")

            if st.session_state.data_cache:
                summary_df = self.create_stock_summary_table()

                # Apply filters
                if selected_sectors:
                    summary_df = summary_df[summary_df['Sector'].isin(selected_sectors)]

                if signals_only:
                    summary_df = summary_df[summary_df['Signals Today'] > 0]

                if min_price > 0:
                    # Extract numeric value from price string
                    summary_df['Price_Numeric'] = summary_df['Price'].str.replace('₹', '').str.replace(',', '').astype(float)
                    summary_df = summary_df[summary_df['Price_Numeric'] >= min_price]
                    summary_df = summary_df.drop('Price_Numeric', axis=1)

                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Change %": st.column_config.NumberColumn(
                            "Change %",
                            format="%.2f%%"
                        ),
                        "Strategy Score": st.column_config.ProgressColumn(
                            "Strategy Score",
                            min_value=0,
                            max_value=1,
                        ),
                    }
                )

                # Export functionality
                if st.button("Export to CSV"):
                    csv = summary_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"nifty100_signals_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

            else:
                st.info("Loading data... Please wait.")

        with tab2:
            st.markdown("### Detailed Stock Analysis")

            if st.session_state.data_cache:
                # Stock selector
                stock_options = [(f"{info['symbol'].replace('.NS', '')} - {info['company']}", info['symbol']) 
                               for info in symbols_data if info['symbol'] in st.session_state.data_cache]

                if stock_options:
                    selected_display, selected_symbol = st.selectbox(
                        "Select Stock for Detailed Analysis",
                        stock_options,
                        format_func=lambda x: x[0]
                    )

                    self.show_stock_detail(selected_symbol)
                else:
                    st.info("No stock data available for detailed analysis.")
            else:
                st.info("Please wait for data to load.")

        with tab3:
            st.markdown("### Global Analytics")

            if st.session_state.data_cache:
                # Signal count by strategy
                strategy_counts = {strategy: 0 for strategy in self.strategies.strategy_names}
                sector_signals = {}

                for symbol, cache_data in st.session_state.data_cache.items():
                    latest_signals, _ = self.calculate_signals_and_backtest(symbol)
                    sector = cache_data['sector']

                    if latest_signals:
                        for strategy, has_signal in latest_signals.items():
                            if has_signal:
                                strategy_counts[strategy] += 1

                        if sector not in sector_signals:
                            sector_signals[sector] = 0
                        sector_signals[sector] += sum(latest_signals.values())

                # Strategy signals chart
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Signals by Strategy Today")
                    strategy_df = pd.DataFrame([
                        {'Strategy': k, 'Signals': v} for k, v in strategy_counts.items()
                    ])

                    fig_strategy = px.bar(strategy_df, x='Strategy', y='Signals',
                                        title="BUY Signals by Strategy")
                    fig_strategy.update_xaxes(tickangle=45)
                    st.plotly_chart(fig_strategy, use_container_width=True)

                with col2:
                    st.markdown("#### Signals by Sector Today")
                    if sector_signals:
                        sector_df = pd.DataFrame([
                            {'Sector': k, 'Signals': v} for k, v in sector_signals.items()
                        ])

                        fig_sector = px.pie(sector_df, values='Signals', names='Sector',
                                          title="Signal Distribution by Sector")
                        st.plotly_chart(fig_sector, use_container_width=True)
                    else:
                        st.info("No signals found across sectors today.")

                # Top performers
                st.markdown("#### Top 10 Stocks by Strategy Score")
                summary_df = self.create_stock_summary_table()
                if not summary_df.empty:
                    summary_df['Score_Numeric'] = summary_df['Strategy Score'].astype(float)
                    top_10 = summary_df.nlargest(10, 'Score_Numeric')[
                        ['Symbol', 'Company', 'Sector', 'Recommended Strategy', 'Strategy Score', 'Win %', 'LTM Return']
                    ]
                    st.dataframe(top_10, use_container_width=True, hide_index=True)

            else:
                st.info("Analytics will be available once data is loaded.")

# Run the dashboard
if __name__ == "__main__":
    dashboard = TradingDashboard()
    dashboard.run_dashboard()

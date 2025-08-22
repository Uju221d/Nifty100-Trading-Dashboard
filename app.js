// NIFTY 100 Trading Dashboard - Main Application
class TradingDashboard {
    constructor() {
        this.stocks = [];
        this.currentStock = null;
        this.charts = {};
        this.strategies = [
            'BB Signal + 513',
            'SMA 513 Crossover', 
            'MACD Cross',
            'Dip Buy + 513',
            'MACD + Volume',
            'RSI + ADX',
            'BB + 513 + RSI',
            'BB + 513 + ADX'
        ];
        
        this.init();
    }

    // Initialize the application
    init() {
        this.generateStockData();
        this.calculateTechnicalIndicators();
        this.runBacktesting();
        this.setupEventListeners();
        this.initializeUI();
        this.updateHeaderMetrics();
    }

    // Generate realistic stock data for 2 years
    generateStockData() {
        const stocksData = [
            { symbol: "HDFCBANK", company: "HDFC Bank Ltd", sector: "Banking", base_price: 1650, volatility: 0.15 },
            { symbol: "ICICIBANK", company: "ICICI Bank Ltd", sector: "Banking", base_price: 1200, volatility: 0.16 },
            { symbol: "SBIN", company: "State Bank of India", sector: "Banking", base_price: 800, volatility: 0.18 },
            { symbol: "TCS", company: "Tata Consultancy Services", sector: "IT", base_price: 3500, volatility: 0.20 },
            { symbol: "INFY", company: "Infosys", sector: "IT", base_price: 1800, volatility: 0.19 },
            { symbol: "WIPRO", company: "Wipro", sector: "IT", base_price: 650, volatility: 0.21 },
            { symbol: "RELIANCE", company: "Reliance Industries", sector: "Oil & Gas", base_price: 2800, volatility: 0.17 },
            { symbol: "ONGC", company: "Oil & Natural Gas Corp", sector: "Oil & Gas", base_price: 300, volatility: 0.22 },
            { symbol: "HINDUNILVR", company: "Hindustan Unilever", sector: "FMCG", base_price: 2400, volatility: 0.12 },
            { symbol: "ITC", company: "ITC Ltd", sector: "FMCG", base_price: 480, volatility: 0.14 },
            { symbol: "MARUTI", company: "Maruti Suzuki", sector: "Auto", base_price: 11000, volatility: 0.18 },
            { symbol: "TATAMOTORS", company: "Tata Motors", sector: "Auto", base_price: 900, volatility: 0.25 },
            { symbol: "SUNPHARMA", company: "Sun Pharmaceutical", sector: "Pharma", base_price: 1600, volatility: 0.16 },
            { symbol: "DRREDDY", company: "Dr Reddy's Labs", sector: "Pharma", base_price: 6500, volatility: 0.17 },
            { symbol: "TATASTEEL", company: "Tata Steel", sector: "Metals", base_price: 150, volatility: 0.24 },
            { symbol: "JSWSTEEL", company: "JSW Steel", sector: "Metals", base_price: 900, volatility: 0.23 },
            { symbol: "LT", company: "Larsen & Toubro", sector: "Infrastructure", base_price: 3600, volatility: 0.19 },
            { symbol: "ULTRACEMCO", company: "UltraTech Cement", sector: "Construction Materials", base_price: 10000, volatility: 0.20 },
            { symbol: "NTPC", company: "NTPC", sector: "Power", base_price: 350, volatility: 0.16 },
            { symbol: "POWERGRID", company: "Power Grid Corp", sector: "Power", base_price: 250, volatility: 0.15 },
            { symbol: "BHARTIARTL", company: "Bharti Airtel", sector: "Telecom", base_price: 1500, volatility: 0.17 },
            { symbol: "ASIANPAINT", company: "Asian Paints", sector: "Paints", base_price: 2800, volatility: 0.16 },
            { symbol: "NESTLEIND", company: "Nestle India", sector: "FMCG", base_price: 24000, volatility: 0.13 },
            { symbol: "KOTAKBANK", company: "Kotak Mahindra Bank", sector: "Banking", base_price: 1800, volatility: 0.16 },
            { symbol: "BAJFINANCE", company: "Bajaj Finance", sector: "Financial Services", base_price: 7000, volatility: 0.20 }
        ];

        this.stocks = stocksData.map(stock => this.generateStockPriceData(stock));
    }

    // Generate 2 years of daily price data for a stock
    generateStockPriceData(stockInfo) {
        const data = [];
        const startDate = new Date('2023-01-01');
        const endDate = new Date('2025-01-01');
        const totalDays = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));
        
        let price = stockInfo.base_price;
        let trend = (Math.random() - 0.5) * 2; // Random trend direction
        
        for (let i = 0; i < totalDays; i++) {
            const date = new Date(startDate);
            date.setDate(date.getDate() + i);
            
            // Skip weekends
            if (date.getDay() === 0 || date.getDay() === 6) continue;
            
            // Add some trend and random walk
            const dailyReturn = (Math.random() - 0.5) * stockInfo.volatility + trend * 0.01;
            const priceChange = price * dailyReturn;
            
            const open = price;
            const high = open * (1 + Math.random() * 0.03);
            const low = open * (1 - Math.random() * 0.03);
            const close = Math.max(low, Math.min(high, open + priceChange));
            
            const baseVolume = 1000000 + Math.random() * 2000000;
            const volume = Math.floor(baseVolume * (1 + Math.abs(dailyReturn) * 5));
            
            data.push({
                date: date.toISOString().split('T')[0],
                open: Math.round(open * 100) / 100,
                high: Math.round(high * 100) / 100,
                low: Math.round(low * 100) / 100,
                close: Math.round(close * 100) / 100,
                volume: volume
            });
            
            price = close;
            
            // Occasionally change trend
            if (Math.random() < 0.02) {
                trend = (Math.random() - 0.5) * 2;
            }
        }
        
        return {
            ...stockInfo,
            data: data,
            currentPrice: data[data.length - 1].close,
            dailyChange: ((data[data.length - 1].close - data[data.length - 2].close) / data[data.length - 2].close) * 100
        };
    }

    // Calculate technical indicators
    calculateTechnicalIndicators() {
        this.stocks.forEach(stock => {
            const prices = stock.data.map(d => d.close);
            const highs = stock.data.map(d => d.high);
            const lows = stock.data.map(d => d.low);
            const volumes = stock.data.map(d => d.volume);
            
            // SMAs
            stock.sma5 = this.calculateSMA(prices, 5);
            stock.sma13 = this.calculateSMA(prices, 13);
            stock.sma50 = this.calculateSMA(prices, 50);
            stock.sma200 = this.calculateSMA(prices, 200);
            
            // EMAs
            stock.ema10 = this.calculateEMA(prices, 10);
            stock.ema30 = this.calculateEMA(prices, 30);
            
            // RSI
            stock.rsi = this.calculateRSI(prices, 14);
            
            // MACD
            const macdData = this.calculateMACD(prices);
            stock.macd = macdData.macd;
            stock.macdSignal = macdData.signal;
            stock.macdHist = macdData.histogram;
            
            // Bollinger Bands
            const bbData = this.calculateBollingerBands(prices, 20, 2);
            stock.bbUpper = bbData.upper;
            stock.bbMiddle = bbData.middle;
            stock.bbLower = bbData.lower;
            stock.bbPercent = bbData.percent;
            
            // ADX
            const adxData = this.calculateADX(highs, lows, prices, 14);
            stock.adx = adxData.adx;
            stock.plusDI = adxData.plusDI;
            stock.minusDI = adxData.minusDI;
            
            // Volume indicators
            stock.volumeMA = this.calculateSMA(volumes, 20);
        });
    }

    // Simple Moving Average
    calculateSMA(data, period) {
        const result = [];
        for (let i = 0; i < data.length; i++) {
            if (i < period - 1) {
                result.push(null);
            } else {
                const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
                result.push(sum / period);
            }
        }
        return result;
    }

    // Exponential Moving Average
    calculateEMA(data, period) {
        const result = [];
        const multiplier = 2 / (period + 1);
        result[0] = data[0];
        
        for (let i = 1; i < data.length; i++) {
            result[i] = (data[i] * multiplier) + (result[i - 1] * (1 - multiplier));
        }
        return result;
    }

    // RSI Calculation
    calculateRSI(data, period) {
        const result = [];
        const changes = [];
        
        for (let i = 1; i < data.length; i++) {
            changes.push(data[i] - data[i - 1]);
        }
        
        for (let i = 0; i < changes.length; i++) {
            if (i < period - 1) {
                result.push(null);
            } else {
                const gains = changes.slice(i - period + 1, i + 1).map(c => c > 0 ? c : 0);
                const losses = changes.slice(i - period + 1, i + 1).map(c => c < 0 ? -c : 0);
                
                const avgGain = gains.reduce((a, b) => a + b, 0) / period;
                const avgLoss = losses.reduce((a, b) => a + b, 0) / period;
                
                const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
                const rsi = 100 - (100 / (1 + rs));
                result.push(rsi);
            }
        }
        
        result.unshift(null); // Add null for first element
        return result;
    }

    // MACD Calculation
    calculateMACD(data) {
        const ema12 = this.calculateEMA(data, 12);
        const ema26 = this.calculateEMA(data, 26);
        const macd = [];
        
        for (let i = 0; i < data.length; i++) {
            if (ema12[i] !== null && ema26[i] !== null) {
                macd.push(ema12[i] - ema26[i]);
            } else {
                macd.push(null);
            }
        }
        
        const signal = this.calculateEMA(macd.filter(m => m !== null), 9);
        const histogram = [];
        
        let signalIndex = 0;
        for (let i = 0; i < macd.length; i++) {
            if (macd[i] !== null) {
                if (signal[signalIndex] !== undefined) {
                    histogram.push(macd[i] - signal[signalIndex]);
                } else {
                    histogram.push(null);
                }
                signalIndex++;
            } else {
                histogram.push(null);
            }
        }
        
        return { macd, signal: this.padArrayToLength(signal, data.length), histogram };
    }

    // Bollinger Bands Calculation
    calculateBollingerBands(data, period, stdDev) {
        const sma = this.calculateSMA(data, period);
        const upper = [];
        const lower = [];
        const percent = [];
        
        for (let i = 0; i < data.length; i++) {
            if (sma[i] !== null) {
                const slice = data.slice(i - period + 1, i + 1);
                const variance = slice.reduce((sum, val) => sum + Math.pow(val - sma[i], 2), 0) / period;
                const stdDeviation = Math.sqrt(variance);
                
                upper.push(sma[i] + (stdDeviation * stdDev));
                lower.push(sma[i] - (stdDeviation * stdDev));
                
                // %B calculation
                const pctB = (data[i] - lower[i]) / (upper[i] - lower[i]);
                percent.push(pctB);
            } else {
                upper.push(null);
                lower.push(null);
                percent.push(null);
            }
        }
        
        return { upper, middle: sma, lower, percent };
    }

    // ADX Calculation (simplified)
    calculateADX(highs, lows, closes, period) {
        const trueRanges = [];
        const plusDMs = [];
        const minusDMs = [];
        
        for (let i = 1; i < closes.length; i++) {
            const tr = Math.max(
                highs[i] - lows[i],
                Math.abs(highs[i] - closes[i - 1]),
                Math.abs(lows[i] - closes[i - 1])
            );
            trueRanges.push(tr);
            
            const plusDM = highs[i] - highs[i - 1] > lows[i - 1] - lows[i] ? 
                Math.max(highs[i] - highs[i - 1], 0) : 0;
            const minusDM = lows[i - 1] - lows[i] > highs[i] - highs[i - 1] ? 
                Math.max(lows[i - 1] - lows[i], 0) : 0;
            
            plusDMs.push(plusDM);
            minusDMs.push(minusDM);
        }
        
        const atr = this.calculateSMA(trueRanges, period);
        const plusDI = [];
        const minusDI = [];
        const adx = [];
        
        for (let i = 0; i < atr.length; i++) {
            if (atr[i] !== null && atr[i] !== 0) {
                plusDI.push((plusDMs[i] / atr[i]) * 100);
                minusDI.push((minusDMs[i] / atr[i]) * 100);
                
                const dx = Math.abs(plusDI[i] - minusDI[i]) / (plusDI[i] + minusDI[i]) * 100;
                adx.push(dx);
            } else {
                plusDI.push(null);
                minusDI.push(null);
                adx.push(null);
            }
        }
        
        // Smooth ADX
        const smoothedADX = this.calculateSMA(adx, period);
        
        return {
            adx: this.padArrayToLength(smoothedADX, closes.length),
            plusDI: this.padArrayToLength(plusDI, closes.length),
            minusDI: this.padArrayToLength(minusDI, closes.length)
        };
    }

    padArrayToLength(arr, length) {
        const result = new Array(length).fill(null);
        const offset = length - arr.length;
        for (let i = 0; i < arr.length; i++) {
            result[i + offset] = arr[i];
        }
        return result;
    }

    // Trading Strategy Implementations
    runBacktesting() {
        this.stocks.forEach(stock => {
            stock.strategies = {};
            
            // Strategy 1: BB Signal + 513
            stock.strategies['BB Signal + 513'] = this.backtestBBSignal513(stock);
            
            // Strategy 2: SMA 513 Crossover
            stock.strategies['SMA 513 Crossover'] = this.backtestSMA513(stock);
            
            // Strategy 3: MACD Cross
            stock.strategies['MACD Cross'] = this.backtestMACDCross(stock);
            
            // Strategy 4: Dip Buy + 513
            stock.strategies['Dip Buy + 513'] = this.backtestDipBuy513(stock);
            
            // Strategy 5: MACD + Volume
            stock.strategies['MACD + Volume'] = this.backtestMACDVolume(stock);
            
            // Strategy 6: RSI + ADX
            stock.strategies['RSI + ADX'] = this.backtestRSIADX(stock);
            
            // Strategy 7: BB + 513 + RSI
            stock.strategies['BB + 513 + RSI'] = this.backtestBB513RSI(stock);
            
            // Strategy 8: BB + 513 + ADX
            stock.strategies['BB + 513 + ADX'] = this.backtestBB513ADX(stock);
            
            // Calculate recommended strategy
            stock.recommendedStrategy = this.getRecommendedStrategy(stock);
        });
    }

    // Strategy backtesting methods
    backtestBBSignal513(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 13 || !stock.bbPercent[i] || !stock.sma5[i] || !stock.sma13[i]) return false;
            
            // BB breakout + SMA crossover within 3 bars
            const bbBreakout = stock.bbPercent[i] > 1 || stock.bbPercent[i] < 0;
            const smaSignal = stock.sma5[i] > stock.sma13[i];
            
            // Check if SMA crossover happened within last 3 bars
            let recentCrossover = false;
            for (let j = Math.max(0, i - 3); j <= i; j++) {
                if (j > 0 && stock.sma5[j] > stock.sma13[j] && stock.sma5[j-1] <= stock.sma13[j-1]) {
                    recentCrossover = true;
                    break;
                }
            }
            
            return bbBreakout && smaSignal && recentCrossover;
        });
    }

    backtestSMA513(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 13 || !stock.sma5[i] || !stock.sma13[i]) return false;
            return i > 0 && stock.sma5[i] > stock.sma13[i] && stock.sma5[i-1] <= stock.sma13[i-1];
        });
    }

    backtestMACDCross(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 26 || !stock.macd[i] || !stock.macdSignal[i]) return false;
            return i > 0 && stock.macd[i] > stock.macdSignal[i] && 
                   stock.macd[i-1] <= stock.macdSignal[i-1] && stock.macd[i] < 0;
        });
    }

    backtestDipBuy513(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 13 || !stock.sma5[i] || !stock.sma13[i]) return false;
            const dailyReturn = i > 0 ? (stock.data[i].close - stock.data[i-1].close) / stock.data[i-1].close : 0;
            return dailyReturn < -0.04 && stock.sma5[i] > stock.sma13[i];
        });
    }

    backtestMACDVolume(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 26 || !stock.macd[i] || !stock.macdSignal[i] || !stock.volumeMA[i]) return false;
            return stock.macd[i] > stock.macdSignal[i] && stock.data[i].volume > stock.volumeMA[i] * 1.2;
        });
    }

    backtestRSIADX(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 14 || !stock.rsi[i] || !stock.adx[i] || !stock.plusDI[i] || !stock.minusDI[i]) return false;
            const rsiRecovery = i > 0 && stock.rsi[i-1] < 30 && stock.rsi[i] > 30;
            return rsiRecovery && stock.adx[i] > 20 && stock.plusDI[i] > stock.minusDI[i];
        });
    }

    backtestBB513RSI(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 20 || !stock.bbPercent[i] || !stock.sma5[i] || !stock.sma13[i] || !stock.rsi[i]) return false;
            const nearBands = stock.bbPercent[i] < 0.2 || stock.bbPercent[i] > 0.8;
            return nearBands && stock.sma5[i] > stock.sma13[i] && stock.rsi[i] >= 45 && stock.rsi[i] <= 60;
        });
    }

    backtestBB513ADX(stock) {
        return this.executeBacktest(stock, (i) => {
            if (i < 20 || !stock.bbPercent[i] || !stock.sma5[i] || !stock.sma13[i] || !stock.adx[i]) return false;
            const bbRebound = i > 0 && stock.bbPercent[i-1] < 0.2 && stock.bbPercent[i] > 0.2;
            return bbRebound && stock.sma5[i] > stock.sma13[i] && stock.adx[i] > 18;
        });
    }

    executeBacktest(stock, signalFunction) {
        const trades = [];
        const signals = [];
        let position = null;
        
        for (let i = 0; i < stock.data.length; i++) {
            signals.push(false);
            
            // Check for entry signal
            if (!position && signalFunction(i)) {
                signals[i] = true;
                
                // Enter position at next day's open (if available)
                if (i < stock.data.length - 1) {
                    position = {
                        entryPrice: stock.data[i + 1].open,
                        entryDate: i + 1,
                        entryIndex: i
                    };
                }
            }
            
            // Check for exit (10 trading days)
            if (position && i >= position.entryDate + 10) {
                const exitPrice = stock.data[i].open;
                const grossReturn = (exitPrice - position.entryPrice) / position.entryPrice;
                const netReturn = grossReturn - 0.001 - 0.0005; // Transaction costs + slippage
                
                trades.push({
                    entryPrice: position.entryPrice,
                    exitPrice: exitPrice,
                    return: netReturn,
                    days: i - position.entryDate
                });
                
                position = null;
            }
        }
        
        // Calculate performance metrics
        const performance = this.calculatePerformanceMetrics(trades);
        return { signals, trades, ...performance };
    }

    calculatePerformanceMetrics(trades) {
        if (trades.length === 0) {
            return {
                winRate: 0,
                profitFactor: 0,
                avgReturn: 0,
                maxDrawdown: 0,
                sharpeRatio: 0,
                cagr: 0,
                totalTrades: 0
            };
        }
        
        const winningTrades = trades.filter(t => t.return > 0);
        const losingTrades = trades.filter(t => t.return <= 0);
        
        const winRate = (winningTrades.length / trades.length) * 100;
        const avgWin = winningTrades.length > 0 ? winningTrades.reduce((sum, t) => sum + t.return, 0) / winningTrades.length : 0;
        const avgLoss = losingTrades.length > 0 ? Math.abs(losingTrades.reduce((sum, t) => sum + t.return, 0) / losingTrades.length) : 0;
        const profitFactor = avgLoss > 0 ? avgWin / avgLoss : 0;
        const avgReturn = trades.reduce((sum, t) => sum + t.return, 0) / trades.length;
        
        // Calculate CAGR (assuming average holding period)
        const avgHoldingDays = trades.reduce((sum, t) => sum + t.days, 0) / trades.length;
        const tradesPerYear = 252 / avgHoldingDays; // 252 trading days per year
        const cagr = Math.pow(1 + avgReturn, tradesPerYear) - 1;
        
        // Simplified Sharpe ratio
        const returns = trades.map(t => t.return);
        const stdDev = this.calculateStandardDeviation(returns);
        const sharpeRatio = stdDev > 0 ? (avgReturn * Math.sqrt(tradesPerYear)) / (stdDev * Math.sqrt(tradesPerYear)) : 0;
        
        // Max drawdown calculation (simplified)
        let maxDrawdown = 0;
        let runningReturn = 1;
        let peak = 1;
        
        trades.forEach(trade => {
            runningReturn *= (1 + trade.return);
            if (runningReturn > peak) peak = runningReturn;
            const drawdown = (peak - runningReturn) / peak;
            if (drawdown > maxDrawdown) maxDrawdown = drawdown;
        });
        
        return {
            winRate: Math.round(winRate * 100) / 100,
            profitFactor: Math.round(profitFactor * 100) / 100,
            avgReturn: Math.round(avgReturn * 10000) / 100,
            maxDrawdown: Math.round(maxDrawdown * 10000) / 100,
            sharpeRatio: Math.round(sharpeRatio * 100) / 100,
            cagr: Math.round(cagr * 10000) / 100,
            totalTrades: trades.length
        };
    }

    calculateStandardDeviation(values) {
        const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
        const squareDiffs = values.map(val => Math.pow(val - avg, 2));
        const avgSquareDiff = squareDiffs.reduce((sum, val) => sum + val, 0) / squareDiffs.length;
        return Math.sqrt(avgSquareDiff);
    }

    getRecommendedStrategy(stock) {
        const strategies = Object.keys(stock.strategies);
        let bestStrategy = strategies[0];
        let bestScore = 0;
        
        strategies.forEach(strategy => {
            const perf = stock.strategies[strategy];
            if (perf.totalTrades > 0) {
                // Scoring: Win Rate (50%) + Profit Factor (30%) + LTM Return (20%)
                const score = (perf.winRate * 0.5) + (perf.profitFactor * 30 * 0.3) + (perf.cagr * 0.2);
                if (score > bestScore) {
                    bestScore = score;
                    bestStrategy = strategy;
                }
            }
        });
        
        return { name: bestStrategy, score: Math.round(bestScore * 100) / 100 };
    }

    // UI Setup and Event Listeners
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Filters
        document.getElementById('sector-filter').addEventListener('change', () => this.filterStocks());
        document.getElementById('signals-only').addEventListener('change', () => this.filterStocks());
        document.getElementById('price-range').addEventListener('input', (e) => {
            document.getElementById('price-range-max').textContent = e.target.value;
            this.filterStocks();
        });
        
        // Table sorting
        document.querySelectorAll('.sortable').forEach(header => {
            header.addEventListener('click', () => this.sortTable(header.dataset.sort));
        });
        
        // Stock selection for detailed analysis
        document.getElementById('stock-selector').addEventListener('change', (e) => {
            this.currentStock = this.stocks.find(s => s.symbol === e.target.value);
            this.updateDetailedAnalysis();
        });
        
        // Export CSV
        document.getElementById('export-csv').addEventListener('click', () => this.exportCSV());
    }

    initializeUI() {
        // Initialize last update time
        document.getElementById('last-update').textContent = new Date().toLocaleString();
        
        // Populate sector filter
        const sectors = [...new Set(this.stocks.map(s => s.sector))];
        const sectorFilter = document.getElementById('sector-filter');
        sectors.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = sector;
            sectorFilter.appendChild(option);
        });
        
        // Populate stock selector
        const stockSelector = document.getElementById('stock-selector');
        this.stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.symbol;
            option.textContent = `${stock.symbol} - ${stock.company}`;
            stockSelector.appendChild(option);
        });
        
        // Set first stock as current
        this.currentStock = this.stocks[0];
        
        // Initialize all sections
        this.updateStockTable();
        this.updateDetailedAnalysis();
        this.updateAnalytics();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        
        // Update content based on active tab
        if (tabName === 'analytics') {
            this.updateAnalytics();
        } else if (tabName === 'analysis') {
            this.updateDetailedAnalysis();
        }
    }

    updateHeaderMetrics() {
        const totalSignals = this.stocks.reduce((sum, stock) => {
            return sum + Object.values(stock.strategies).reduce((stratSum, strat) => {
                const lastSignals = strat.signals.slice(-1)[0];
                return stratSum + (lastSignals ? 1 : 0);
            }, 0);
        }, 0);
        
        // Find best performing sector
        const sectorPerformance = {};
        this.stocks.forEach(stock => {
            if (!sectorPerformance[stock.sector]) {
                sectorPerformance[stock.sector] = { total: 0, count: 0 };
            }
            sectorPerformance[stock.sector].total += stock.dailyChange;
            sectorPerformance[stock.sector].count++;
        });
        
        let bestSector = '';
        let bestPerformance = -Infinity;
        Object.keys(sectorPerformance).forEach(sector => {
            const avgPerf = sectorPerformance[sector].total / sectorPerformance[sector].count;
            if (avgPerf > bestPerformance) {
                bestPerformance = avgPerf;
                bestSector = sector;
            }
        });
        
        document.getElementById('active-signals').textContent = totalSignals;
        document.getElementById('best-sector').textContent = bestSector;
    }

    updateStockTable() {
        const tableBody = document.getElementById('stock-table-body');
        tableBody.innerHTML = '';
        
        this.getFilteredStocks().forEach(stock => {
            const row = document.createElement('tr');
            row.onclick = () => {
                document.getElementById('stock-selector').value = stock.symbol;
                this.currentStock = stock;
                this.switchTab('analysis');
                this.updateDetailedAnalysis();
            };
            
            // Count active signals
            const activeSignals = Object.values(stock.strategies).filter(strat => 
                strat.signals[strat.signals.length - 1]
            ).length;
            
            const signalBadges = activeSignals > 0 ? 
                `<span class="signal-count">${activeSignals}</span>` : 
                `<span class="signal-count signal-count--zero">0</span>`;
            
            const changeClass = stock.dailyChange >= 0 ? 'change-positive' : 'change-negative';
            const changeSymbol = stock.dailyChange >= 0 ? '+' : '';
            
            row.innerHTML = `
                <td>
                    <div class="stock-info">
                        <div class="stock-symbol">${stock.symbol}</div>
                        <div class="stock-company">${stock.company}</div>
                    </div>
                </td>
                <td>
                    <div class="price-info">
                        <div class="price">₹${stock.currentPrice.toFixed(2)}</div>
                    </div>
                </td>
                <td class="${changeClass}">
                    ${changeSymbol}${stock.dailyChange.toFixed(2)}%
                </td>
                <td>${stock.sector}</td>
                <td>${signalBadges}</td>
                <td>
                    <div class="recommended-strategy">
                        <div class="strategy-name">${stock.recommendedStrategy.name}</div>
                        <div class="strategy-score">Score: ${stock.recommendedStrategy.score}</div>
                    </div>
                </td>
                <td>${stock.strategies[stock.recommendedStrategy.name].winRate}%</td>
                <td>${stock.strategies[stock.recommendedStrategy.name].profitFactor}</td>
                <td class="${stock.strategies[stock.recommendedStrategy.name].cagr >= 0 ? 'change-positive' : 'change-negative'}">
                    ${stock.strategies[stock.recommendedStrategy.name].cagr.toFixed(2)}%
                </td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    getFilteredStocks() {
        const sectorFilter = document.getElementById('sector-filter').value;
        const signalsOnly = document.getElementById('signals-only').checked;
        const maxPrice = parseFloat(document.getElementById('price-range').value);
        
        return this.stocks.filter(stock => {
            // Sector filter
            if (sectorFilter && stock.sector !== sectorFilter) return false;
            
            // Price filter
            if (stock.currentPrice > maxPrice) return false;
            
            // Signals filter
            if (signalsOnly) {
                const hasSignals = Object.values(stock.strategies).some(strat => 
                    strat.signals[strat.signals.length - 1]
                );
                if (!hasSignals) return false;
            }
            
            return true;
        });
    }

    filterStocks() {
        this.updateStockTable();
    }

    sortTable(column) {
        // Implementation would sort the filtered stocks and update table
        // For brevity, simplified implementation
        this.updateStockTable();
    }

    updateDetailedAnalysis() {
        if (!this.currentStock) return;
        
        this.createPriceChart();
        this.createIndicatorCharts();
        this.updateCurrentSignals();
        this.updateStrategyComparison();
    }

    createPriceChart() {
        const ctx = document.getElementById('price-chart').getContext('2d');
        
        if (this.charts.priceChart) {
            this.charts.priceChart.destroy();
        }
        
        const stock = this.currentStock;
        const labels = stock.data.map(d => d.date);
        
        this.charts.priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Price',
                    data: stock.data.map(d => d.close),
                    borderColor: '#1FB8CD',
                    backgroundColor: 'rgba(31, 184, 205, 0.1)',
                    fill: false
                }, {
                    label: 'SMA 5',
                    data: stock.sma5,
                    borderColor: '#FFC185',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderWidth: 1
                }, {
                    label: 'SMA 13',
                    data: stock.sma13,
                    borderColor: '#B4413C',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderWidth: 1
                }, {
                    label: 'BB Upper',
                    data: stock.bbUpper,
                    borderColor: 'rgba(93, 135, 143, 0.5)',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderWidth: 1,
                    borderDash: [5, 5]
                }, {
                    label: 'BB Lower',
                    data: stock.bbLower,
                    borderColor: 'rgba(93, 135, 143, 0.5)',
                    backgroundColor: 'transparent',
                    fill: false,
                    borderWidth: 1,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        display: true
                    },
                    y: {
                        display: true
                    }
                },
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }

    createIndicatorCharts() {
        // MACD Chart
        const macdCtx = document.getElementById('macd-chart').getContext('2d');
        if (this.charts.macdChart) this.charts.macdChart.destroy();
        
        this.charts.macdChart = new Chart(macdCtx, {
            type: 'line',
            data: {
                labels: this.currentStock.data.map(d => d.date),
                datasets: [{
                    label: 'MACD',
                    data: this.currentStock.macd,
                    borderColor: '#1FB8CD',
                    backgroundColor: 'transparent',
                    fill: false
                }, {
                    label: 'Signal',
                    data: this.currentStock.macdSignal,
                    borderColor: '#FFC185',
                    backgroundColor: 'transparent',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { display: true } },
                plugins: { legend: { display: true } }
            }
        });

        // RSI Chart
        const rsiCtx = document.getElementById('rsi-chart').getContext('2d');
        if (this.charts.rsiChart) this.charts.rsiChart.destroy();
        
        this.charts.rsiChart = new Chart(rsiCtx, {
            type: 'line',
            data: {
                labels: this.currentStock.data.map(d => d.date),
                datasets: [{
                    label: 'RSI',
                    data: this.currentStock.rsi,
                    borderColor: '#B4413C',
                    backgroundColor: 'transparent',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { 
                    y: { 
                        display: true,
                        min: 0,
                        max: 100
                    } 
                },
                plugins: { legend: { display: true } }
            }
        });

        // Volume Chart
        const volumeCtx = document.getElementById('volume-chart').getContext('2d');
        if (this.charts.volumeChart) this.charts.volumeChart.destroy();
        
        this.charts.volumeChart = new Chart(volumeCtx, {
            type: 'bar',
            data: {
                labels: this.currentStock.data.map(d => d.date),
                datasets: [{
                    label: 'Volume',
                    data: this.currentStock.data.map(d => d.volume),
                    backgroundColor: 'rgba(31, 184, 205, 0.3)',
                    borderColor: '#1FB8CD',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { display: true } },
                plugins: { legend: { display: true } }
            }
        });
    }

    updateCurrentSignals() {
        const container = document.getElementById('current-signals-list');
        container.innerHTML = '';
        
        Object.keys(this.currentStock.strategies).forEach(strategy => {
            const strat = this.currentStock.strategies[strategy];
            const hasSignal = strat.signals[strat.signals.length - 1];
            
            const badge = document.createElement('div');
            badge.className = `signal-badge ${hasSignal ? '' : 'signal-badge--neutral'}`;
            badge.textContent = strategy;
            container.appendChild(badge);
        });
    }

    updateStrategyComparison() {
        const tableBody = document.getElementById('strategy-table-body');
        tableBody.innerHTML = '';
        
        Object.keys(this.currentStock.strategies).forEach(strategyName => {
            const strategy = this.currentStock.strategies[strategyName];
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${strategyName}</td>
                <td>${strategy.winRate}%</td>
                <td>${strategy.profitFactor}</td>
                <td>${strategy.avgReturn.toFixed(2)}%</td>
                <td>${strategy.maxDrawdown.toFixed(2)}%</td>
                <td>${strategy.sharpeRatio}</td>
                <td class="${strategy.cagr >= 0 ? 'text-success' : 'text-error'}">${strategy.cagr.toFixed(2)}%</td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    updateAnalytics() {
        this.createAnalyticsCharts();
        this.updateTopPerformers();
        this.updateMarketStats();
        this.createHeatmap();
    }

    createAnalyticsCharts() {
        // Strategy distribution pie chart
        const strategyData = {};
        this.stocks.forEach(stock => {
            Object.keys(stock.strategies).forEach(strategy => {
                if (!strategyData[strategy]) strategyData[strategy] = 0;
                if (stock.strategies[strategy].signals[stock.strategies[strategy].signals.length - 1]) {
                    strategyData[strategy]++;
                }
            });
        });

        const pieCtx = document.getElementById('strategy-pie-chart').getContext('2d');
        if (this.charts.strategyPieChart) this.charts.strategyPieChart.destroy();
        
        this.charts.strategyPieChart = new Chart(pieCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(strategyData),
                datasets: [{
                    data: Object.values(strategyData),
                    backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C', '#ECEBD5', '#5D878F', '#DB4545', '#D2BA4C', '#964325']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Sector bar chart
        const sectorData = {};
        this.stocks.forEach(stock => {
            if (!sectorData[stock.sector]) sectorData[stock.sector] = 0;
            const totalSignals = Object.values(stock.strategies).filter(strat => 
                strat.signals[strat.signals.length - 1]
            ).length;
            sectorData[stock.sector] += totalSignals;
        });

        const barCtx = document.getElementById('sector-bar-chart').getContext('2d');
        if (this.charts.sectorBarChart) this.charts.sectorBarChart.destroy();
        
        this.charts.sectorBarChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(sectorData),
                datasets: [{
                    label: 'Active Signals',
                    data: Object.values(sectorData),
                    backgroundColor: '#1FB8CD'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateTopPerformers() {
        const performers = this.stocks
            .map(stock => ({
                symbol: stock.symbol,
                return: stock.strategies[stock.recommendedStrategy.name].cagr
            }))
            .sort((a, b) => b.return - a.return)
            .slice(0, 10);
        
        const container = document.getElementById('top-performers');
        container.innerHTML = '';
        
        performers.forEach(performer => {
            const item = document.createElement('div');
            item.className = 'performer-item';
            item.innerHTML = `
                <span class="performer-symbol">${performer.symbol}</span>
                <span class="performer-return">${performer.return.toFixed(2)}%</span>
            `;
            container.appendChild(item);
        });
    }

    updateMarketStats() {
        const totalSignals = this.stocks.reduce((sum, stock) => {
            return sum + Object.values(stock.strategies).filter(strat => 
                strat.signals[strat.signals.length - 1]
            ).length;
        }, 0);
        
        // Most active strategy
        const strategyCount = {};
        this.stocks.forEach(stock => {
            Object.keys(stock.strategies).forEach(strategy => {
                if (!strategyCount[strategy]) strategyCount[strategy] = 0;
                if (stock.strategies[strategy].signals[stock.strategies[strategy].signals.length - 1]) {
                    strategyCount[strategy]++;
                }
            });
        });
        
        const mostActiveStrategy = Object.keys(strategyCount).reduce((a, b) => 
            strategyCount[a] > strategyCount[b] ? a : b, '');
        
        const avgReturn = this.stocks.reduce((sum, stock) => 
            sum + stock.dailyChange, 0) / this.stocks.length;
        
        const container = document.getElementById('market-stats');
        container.innerHTML = `
            <div class="stat-item">
                <div class="stat-value">${totalSignals}</div>
                <div class="stat-label">Total Signals</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${mostActiveStrategy.split(' ')[0]}</div>
                <div class="stat-label">Most Active</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${avgReturn.toFixed(2)}%</div>
                <div class="stat-label">Avg Daily Return</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${this.stocks.length}</div>
                <div class="stat-label">Stocks Tracked</div>
            </div>
        `;
    }

    createHeatmap() {
        const sectors = [...new Set(this.stocks.map(s => s.sector))];
        const heatmapData = {};
        
        sectors.forEach(sector => {
            heatmapData[sector] = {};
            this.strategies.forEach(strategy => {
                heatmapData[sector][strategy] = 0;
            });
        });
        
        this.stocks.forEach(stock => {
            this.strategies.forEach(strategy => {
                if (stock.strategies[strategy].signals[stock.strategies[strategy].signals.length - 1]) {
                    heatmapData[stock.sector][strategy]++;
                }
            });
        });
        
        const container = document.getElementById('heatmap-container');
        container.innerHTML = '<div class="heatmap"></div>';
        
        const heatmap = container.querySelector('.heatmap');
        heatmap.style.gridTemplateColumns = `120px repeat(${this.strategies.length}, 1fr)`;
        
        // Header row
        const headerRow = document.createElement('div');
        headerRow.className = 'heatmap-row';
        headerRow.innerHTML = '<div class="heatmap-label"></div>' + 
            this.strategies.map(s => `<div class="heatmap-label">${s.split(' ')[0]}</div>`).join('');
        heatmap.appendChild(headerRow);
        
        // Data rows
        sectors.forEach(sector => {
            const row = document.createElement('div');
            row.className = 'heatmap-row';
            
            let html = `<div class="heatmap-label">${sector}</div>`;
            this.strategies.forEach(strategy => {
                const value = heatmapData[sector][strategy];
                const intensity = Math.min(value / 3, 1); // Normalize to 0-1
                const backgroundColor = `rgba(31, 184, 205, ${intensity})`;
                html += `<div class="heatmap-cell" style="background-color: ${backgroundColor}">${value}</div>`;
            });
            
            row.innerHTML = html;
            heatmap.appendChild(row);
        });
    }

    exportCSV() {
        const headers = ['Symbol', 'Company', 'Sector', 'Price', 'Change%', 'Active Signals', 'Recommended Strategy', 'Win Rate', 'Profit Factor', 'CAGR'];
        const rows = [headers];
        
        this.getFilteredStocks().forEach(stock => {
            const activeSignals = Object.values(stock.strategies).filter(strat => 
                strat.signals[strat.signals.length - 1]
            ).length;
            
            const recommendedPerf = stock.strategies[stock.recommendedStrategy.name];
            
            rows.push([
                stock.symbol,
                stock.company,
                stock.sector,
                stock.currentPrice.toFixed(2),
                stock.dailyChange.toFixed(2),
                activeSignals,
                stock.recommendedStrategy.name,
                recommendedPerf.winRate,
                recommendedPerf.profitFactor,
                recommendedPerf.cagr.toFixed(2)
            ]);
        });
        
        const csvContent = rows.map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'nifty100_signals.csv';
        a.click();
        
        window.URL.revokeObjectURL(url);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TradingDashboard();
});
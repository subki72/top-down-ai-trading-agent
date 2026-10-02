import sys
import os

# Ensure root directory is on sys.path when executed directly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from config.settings import MIN_RR_RATIO, ACCOUNT_EQUITY, MAX_RISK_PER_TRADE_PCT
from config.logger import setup_logger


logger = setup_logger("backtester")

class StrategyBacktester:
    """
    Lightweight simulation backtester for Top-Down trading rules.
    Evaluates historical data to benchmark win rate, profit factor, and drawdown.
    """
    def __init__(
        self,
        initial_equity: float = ACCOUNT_EQUITY,
        risk_per_trade_pct: float = MAX_RISK_PER_TRADE_PCT,
        min_rr_ratio: float = MIN_RR_RATIO
    ):
        self.initial_equity = initial_equity
        self.equity = initial_equity
        self.risk_per_trade_pct = risk_per_trade_pct
        self.min_rr_ratio = min_rr_ratio
        self.trades: List[Dict[str, Any]] = []

    def run_backtest(self, df_candles: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs backtest across historical candles with columns:
        ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'ema_13', 'ema_21']
        """
        logger.info(f"Running strategy backtest over {len(df_candles)} historical candles...")
        
        if len(df_candles) < 30:
            logger.warning("Not enough candles for meaningful backtest.")
            return {"error": "Insufficient candle data"}

        equity_curve = [self.initial_equity]
        wins = 0
        losses = 0
        total_pnl = 0.0

        for i in range(25, len(df_candles) - 5):
            curr = df_candles.iloc[i]
            prev = df_candles.iloc[i - 1]
            
            # 1. Deterministic Trend Condition
            is_bullish = curr.get('ema_13', 0) > curr.get('ema_21', 0) and curr['close'] > curr.get('ema_13', 0)
            is_bearish = curr.get('ema_13', 0) < curr.get('ema_21', 0) and curr['close'] < curr.get('ema_13', 0)

            # 2. Setup Condition (Pullback check)
            rsi = curr.get('rsi', 50.0)
            long_setup = is_bullish and 40 <= rsi <= 60 and curr['low'] <= curr.get('ema_13', 0)
            short_setup = is_bearish and 40 <= rsi <= 60 and curr['high'] >= curr.get('ema_13', 0)

            if not (long_setup or short_setup):
                continue

            entry = curr['close']
            if long_setup:
                sl = min(curr['low'], prev['low']) * 0.998
                risk = entry - sl
                tp = entry + (risk * self.min_rr_ratio)
            else:
                sl = max(curr['high'], prev['high']) * 1.002
                risk = sl - entry
                tp = entry - (risk * self.min_rr_ratio)

            if risk <= 0:
                continue

            # Position Sizing
            dollar_risk = (self.risk_per_trade_pct / 100.0) * self.equity
            units = dollar_risk / risk

            # Simulate outcome across next 5 candles
            outcome = "EXPIRED"
            pnl = 0.0

            for j in range(i + 1, min(i + 6, len(df_candles))):
                future_candle = df_candles.iloc[j]
                if long_setup:
                    if future_candle['high'] >= tp:
                        outcome = "WIN"
                        pnl = dollar_risk * self.min_rr_ratio
                        break
                    elif future_candle['low'] <= sl:
                        outcome = "LOSS"
                        pnl = -dollar_risk
                        break
                else:
                    if future_candle['low'] <= tp:
                        outcome = "WIN"
                        pnl = dollar_risk * self.min_rr_ratio
                        break
                    elif future_candle['high'] >= sl:
                        outcome = "LOSS"
                        pnl = -dollar_risk
                        break

            if outcome == "WIN":
                wins += 1
            elif outcome == "LOSS":
                losses += 1
            
            self.equity += pnl
            total_pnl += pnl
            equity_curve.append(self.equity)

            self.trades.append({
                "index": i,
                "type": "LONG" if long_setup else "SHORT",
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "outcome": outcome,
                "pnl": pnl,
                "equity_after": self.equity
            })

        total_trades = wins + losses
        win_rate = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0.0
        
        # Max Drawdown
        peak = self.initial_equity
        max_dd = 0.0
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100.0
            if dd > max_dd:
                max_dd = dd

        summary = {
            "initial_equity": self.initial_equity,
            "final_equity": round(self.equity, 2),
            "total_return_pct": round(((self.equity - self.initial_equity) / self.initial_equity) * 100, 2),
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": win_rate,
            "max_drawdown_pct": round(max_dd, 2),
            "total_pnl_usd": round(total_pnl, 2),
        }
        logger.info(f"Backtest completed: Win Rate: {win_rate}%, Return: {summary['total_return_pct']}%, Max DD: {max_dd:.2f}%")
        return summary

if __name__ == "__main__":
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n" + "=" * 60)
    print("[*] AI TRADING FIRM: STRATEGY BACKTEST DEMO")
    print("=" * 60)
    
    np.random.seed(42)
    n_candles = 200
    base_price = 300.0
    returns = np.random.normal(0.001, 0.015, n_candles)
    close_prices = base_price * np.cumprod(1 + returns)
    high_prices = close_prices * (1 + np.abs(np.random.normal(0.005, 0.005, n_candles)))
    low_prices = close_prices * (1 - np.abs(np.random.normal(0.005, 0.005, n_candles)))
    open_prices = (close_prices + np.roll(close_prices, 1)) / 2
    open_prices[0] = base_price

    df = pd.DataFrame({
        'timestamp': [1700000000000 + i * 3600000 for i in range(n_candles)],
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': np.random.uniform(500, 5000, n_candles)
    })
    
    # Calculate indicators
    df['ema_13'] = df['close'].ewm(span=13, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['rsi'] = 100 - (100 / (1 + rs))

    backtester = StrategyBacktester(initial_equity=10000.0, risk_per_trade_pct=1.0, min_rr_ratio=1.5)
    summary = backtester.run_backtest(df)

    print(f"\nInitial Equity:     ${summary['initial_equity']:,.2f}")
    print(f"Final Equity:       ${summary['final_equity']:,.2f}")
    print(f"Total Return:       {summary['total_return_pct']}% (${summary['total_pnl_usd']:+,.2f})")
    print(f"Total Trades:       {summary['total_trades']}")
    print(f"Wins / Losses:      {summary['wins']} wins / {summary['losses']} losses")
    print(f"Win Rate:           {summary['win_rate_pct']}%")
    print(f"Max Drawdown:       {summary['max_drawdown_pct']}%\n")
    print("=" * 60 + "\n")


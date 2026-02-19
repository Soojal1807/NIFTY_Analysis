import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

def fetch_nifty_data():
    """Fetches Nifty data."""
    print("Fetching Nifty 50 data...")
    nifty = yf.Ticker("^NSEI")
    return nifty.history(period="max")

def calculate_volatility_analysis(hist):
    """Calculates volatility score."""
    hist['Log_Ret'] = np.log(hist['Close'] / hist['Close'].shift(1))
    
    # 1-year rolling volatility
    rolling_vol = hist['Log_Ret'].rolling(window=252).std() * np.sqrt(252)
    current_vol = rolling_vol.iloc[-1]
    
    if pd.isna(current_vol):
        current_vol = hist['Log_Ret'].std() * np.sqrt(252)
        min_vol = current_vol * 0.5 
        max_vol = current_vol * 1.5
    else:
        min_vol = rolling_vol.min()
        max_vol = rolling_vol.max()
    
    # Normalize score (0-1)
    if max_vol == min_vol:
        score = 0.5
    else:
        normalized = (current_vol - min_vol) / (max_vol - min_vol)
        score = 1.0 - normalized
    
    score = max(0.0, min(1.0, score))
    return current_vol, score

def calculate_5yr_returns(hist):
    """Calculates 5-year returns."""
    # 1260 trading days
    hist['5y_Return'] = hist['Close'].pct_change(periods=1260)
    
    latest_5y = hist['5y_Return'].iloc[-1]
    avg_5y = hist['5y_Return'].mean()
    max_idx = hist['5y_Return'].idxmax()
    min_idx = hist['5y_Return'].idxmin()
    max_5y = hist['5y_Return'].max()
    min_5y = hist['5y_Return'].min()
    
    return {
        "latest": latest_5y,
        "average": avg_5y,
        "max": max_5y,
        "min": min_5y,
        "max_date": max_idx,
        "min_date": min_idx
    }

def identify_market_regimes(hist, threshold=0.20):
    """Identifies Bull/Bear markets."""
    dates = hist.index
    prices = hist['Close'].values
    regimes = []
    
    # 0:Unknown, 1:Bull, -1:Bear
    current_regime = 0 
    last_peak = last_trough = prices[0]
    last_peak_date = last_trough_date = regime_start_date = dates[0]
    
    for i in range(1, len(prices)):
        price = prices[i]
        date = dates[i]
        
        if current_regime == 0:
            if price >= last_trough * (1 + threshold):
                current_regime = 1 
                regime_start_date = last_trough_date
                last_peak = price
                last_peak_date = date
            elif price <= last_peak * (1 - threshold):
                current_regime = -1 
                regime_start_date = last_peak_date
                last_trough = price
                last_trough_date = date
            else:
                if price > last_peak: last_peak, last_peak_date = price, date
                if price < last_trough: last_trough, last_trough_date = price, date
                    
        elif current_regime == 1: 
            if price > last_peak:
                last_peak, last_peak_date = price, date
            elif price <= last_peak * (1 - threshold):
                regimes.append({
                    "type": "Bull",
                    "start": regime_start_date,
                    "end": last_peak_date,
                    "return": (last_peak / hist.loc[regime_start_date]['Close']) - 1
                })
                current_regime = -1
                regime_start_date = last_peak_date
                last_trough, last_trough_date = price, date
                
        elif current_regime == -1: 
            if price < last_trough:
                last_trough, last_trough_date = price, date
            elif price >= last_trough * (1 + threshold):
                regimes.append({
                    "type": "Bear",
                    "start": regime_start_date,
                    "end": last_trough_date,
                    "return": (last_trough / hist.loc[regime_start_date]['Close']) - 1
                })
                current_regime = 1
                regime_start_date = last_trough_date
                last_peak, last_peak_date = price, date

    # Ongoing regime
    regimes.append({
        "type": "Bull (Ongoing)" if current_regime == 1 else "Bear (Ongoing)",
        "start": regime_start_date,
        "end": dates[-1],
        "return": (prices[-1] / hist.loc[regime_start_date]['Close']) - 1
    })
        
    return regimes

def main():
    hist = fetch_nifty_data()
    if hist.empty: return

    volatility, vol_score = calculate_volatility_analysis(hist)
    returns_5y = calculate_5yr_returns(hist)
    regimes = identify_market_regimes(hist)
    
    bull_periods = [r for r in regimes if "Bull" in r['type']]
    bear_periods = [r for r in regimes if "Bear" in r['type']]
    
    output = []
    output.append(f"NIFTY 50 ANALYSIS SUMMARY (As of {datetime.now().strftime('%Y-%m-%d')})")
    output.append("="*60)
    output.append(f"Latest Close: {hist['Close'].iloc[-1]:.2f}")
    output.append(f"Data Range: {hist.index[0].date()} to {hist.index[-1].date()}")
    output.append("-" * 60)
    
    output.append(f"VOLATILITY INDEX (0=Bad/High, 1=Good/Low)")
    output.append(f"Current Annualized Volatility: {volatility:.2%}")
    output.append(f"Volatility Score: {vol_score:.2f} / 1.00")
    if vol_score > 0.7: output.append("(Market is relatively Stable/Calm)")
    elif vol_score < 0.3: output.append("(Market is Highly Volatile/Risky)")
    else: output.append("(Market volatility is Moderate)")
    output.append("-" * 60)
    
    output.append("5-YEAR RETURN ANALYSIS (Rolling)")
    output.append(f"Latest 5-Year Return: {returns_5y['latest']:.2%}")
    output.append(f"Average 5-Year Return: {returns_5y['average']:.2%}")
    max_yr = returns_5y['max_date'].year
    min_yr = returns_5y['min_date'].year
    output.append(f"Best 5-Year Return: {returns_5y['max']:.2%} ({max_yr-5}-{max_yr})")
    output.append(f"Worst 5-Year Return: {returns_5y['min']:.2%} ({min_yr-5}-{min_yr})")
    output.append("-" * 60)
    
    output.append("BULL PERIODS")
    output.append(f"{'Start Date':<15} {'End Date':<15} {'Return':<10}")
    output.append("-" * 45)
    for r in bull_periods:
        output.append(f"{r['start'].strftime('%Y-%m-%d'):<15} {r['end'].strftime('%Y-%m-%d'):<15} {r['return']:<10.2%}")
    
    output.append("-" * 60)
    
    output.append("BEAR PERIODS")
    output.append(f"{'Start Date':<15} {'End Date':<15} {'Return':<10}")
    output.append("-" * 45)
    for r in bear_periods:
        output.append(f"{r['start'].strftime('%Y-%m-%d'):<15} {r['end'].strftime('%Y-%m-%d'):<15} {r['return']:<10.2%}")

    output.append("="*60)
    text = "\n".join(output)
    
    with open("Output_Summary.txt", "w") as f:
        f.write(text)
    print("\nAnalysis complete. Results written to Output_Summary.txt")
    print("-" * 30)
    print(text)

if __name__ == "__main__":
    main()

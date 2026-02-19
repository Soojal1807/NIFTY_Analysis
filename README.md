# Nifty 50 Historical Analysis

A Python analysis tool for Nifty 50 historical data, designed to identify market regimes, calculate returns, and assess volatility.

## Features

- **Historical Data**: Fetches max history from Yahoo Finance (`^NSEI`).
- **Market Regimes**: Automatically identifies Bull and Bear phases.
- **Return Analysis**: Rolling 5-year return performance (Average, Best, Worst).
- **Volatility Index**: Custom 0-1 score indicating market stability.

## Volatility Algorithm

The volatility index is calculated using a **Normalized Rolling Volatility** approach:

1.  **Log Returns**: Calculate daily logarithmic returns of the closing price.
2.  **Rolling Volatility**: Compute the annualized standard deviation (using $\sqrt{252}$) over a rolling 1-year (252 trading days) window.
3.  **Normalization**:
    $$ \text{Score} = 1 - \frac{\text{Current Vol} - \text{Min Historical Vol}}{\text{Max Historical Vol} - \text{Min Historical Vol}} $$
    - **Score -> 1.0**: Low relative volatility (Stable/Good).
    - **Score -> 0.0**: High relative volatility (Risky/Bad).

## Usage

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the script:
    ```bash
    python nifty_analysis.py
    ```
3.  Check `Output_Summary.txt` for the report.

## License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

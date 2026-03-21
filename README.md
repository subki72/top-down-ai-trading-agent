# Top-Down AI Trading Firm (LangGraph Architecture)

## Overview
This project implements an automated, Multi-Agent Artificial Intelligence trading system utilizing a strict Top-Down Analysis methodology. It leverages a state-graph architecture (LangGraph) and the Llama 3 models (via Groq API) to process market data, synthesize macrotechnicals trends, and generate highly calibrated trading decisions.

## System Architecture
The architecture is designed to mitigate Large Language Model (LLM) hallucination by compartmentalizing analysis and enforcing strict programmatic guardrails. Rather than a linear script, the system operates as a finite state machine where a central `TradingState` is passed between specialized departments.

The pipeline consists of specific AI agents and deterministic modules:

1. **Data Fetcher (Tools)**: Acquires multi-timeframe OHLCV data from Kraken and calculates technical indicators (RSI, MACD).
2. **H1 Strategist Agent**: Analyzes the overarching macroeconomic direction and identifies market structures.
3. **M15 Analyst Agent**: Scans for localized market structures and chart patterns (SMC, Flags, Triangles) that align with the macro trend.
4. **M5 Sniper Agent**: Acts as the execution layer, identifying immediate momentum shifts via short-term candlestick formations to define exact Entry, Stop Loss, and Take Profit levels.
5. **Risk Guardrail (Deterministic)**: A pure mathematical module that intercepts the Sniper's signal. It calculates the absolute Risk-to-Reward (RR) ratio. If the ratio falls below the acceptable threshold (e.g., 1:1.5), the system automatically rejects the trade.
6. **CIO Manager Agent**: Synthesizes the reports from all underlying agents to provide a final professional reasoning for the system's decision.
7. **Telegram Dispatcher**: Asynchronously delivers the executive summary to the user's device.

## Prerequisites
- Python 3.9+
- CCXT (Cryptocurrency Exchange Trading Library)
- Pandas & TA (Technical Analysis)
- LangChain, LangChain-Groq, & LangGraph
- Python-dotenv

## Installation and Setup
1. Clone this repository to your local machine.
2. Create and activate a Python virtual environment.
3. Install the required dependencies:
   `pip install -r requirements.txt`
4. Create a `.env` file in the root directory. You must supply the following environment variables:
   - `GROQ_API_KEY=your_groq_api_key_here`
   - `TELEGRAM_TOKEN=your_telegram_bot_token_here`
   - `TELEGRAM_CHAT_ID=your_telegram_chat_id_here`

## Usage
To execute a single analysis cycle, run the main control panel:
```bash
python main.py
```
The system will dynamically route the decision-making process. If a macro trend is invalid, it will short-circuit the execution to save compute resources and immediately dispatch a standby notification.

## Disclaimer
This software is provided for educational, research, and analytical purposes only. It does not constitute financial advice. Do not deploy this system with real capital without conducting extensive backtesting. The creator assumes no liability for any financial losses incurred.

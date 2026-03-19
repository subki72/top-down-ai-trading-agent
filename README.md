# Top-Down AI Trading Agent

## Overview
This project implements an automated, Multi-Agent Artificial Intelligence trading system utilizing a strict Top-Down Analysis methodology. It leverages the Llama 3.1 model (via Groq API) to process market data across multiple timeframes, synthesizing macroeconomic trends, market structures, and execution triggers into a single, highly calibrated trading decision.

## System Architecture
The architecture is designed to mitigate Large Language Model (LLM) hallucination by compartmentalizing analysis and enforcing strict programmatic guardrails. 

The pipeline consists of four distinct AI agents and one mathematical validation module:

1. Trend Agent (1H Timeframe): Analyzes the overarching macroeconomic direction and identifies primary support and resistance zones.
2. Pattern Agent (15m Timeframe): Scans for broader market structures and chart patterns (e.g., Double Bottom, Head and Shoulders) to determine localized market context.
3. Trigger Agent (5m Timeframe): Acts as the execution layer, identifying immediate momentum shifts via short-term candlestick formations.
4. Manager Agent : Synthesizes the reports from the three underlying agents. It enforces a strict alignment protocol; a final execution directive (BUY/SELL) is only issued if the macro, micro, and trigger analyses are completely aligned.
5. Risk Guardrails: A deterministic Python module that intercepts the Manager Agent's decision and validates it against hardcoded technical indicators (RSI, MACD, Volume). If the AI decision contradicts mathematical reality, the trade is rejected.

## Prerequisites
- Python 3.9 or higher
- CCXT (Cryptocurrency Exchange Trading Library)
- Pandas
- TA (Technical Analysis Library)
- LangChain & LangChain-OpenAI
- Python-dotenv

## Installation and Setup
1. Clone this repository to your local machine.
2. Create and activate a Python virtual environment.
3. Install the required dependencies:
   `pip install -r requirements.txt`
4. Create a `.env` file in the root directory. You must supply the following environment variables to authenticate the LLM and the notification system:
   GROQ_API_KEY=your_groq_api_key_here
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   TELEGRAM_CHAT_ID=your_telegram_chat_id_here

## Usage
To execute a single analysis cycle, run the main control panel:
`python main.py`

The system will fetch real-time OHLCV data from the exchange, process the information through the Multi-Agent pipeline, validate the output, and dispatch an executive summary to the configured Telegram endpoint.

## Disclaimer
This software is provided for educational, research, and analytical purposes only. It does not constitute financial advice. Do not deploy this system with real capital without conducting extensive backtesting and implementing robust risk management protocols. The creator assumes no liability for any financial losses incurred.
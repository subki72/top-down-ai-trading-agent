# main.py
import requests
from config.settings import SYMBOL, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, TF_MACRO, TF_MICRO, TF_TRIGGER
from tools.market_data import get_multi_timeframe_data
from tools.indicators import calculate_indicators
from guardrails.risk_manager import check_trading_permission

# Import 3 Specialists + 1 CEO
from agents.trend_agent import analyze_macro_trend
from agents.pattern_agent import analyze_chart_pattern
from agents.trigger_agent import analyze_trigger_entry
from agents.manager_agent import determine_final_decision

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        if response.status_code == 200:
            print("[TELEGRAM] Message successfully delivered to user.")
        else:
            print(f"[TELEGRAM ERROR] Server rejected the message. Reason: {response.text}")
    except Exception as e:
        print(f"[NETWORK CRASH] Failed to connect: {e}")

def run_trading_cycle():
    print("=======================================")
    print(" INITIATING TOP-DOWN AI TRADING CYCLE...")
    print("=======================================\n")
    
    # 1. Fetch data for all 3 timeframes
    market_data = get_multi_timeframe_data(symbol=SYMBOL, limit=100)
    if market_data is None: 
        return

    # 2. Calculate Indicators (Using 15m data to reduce noise)
    indicators = calculate_indicators(market_data['micro'])
    if indicators is None: 
        return

    # 3. TOP-DOWN ANALYSIS (Board Meeting)
    print("\n--- Initiating Specialist Analysis ---")
    trend_report = analyze_macro_trend(market_data['macro'])
    pattern_report = analyze_chart_pattern(market_data['micro'])
    trigger_report = analyze_trigger_entry(market_data['trigger'])
    
    # 4. CEO Decision Making
    ceo_decision = determine_final_decision(trend_report, pattern_report, trigger_report)
    print("--- Analysis Complete ---\n")

    # 5. Guardrail Validation (Strict Risk Management)
    final_action = ceo_decision.get('decision', 'WAIT')
    guardrail_status = check_trading_permission(final_action, indicators)

    # 6. Format Executive Report for Telegram
    pattern_text = pattern_report.get('chart_pattern', '-')
    trigger_text = trigger_report.get('candlestick_trigger', '-')
    guardrail_msg = guardrail_status.get('message', '-')

    telegram_message = f"""
=== TOP-DOWN TRADING REPORT ===
ASSET : {SYMBOL}
RSI ({TF_MICRO}) : {indicators['rsi']:.2f}
MACD ({TF_MICRO}) : {indicators['macd_hist']:.2f}

[ DETAILED ANALYSIS ]
> Macro (1H)  : Trend {trend_report.get('macro_trend', '-')}
> Micro (15m) : Pattern {pattern_text}
> Sniper (5m) : Trigger {trigger_text}

[ FINAL DECISION ]
> Action    : {final_action}
> Reasoning : {ceo_decision.get('reasoning', '-')}

[ SYSTEM GUARDRAILS ]
> Status : {guardrail_msg}
===============================
"""
    print("[TELEGRAM] Dispatching notification...")
    send_telegram_message(telegram_message)
    print("Cycle complete.")

if __name__ == "__main__":
    run_trading_cycle()
# guardrails/risk_manager.py
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

def check_trading_permission(ai_decision, indicator_data):
    """
    Acts as the deterministic guardrail.
    Receives the AI's decision and validates it strictly against technical indicators.
    """
    print(f"[GUARDRAILS] Validating execution permission for AI decision: {ai_decision}...")
    
    rsi = indicator_data['rsi']
    macd_hist = indicator_data['macd_hist']
    current_vol = indicator_data['current_volume']
    avg_vol = indicator_data['avg_volume']

    if ai_decision == "BUY":
        if rsi < RSI_OVERSOLD and macd_hist > 0 and current_vol > avg_vol:
            return {"status": "APPROVED", "message": "BUY conditions met (RSI Oversold, MACD Positive, High Volume)."}
        else:
            return {"status": "REJECTED", "message": "Guardrail rejection: Indicators do not support BUY execution."}

    elif ai_decision == "SELL":
        if rsi > RSI_OVERBOUGHT and macd_hist < 0 and current_vol > avg_vol:
            return {"status": "APPROVED", "message": "SELL conditions met (RSI Overbought, MACD Negative, High Volume)."}
        else:
            return {"status": "REJECTED", "message": "Guardrail rejection: Indicators do not support SELL execution."}

    else:
        return {"status": "STANDBY", "message": "AI decision is WAIT. No execution permitted."}
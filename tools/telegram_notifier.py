import requests
from state import TradingState
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, API_TIMEOUT_SECONDS
from tools.resilience import retry_with_backoff
from config.logger import setup_logger

logger = setup_logger("telegram_notifier")

def send_telegram_report(state: TradingState):
    """Dispatches executive trading report to Telegram bot with resilience and retry."""
    logger.info("Dispatching executive report to Telegram...")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured. Skipping notification.")
        return {"execution_logs": ["Telegram notification skipped (credentials not configured)"]}

    asset = state.get('asset_pair', 'N/A')
    action = state.get('final_action', 'IDLE')
    rr_ratio = state.get('rr_ratio', 0.0)
    trend = state.get('macro_trend_h1', 'N/A')
    
    m15_status = state.get('micro_signal_m15') or "SKIPPED (No Pattern)"
    m5_trigger = state.get('trigger_m5') or "SKIPPED (No Trigger)"
    
    entry = state.get('entry_price')
    sl = state.get('stop_loss')
    tp = state.get('take_profit')
    pos_usd = state.get('position_size_usd', 0.0)
    pos_tokens = state.get('position_size_tokens', 0.0)
    risk_usd = state.get('risk_usd', 0.0)
    reward_usd = state.get('reward_usd', 0.0)
    reason = state.get('risk_rejection_reason', '')

    # Format status emoji
    status_icon = "🟢" if action == "EXECUTE_TRADE" else "🔴" if "REJECT" in action else "🟡"

    report_lines = [
        f"<b>{status_icon} AI TRADING REPORT: {asset}</b>",
        "------------------------------------",
        f"<b>Decision:</b> <code>{action}</code>",
        f"<b>H1 Macro Trend:</b> {trend}",
        f"<b>M15 Pattern:</b> {m15_status}",
        f"<b>M5 Trigger:</b> {m5_trigger}",
        "------------------------------------",
        "<b>Capital & Risk Allocation:</b>",
        f"• Risk/Reward Ratio: 1:{rr_ratio}",
    ]

    if entry is not None and sl is not None and tp is not None:
        report_lines.extend([
            f"• Entry: {entry} | SL: {sl} | TP: {tp}",
            f"• Position Size: ${pos_usd} ({pos_tokens} tokens)",
            f"• Risk: ${risk_usd} | Target Reward: ${reward_usd}"
        ])
    
    if reason:
        report_lines.append(f"• Note: <i>{reason}</i>")

    report_lines.append("------------------------------------")
    report = "\n".join(report_lines)

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": report,
        "parse_mode": "HTML" 
    }

    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def post_to_telegram():
        resp = requests.post(api_url, json=payload, timeout=API_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp

    try:
        post_to_telegram()
        logger.info("Telegram report successfully dispatched")
        return {"execution_logs": ["Telegram report successfully dispatched"]}
    except Exception as e:
        logger.error(f"Telegram delivery failed: {str(e)}", exc_info=True)
        return {"execution_logs": [f"Telegram notification error: {str(e)}"]}
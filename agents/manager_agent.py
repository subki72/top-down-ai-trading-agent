from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import TradingState
from config.settings import MODEL_MANAGER, API_TIMEOUT_SECONDS
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("manager_agent")

def synthesize_final_report(state: TradingState):
    logger.info("Compiling CIO executive synthesis...")
    
    template = """
    As the Chief Investment Officer (CIO), provide a high-level executive summary for the following analysis:
    - Asset: {asset}
    - Macro Trend: {trend}
    - Setup: {setup}
    - Trigger: {trigger}
    - RR Ratio: 1:{rr}
    - Recommended Position: ${position_usd} ({position_tokens} units)
    - Dollar Risk: ${risk_usd} | Target Reward: ${reward_usd}
    - Final Action: {action}
    - Rejection Reason (if any): {rejection_reason}

    Requirement: Provide a professional reasoning (max 2 sentences). 
    Focus on confluence, risk mitigation, and disciplined capital allocation. If rejected, clearly state why.
    """
    
    prompt = PromptTemplate.from_template(template)

    @retry_with_backoff(max_attempts=3, initial_delay=1.0)
    def call_llm():
        llm = ChatGroq(
            temperature=0,
            model_name=MODEL_MANAGER,
            request_timeout=API_TIMEOUT_SECONDS
        )
        return (prompt | llm).invoke({
            "asset": state.get('asset_pair', 'N/A'),
            "trend": state.get('macro_trend_h1', 'N/A'),
            "setup": state.get('micro_signal_m15', 'N/A'),
            "trigger": state.get('trigger_m5', 'N/A'),
            "rr": state.get('rr_ratio', 0.0),
            "position_usd": state.get('position_size_usd', 0.0),
            "position_tokens": state.get('position_size_tokens', 0.0),
            "risk_usd": state.get('risk_usd', 0.0),
            "reward_usd": state.get('reward_usd', 0.0),
            "action": state.get('final_action', 'IDLE'),
            "rejection_reason": state.get('risk_rejection_reason', 'None')
        }).content

    try:
        response = call_llm().strip()
        logger.info(f"CIO Synthesis finalized: {response}")
        return {"execution_logs": [f"CIO Executive Synthesis: {response}"]}
    except Exception as e:
        logger.error(f"CIO synthesis failed: {str(e)}", exc_info=True)
        fallback = (
            f"CIO Synthesis unavailable due to API error: {str(e)}. "
            f"System strictly governed by deterministic guardrail: {state.get('final_action', 'IDLE')}."
        )
        return {"execution_logs": [fallback]}
# agents/manager_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import GROQ_API_KEY

def determine_final_decision(trend_report, pattern_report, trigger_report):
    print("[CEO AGENT] Manager is synthesizing the 3 Top-Down Analysis reports...")
    
    llm = ChatOpenAI(
        api_key=GROQ_API_KEY, 
        base_url="https://api.groq.com/openai/v1", 
        model="llama-3.1-8b-instant", 
        temperature=0.0
    )
    parser = JsonOutputParser()
    
    system_prompt = """
    You are the Chief Investment Officer (Trading CEO).
    Your task is to make the final trading decision (BUY/SELL/WAIT) based on a Top-Down Analysis strategy using three subordinate reports.
    
    ABSOLUTE ALIGNMENT RULES:
    1. Strict BUY Condition: The Macro Trend must be 'Uptrend' AND the Micro Pattern must show upward potential (Bullish/Breakout/Support) AND there must be a Bullish Trigger Candlestick in the lowest timeframe.
    2. Strict SELL Condition: The Macro Trend must be 'Downtrend' AND the Micro Pattern must show downward potential (Bearish/Breakdown/Resistance) AND there must be a Bearish Trigger Candlestick in the lowest timeframe.
    3. If the three reports are NOT ALIGNED (e.g., Uptrend but Bearish Trigger), you MUST choose WAIT. Never force an entry.
    
    You MUST strictly reply with the following pure JSON format:
    {{
        "decision": "BUY/SELL/WAIT",
        "reasoning": "Briefly explain the alignment (or lack thereof) across the three timeframes."
    }}
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Trend Report (1H):\n{trend}\n\nPattern Report (15m):\n{pattern}\n\nTrigger Report (5m):\n{trigger}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    try:
        return (prompt | llm | parser).invoke({
            "trend": str(trend_report),
            "pattern": str(pattern_report),
            "trigger": str(trigger_report)
        })
    except Exception as e:
        return {"decision": "WAIT", "reasoning": f"CEO Error: {e}"}
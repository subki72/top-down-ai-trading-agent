# agents/trigger_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import GROQ_API_KEY

def analyze_trigger_entry(df_5m):
    print("[AGENT 3] Sniper is monitoring for trigger entries on the 5m timeframe...")
    
    llm = ChatOpenAI(
        api_key=GROQ_API_KEY, 
        base_url="https://api.groq.com/openai/v1", 
        model="llama-3.1-8b-instant", 
        temperature=0.0
    )
    parser = JsonOutputParser()
    
    system_prompt = """
    You are an Execution Trigger Specialist (Sniper Agent).
    Your ONLY task is to find very short-term candlestick patterns (Trigger Entries) from this 5-Minute (5m) data.
    Focus on single or double candlestick patterns indicating instant momentum shifts.
    Examples: Dragonfly Doji, Gravestone Doji, Marubozu, Pin Bar, Hammer, Shooting Star, Three White Soldiers.
    
    STRICT RULES:
    - DO NOT analyze macro trends or large chart patterns.
    - You are the final executor. Specify the exact candlestick pattern appearing in the last 1-3 candles.
    
    You MUST strictly reply with the following pure JSON format:
    {{
        "candlestick_trigger": "Specific pattern name (or 'No trigger')",
        "signal": "Bullish / Bearish / Neutral",
        "brief_analysis": "Momentum reasoning based on the body and shadow of the latest candles"
    }}
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze these last 5 5m candles:\n{data}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    # The sniper only needs the last 5 candles. Historical macro data is irrelevant here.
    data_text = df_5m.tail(5).to_string()
    
    try:
        return (prompt | llm | parser).invoke({"data": data_text})
    except Exception as e:
        return {
            "candlestick_trigger": "Error", 
            "signal": "Neutral", 
            "brief_analysis": f"Sniper vision failed: {e}"
        }
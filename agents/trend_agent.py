# agents/trend_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import GROQ_API_KEY

def analyze_macro_trend(df_1h):
    print("[AGENT 1] Macro Specialist is analyzing the 1H timeframe trend...")
    
    llm = ChatOpenAI(
        api_key=GROQ_API_KEY, 
        base_url="https://api.groq.com/openai/v1", 
        model="llama-3.1-8b-instant", 
        temperature=0.0
    )
    parser = JsonOutputParser()
    
    system_prompt = """
    You are a Macro Trend Specialist (Trend Agent).
    Your ONLY task is to analyze the primary trend direction from this 1-Hour (1H) candlestick data.
    Do not look for trigger entries. Focus on:
    1. Primary trend direction (Uptrend / Downtrend / Sideways).
    2. Nearest Support level (lowest price halting the decline).
    3. Nearest Resistance level (highest price halting the advance).
    
    You MUST strictly reply with the following pure JSON format:
    {{
        "macro_trend": "Uptrend/Downtrend/Sideways",
        "support": "support price",
        "resistance": "resistance price",
        "brief_analysis": "Brief reasoning, max 2 sentences"
    }}
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze these last 30 1H candles:\n{data}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    # Extract 30 candles to observe clear peaks and troughs
    data_text = df_1h.tail(30).to_string()
    
    try:
        return (prompt | llm | parser).invoke({"data": data_text})
    except Exception as e:
        return {
            "macro_trend": "Sideways", 
            "support": "-", 
            "resistance": "-", 
            "brief_analysis": f"Failed to read trend: {e}"
        }
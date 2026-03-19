# agents/pattern_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config.settings import GROQ_API_KEY

def analyze_chart_pattern(df_15m):
    print("[AGENT 2] Structure Specialist is searching for Chart Patterns on the 15m timeframe...")
    
    llm = ChatOpenAI(
        api_key=GROQ_API_KEY, 
        base_url="https://api.groq.com/openai/v1", 
        model="llama-3.1-8b-instant", 
        temperature=0.0
    )
    parser = JsonOutputParser()
    
    system_prompt = """
    You are a Price Structure Specialist (Pattern Agent).
    Your ONLY task is to identify macro Chart Patterns from this 15-Minute (15m) candlestick data.
    Focus on structural formations such as: Double Top, Double Bottom, Head and Shoulders, Wedge, or Triangle.
    
    STRICT RULES:
    - DO NOT analyze single candlesticks (like Doji, Hammer, Engulfing). Ignore them completely.
    - Focus solely on price swings (Swing Highs and Swing Lows).
    
    You MUST strictly reply with the following pure JSON format:
    {{
        "chart_pattern": "Name of the pattern (or 'No clear pattern')",
        "structural_phase": "Formation / Breakout / Retest / Consolidation",
        "brief_analysis": "Logical reasoning based on High and Low movements"
    }}
    {format_instructions}
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Analyze these last 50 15m candles:\n{data}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    # Extract 50 candles to ensure structural formations are clearly visible
    data_text = df_15m.tail(50).to_string()
    
    try:
        return (prompt | llm | parser).invoke({"data": data_text})
    except Exception as e:
        return {
            "chart_pattern": "Error", 
            "structural_phase": "-", 
            "brief_analysis": f"Failed to read structure: {e}"
        }
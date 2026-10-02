import json
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from config.settings import MODEL_NEWS, API_TIMEOUT_SECONDS
from config.logger import setup_logger
from tools.resilience import retry_with_backoff

logger = setup_logger("news_classifier")

def safe_parse_json_array(text: str) -> list:
    """
    Safely extracts and parses JSON array from LLM output.
    """
    if not text:
        return []

    cleaned = text.replace("```json", "").replace("```", "").strip()
    
    start_idx = cleaned.find("[")
    end_idx = cleaned.rfind("]") + 1
    if start_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(cleaned[start_idx:end_idx])
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode failed on extracted array: {e}")
            return []
    return []

def classify_news_batch(articles: list) -> list:
    """
    Use Groq LLM with retries to classify a batch of crypto news articles into categories.
    
    Categories:
    - TECHNICAL: Chart patterns, price analysis, support/resistance, indicators
    - FUNDAMENTAL_MACRO: Geopolitics, regulation, monetary policy, economics
    - FUNDAMENTAL_ONCHAIN: Blockchain metrics, whale activity, TVL, DeFi, protocol updates
    
    Also determines sentiment: BULLISH, BEARISH, NEUTRAL
    """
    if not articles:
        logger.info("No articles to classify")
        return []
    
    logger.info(f"Classifying {len(articles)} articles using {MODEL_NEWS}...")
    
    batch_size = 10
    classified_articles = []
    
    template = """You are a crypto news classifier. Classify each article below into EXACTLY one category and sentiment.

Categories:
- TECHNICAL: Price analysis, chart patterns, support/resistance levels, technical indicators, trading signals
- FUNDAMENTAL_MACRO: Geopolitics, government regulation, monetary policy, inflation,
  central bank decisions, economic data, institutional adoption, legal/compliance
- FUNDAMENTAL_ONCHAIN: Blockchain metrics, whale movements, TVL changes, DeFi protocol updates,
  network upgrades, token burns, staking data, smart contract activity

Sentiments: BULLISH, BEARISH, NEUTRAL

Articles:
{articles}

RESPOND IN VALID JSON ARRAY FORMAT ONLY. No explanations. Each item must have:
- "index": article index number
- "category": one of TECHNICAL, FUNDAMENTAL_MACRO, FUNDAMENTAL_ONCHAIN
- "sentiment": one of BULLISH, BEARISH, NEUTRAL
- "summary": one sentence summary in English (max 20 words)

Example:
[{{"index": 0, "category": "FUNDAMENTAL_MACRO", "sentiment": "BEARISH", "summary": "SEC announces new crypto regulations"}}]
"""
    prompt = PromptTemplate.from_template(template)

    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        articles_text = ""
        for idx, article in enumerate(batch):
            tags = ", ".join(article.get("categories", []))
            body_preview = article.get("body", "")[:150]
            articles_text += (
                f"\n[{idx}] Title: {article['title']}\n"
                f"    Source: {article['source']}\n"
                f"    Tags: {tags}\n"
                f"    Preview: {body_preview}\n"
            )

        @retry_with_backoff(max_attempts=3, initial_delay=1.0)
        def call_llm():
            llm = ChatGroq(
                temperature=0,
                model_name=MODEL_NEWS,
                request_timeout=API_TIMEOUT_SECONDS
            )
            return (prompt | llm).invoke({"articles": articles_text}).content

        try:
            raw_response = call_llm()
            classifications = safe_parse_json_array(raw_response)
            
            # Map by index
            class_map = {item.get("index"): item for item in classifications if isinstance(item, dict) and "index" in item}

            for idx, original in enumerate(batch):
                c_item = class_map.get(idx, {})
                category_val = c_item.get("category", "FUNDAMENTAL_MACRO")
                if category_val not in ["TECHNICAL", "FUNDAMENTAL_MACRO", "FUNDAMENTAL_ONCHAIN"]:
                    category_val = "FUNDAMENTAL_MACRO"

                sentiment_val = c_item.get("sentiment", "NEUTRAL")
                if sentiment_val not in ["BULLISH", "BEARISH", "NEUTRAL"]:
                    sentiment_val = "NEUTRAL"

                classified_articles.append({
                    "title": original["title"],
                    "source": original["source"],
                    "url": original["url"],
                    "published_at": original["published_at"],
                    "summary": c_item.get("summary", original["title"]),
                    "category": category_val,
                    "sentiment": sentiment_val,
                    "relevance_score": 0.8 if idx in class_map else 0.5
                })

        except Exception as e:
            logger.error(f"Classification batch {i // batch_size} failed: {str(e)}", exc_info=True)
            # Fallback for this batch
            for original in batch:
                classified_articles.append({
                    "title": original["title"],
                    "source": original["source"],
                    "url": original["url"],
                    "published_at": original["published_at"],
                    "summary": original["title"],
                    "category": "FUNDAMENTAL_MACRO",
                    "sentiment": "NEUTRAL",
                    "relevance_score": 0.5
                })

    logger.info(f"Successfully classified {len(classified_articles)} articles")
    return classified_articles

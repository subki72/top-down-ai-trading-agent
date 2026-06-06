import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

def classify_news_batch(articles: list) -> list:
    """
    Use Groq LLM to classify a batch of crypto news articles into categories.
    
    Categories:
    - TECHNICAL: Chart patterns, price analysis, support/resistance, indicators
    - FUNDAMENTAL_MACRO: Geopolitics, regulation, monetary policy, economics
    - FUNDAMENTAL_ONCHAIN: Blockchain metrics, whale activity, TVL, DeFi, protocol updates
    
    Also determines sentiment: BULLISH, BEARISH, NEUTRAL
    """
    if not articles:
        print("[NEWS_CLASSIFIER] No articles to classify")
        return []
    
    print(f"[NEWS_CLASSIFIER] Classifying {len(articles)} articles...")
    llm = ChatGroq(temperature=0, model_name="llama-3.1-8b-instant")
    
    # Batch articles into groups of 10 for efficiency
    batch_size = 10
    classified_articles = []
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]
        articles_text = ""
        for idx, article in enumerate(batch):
            tags = ", ".join(article.get("categories", []))
            body_preview = article.get("body", "")[:150]
            articles_text += f"\n[{idx}] Title: {article['title']}\n    Source: {article['source']}\n    Tags: {tags}\n    Preview: {body_preview}\n"
        
        template = """You are a crypto news classifier. Classify each article below into EXACTLY one category and sentiment.

Categories:
- TECHNICAL: Price analysis, chart patterns, support/resistance levels, technical indicators, trading signals
- FUNDAMENTAL_MACRO: Geopolitics, government regulation, monetary policy, inflation, central bank decisions, economic data, institutional adoption, legal/compliance
- FUNDAMENTAL_ONCHAIN: Blockchain metrics, whale movements, TVL changes, DeFi protocol updates, network upgrades, token burns, staking data, smart contract activity

Sentiments: BULLISH, BEARISH, NEUTRAL

Articles:
{articles}

RESPOND IN VALID JSON ARRAY FORMAT ONLY. No explanations. Each item must have:
- "index": article index number
- "category": one of TECHNICAL, FUNDAMENTAL_MACRO, FUNDAMENTAL_ONCHAIN
- "sentiment": one of BULLISH, BEARISH, NEUTRAL
- "summary": one sentence summary in English (max 20 words)

Example: [{{"index": 0, "category": "FUNDAMENTAL_MACRO", "sentiment": "BEARISH", "summary": "SEC announces new crypto regulations"}}]
"""
        
        prompt = PromptTemplate.from_template(template)
        
        try:
            response = (prompt | llm).invoke({
                "articles": articles_text
            }).content.strip()
            
            # Clean response - extract JSON array
            response = response.replace("```json", "").replace("```", "").strip()
            
            # Find the JSON array in the response
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                classifications = json.loads(json_str)
            else:
                print(f"[NEWS_CLASSIFIER] Warning: Could not parse JSON from batch {i//batch_size}")
                classifications = []
            
            # Merge classifications with original article data
            for classification in classifications:
                idx = classification.get("index", -1)
                if 0 <= idx < len(batch):
                    original = batch[idx]
                    category_val = classification.get("category", "FUNDAMENTAL_MACRO")
                    if category_val not in ["TECHNICAL", "FUNDAMENTAL_MACRO", "FUNDAMENTAL_ONCHAIN"]:
                        category_val = "FUNDAMENTAL_MACRO"
                        
                    sentiment_val = classification.get("sentiment", "NEUTRAL")
                    if sentiment_val not in ["BULLISH", "BEARISH", "NEUTRAL"]:
                        sentiment_val = "NEUTRAL"
                        
                    classified_articles.append({
                        "title": original["title"],
                        "source": original["source"],
                        "url": original["url"],
                        "published_at": original["published_at"],
                        "summary": classification.get("summary", original["title"]),
                        "category": category_val,
                        "sentiment": sentiment_val,
                        "relevance_score": 0.8
                    })
                    
        except Exception as e:
            print(f"[ERROR] Classification batch {i//batch_size} failed: {str(e)}")
            # Fallback: add unclassified articles
            for article in batch:
                classified_articles.append({
                    "title": article["title"],
                    "source": article["source"],
                    "url": article["url"],
                    "published_at": article["published_at"],
                    "summary": article["title"],
                    "category": "FUNDAMENTAL_MACRO",
                    "sentiment": "NEUTRAL",
                    "relevance_score": 0.5
                })
    
    print(f"[NEWS_CLASSIFIER] Successfully classified {len(classified_articles)} articles")
    return classified_articles

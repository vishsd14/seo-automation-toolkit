import os
from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_serp_data(keyword):
    params = {
        "q": keyword,
        "hl": "en",
        "gl": "us",
        "api_key": SERPAPI_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    competitors, paa_questions, related_searches = [], [], []

    for result in results.get("organic_results", []):
        competitors.append(result.get("title", "") + " - " + result.get("link", ""))
    for question in results.get("related_questions", []):
        paa_questions.append(question.get("question", ""))
    for related in results.get("related_searches", []):
        related_searches.append(related.get("query", ""))

    return [keyword, ", ".join(competitors), ", ".join(paa_questions), ", ".join(related_searches)]

# This script scrapes the web for information about the nutrients in a 
# given food item using Google CSE and OpenRouter LLM.
# It then stores the results in a ChromaDB database for future reference.
import requests
from bs4 import BeautifulSoup
from chroma_ns import store_in_chroma
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CX_ID = os.getenv("CX_ID")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# 1. Search Google CSE
# Google CSE
def search_google_cse(query, api_key, cx, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query, "num": num_results}
    res = requests.get(url, params=params).json()
    return [item['link'] for item in res.get('items', [])]

# Scraping content
def scrape_text_from_url(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return ' '.join(p.get_text() for p in soup.find_all('p'))
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return ""

# Ask OpenRouter (LLM)
def ask_openrouter_llm(content, food_item, model="mistralai/mistral-small-3.1-24b-instruct:free"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"What are the nutrients present in {food_item}? Based on the following content, list them clearly with optional quantities if mentioned:\n\n{content}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a health and nutrition expert."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

# Main pipeline
def run_pipeline(food_item):
    print(f"🔍 Searching for: nutrients in {food_item}")
    query = f"nutrients in {food_item}"
    urls = search_google_cse(query, GOOGLE_API_KEY, CX_ID)

    combined_text = ""
    for url in urls:
        print(f"🌐 Scraping: {url}")
        combined_text += scrape_text_from_url(url) + "\n\n"

    print("🤖 Asking OpenRouter LLM...")
    response = ask_openrouter_llm(combined_text[:12000], food_item)

    print(f"\n✅ Nutrients in {food_item.upper()}:\n")
    print(response)

    # Store in ChromaDB
    store_in_chroma(food_item, response, urls)

if __name__ == "__main__":
    food = input("🍽️ Enter the food you want to analyze: ")
    run_pipeline(food)

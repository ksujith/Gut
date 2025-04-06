from scrapper_llm import run_pipeline
from chroma_ns import store_in_chroma
import requests
from dotenv import load_dotenv
import os

load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")  # or use dotenv to load from .env

def fetch_usda_nutrients(food_name):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food_name,
        "pageSize": 1,
        "api_key": USDA_API_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("❌ Error reaching USDA API:", e)
        return None

    data = res.json()
    if not data.get("foods"):
        return None

    food = data["foods"][0]
    return food.get("foodNutrients", [])

def get_nutrients_for_food(food_name):
    print(f"\n🔍 Looking up nutrients for: {food_name.upper()}")

    nutrients = fetch_usda_nutrients(food_name)

    if nutrients:
        print("\n✅ Nutrients from USDA API:\n")
        content = ""
        for n in nutrients:
            line = f"- {n.get('nutrientName')}: {n.get('value')} {n.get('unitName')}"
            print(line)
            content += line + "\n"

        store_in_chroma(food_name, content, sources=[], source_type="usda")

    else:
        print("⚠️ No USDA data found. Using LLM + web scraping...\n")
        result = run_pipeline(food_name)

        content = result["nutrients"]
        sources = result["sources"]
        print("\n🤖 LLM Nutrient Summary:\n")
        print(content)

        print("\n🔗 Sources:")
        for url in sources:
            print("- " + url)

        store_in_chroma(food_name, content, sources, source_type="llm")

# Run via input
if __name__ == "__main__":
    food = input("🍽️ Enter food name: ")
    get_nutrients_for_food(food)

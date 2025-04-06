import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# STEP 1: Google CSE Search Function
def search_google_cse(query, api_key, cx, num_results=5):
    print("🔍 Searching Google...")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': num_results
    }
    response = requests.get(url, params=params)
    results = response.json().get('items', [])
    return [item['link'] for item in results]

# STEP 2: Scrape page text
def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = " ".join(p.get_text() for p in soup.find_all('p'))
        return text
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return ""

# STEP 3: Extract nutrient-related keywords
def extract_nutrients(text):
    pattern = r'\b(fiber|probiotics?|prebiotics?|zinc|magnesium|vitamin\s?[a-zA-Z0-9]*|omega[-\s]?3|polyphenols?|iron|calcium|potassium|fermented foods?|digestive enzymes?)\b'
    return list(set(re.findall(pattern, text.lower())))

# STEP 4: Combine everything and save as CSV
def run_pipeline(api_key, cx):
    links = search_google_cse("nutrients for gut health", api_key, cx)
    all_data = []

    for url in links:
        print(f"🌐 Scraping: {url}")
        content = get_text_from_url(url)
        nutrients = extract_nutrients(content)
        all_data.append({"url": url, "nutrients": nutrients})

    df = pd.DataFrame(all_data)
    df.to_csv("gut_health_nutrients.csv", index=False)
    print("\n✅ Done! Data saved to: gut_health_nutrients.csv")

# 🔑 Replace with your own Google API key and CSE ID
YOUR_API_KEY = "AIzaSyCDpIKBq07S2fm5I6hoWvmlJgXKX6KU50o"
YOUR_CX = "17ba7fc064afc4524"

run_pipeline(YOUR_API_KEY, YOUR_CX)

from chroma_ns import get_data_by_food

if __name__ == "__main__":
    food = input("🍽️ Enter the food to fetch nutrients: ")
    data = get_data_by_food(food)

    if data:
        print(f"\n🍽️ Food: {data['food_name']}")
        print(f"📜 Source Type: {data['source_type']}")
        print(f"🕒 Saved on: {data['timestamp']}")
        print(f"\n📋 Nutrient Info:\n{data['nutrient_info']}")
        print(f"\n🔗 Sources: {data['source_urls']}")
    else:
        print("❌ No data found in ChromaDB.")

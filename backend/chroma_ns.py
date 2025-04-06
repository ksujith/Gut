#this file is used to store the nutrient knowledge from scrappper in chroma 
from chromadb import PersistentClient
from datetime import datetime

def store_in_chroma(food_name, content, sources, source_type):
    client = PersistentClient(path="./chroma_store")
    collection = client.get_or_create_collection("nutrient_knowledge")

    collection.add(
        documents=[content],
        metadatas=[{
            "food_name": food_name,
            "source_urls": ", ".join(sources) if sources else "",
            "source_type": source_type,
            "timestamp": datetime.now().isoformat()
        }],
        ids=[food_name.lower().replace(" ", "_")]
    )


def get_data_by_food(food_name):
    client = PersistentClient(path="./chroma_store")
    collection = client.get_or_create_collection("nutrient_knowledge")

    result = collection.get(
        ids=[food_name.lower().replace(" ", "_")],
        include=["documents", "metadatas"]
    )

    if not result["documents"]:
        print(f"❌ No data found for '{food_name}' in ChromaDB.")
        return None

    return {
        "food_name": result["metadatas"][0].get("food_name"),
        "nutrient_info": result["documents"][0],
        "source_urls": result["metadatas"][0].get("source_urls"),
        "source_type": result["metadatas"][0].get("source_type"),
        "timestamp": result["metadatas"][0].get("timestamp")
    }

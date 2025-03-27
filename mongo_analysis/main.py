import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

from bson import json_util

# Load environment variables from .env
load_dotenv()

# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["diabetic_records"]

    # Get all collections in 'diabetic_records' database
    collections = db.list_collection_names()
    print(f"📁 Collections in 'diabetic_records' database: {collections}")

    unique_structures = {}
    
    for collection_name in collections:
        collection = db[collection_name]

        # Get all documents from the collection
        documents = collection.find({})

        for doc in documents:
            # Extract the structure (sorted keys to maintain consistency)
            structure = tuple(sorted(doc.keys()))

            # Store unique structure and an example document
            if collection_name not in unique_structures:
                unique_structures[collection_name] = {}

            if structure not in unique_structures[collection_name]:
                unique_structures[collection_name][structure] = doc  # Save an example doc

    # Print unique document structures
    print("\n🔍 Unique Document Structures:")
    for collection, structures in unique_structures.items():
        print(f"\n📂 Collection: {collection}")
        for structure, example in structures.items():

            formatted_example = json.dumps(
                json.loads(
                    json_util.dumps(example)
                ),
                indent=4
            )
            
            print(f"📌 Structure: {structure}")
            print(f"📝 Example Document: {formatted_example}")


except Exception as e:
    print("❌ Error:", e)



import chromadb


# =========================================================
# CONFIGURATION
# =========================================================

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "dashboard_guidelines"


# =========================================================
# CONNECT TO CHROMA
# =========================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


# =========================================================
# USER QUESTION
# =========================================================

question = input(
    "\nAsk a dashboard question: "
)


# =========================================================
# RETRIEVE RELEVANT CHUNKS
# =========================================================

results = collection.query(
    query_texts=[question],
    n_results=3
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

print("\n" + "=" * 60)
print("RAG RETRIEVAL RESULTS")
print("=" * 60)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

for i, (document, metadata, distance) in enumerate(
    zip(documents, metadatas, distances),
    start=1
):

    print(f"\n--- RESULT {i} ---")

    print(
        f"Similarity distance: {distance:.4f}"
    )

    print(
        f"Source: {metadata.get('source')}"
    )

    print(
        f"Page: {metadata.get('page')}"
    )

    print("\nRetrieved text:")

    print(document)


print("\n" + "=" * 60)
print("RETRIEVAL COMPLETE")
print("=" * 60)

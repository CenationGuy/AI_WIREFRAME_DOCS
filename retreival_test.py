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


Ask a dashboard question: For revenue over time whats the best chart

============================================================
RAG RETRIEVAL RESULTS
============================================================

--- RESULT 1 ---
Similarity distance: 0.9193
Source: standards/dashboard_standard_guidelines.pdf
Page: 1

Retrieved text:
Dashboard Standard Guidelines — Test Version
Purpose
This dummy guideline defines the visual and analytical standards for the test version of an AI-generated Sales
Performance dashboard.
1. Required Layout
Use a clear title at the top. Place four KPI cards in a single row beneath the title. Place the primary trend
visualization below the KPI row. Supporting breakdowns should appear in the lower sections.
2. Required KPIs
The test dashboard must contain Total Revenue, Gross Margin, Units Sold, and Margin %.
3. Required Visualizations
Revenue Trend should use a line chart. Revenue by Region should use a bar chart. Revenue by Product should
use a bar chart.
4. Filters

--- RESULT 2 ---
Similarity distance: 0.9615
Source: standards/dashboard_standard_guidelines.pdf
Page: 1

Retrieved text:
use a bar chart.
4. Filters
Provide Date, Region, and Product filters. Filters should be visually separated from the main analytical charts.
5. Data Rules
Revenue and Cost are numeric measures. Gross Margin is Revenue minus Cost. Margin % is Gross Margin
divided by Revenue. Date is the time dimension; Region and Product are categorical dimensions.
6. Visual Validation Rules
The generated dashboard should be compared with the supplied standard image. Check title placement, KPI
count and ordering, chart types, relative layout, filter presence, and overall visual hierarchy. Detected deviations
should be returned as correction instructions for a subsequent generation pass.

--- RESULT 3 ---
Similarity distance: 1.5776
Source: standards/dashboard_standard_guidelines.pdf
Page: 1

Retrieved text:
should be returned as correction instructions for a subsequent generation pass.
7. Test Acceptance Criteria
Area
Minimum requirement
KPI row
4 KPI cards in one row
Primary chart
Revenue Trend line chart
Breakdowns
Region and Product charts
Filters
Date, Region, Product
Documentation
Dashboard specification + technical documentation

============================================================
RETRIEVAL COMPLETE
============================================================

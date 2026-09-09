import json
import os

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from google.genai.types import EmbedContentConfig
import chromadb


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"
LOCATION = "global"

EMBEDDING_MODEL = "gemini-embedding-001"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PDF_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "SAC Standards.pdf"
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = "sac_standards"


# ============================================================
# GEMINI CLIENT
# ============================================================

def create_gemini_client():

    return genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION
    )


# ============================================================
# STEP 1
# PDF EXTRACTION
# ============================================================

def extract_pdf():

    print("\n============================================")
    print("STEP 1 - PDF EXTRACTION")
    print("============================================")

    reader = PdfReader(PDF_PATH)

    print(
        f"PDF loaded successfully."
    )

    print(
        f"Total pages: {len(reader.pages)}"
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        text = text.strip()

        if not text:
            continue

        pages.append(
            {
                "page_number": page_number,
                "text": text
            }
        )

        print(
            f"Page {page_number}: "
            f"{len(text)} characters"
        )

    print(
        f"\nPages extracted: {len(pages)}"
    )

    return pages


# ============================================================
# STEP 2
# CHUNKING
# ============================================================

def create_chunks(pages):

    print("\n============================================")
    print("STEP 2 - TEXT CHUNKING")
    print("============================================")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for page in pages:

        page_number = page["page_number"]

        page_chunks = splitter.split_text(
            page["text"]
        )

        for chunk_number, chunk_text in enumerate(
            page_chunks,
            start=1
        ):

            chunks.append(
                {
                    "chunk_id": (
                        f"sac_page_{page_number}"
                        f"_chunk_{chunk_number}"
                    ),

                    "page_number": page_number,

                    "chunk_number": chunk_number,

                    "text": chunk_text
                }
            )

    print(
        f"Total chunks created: {len(chunks)}"
    )

    return chunks


# ============================================================
# STEP 3
# GEMINI EMBEDDING
# ============================================================

def generate_embedding(
    client,
    text
):

    response = client.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=text,

        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=3072
        )
    )

    return response.embeddings[0].values


# ============================================================
# STEP 4
# STORE IN CHROMADB
# ============================================================

def create_vector_database(chunks):

    print("\n============================================")
    print("STEP 3 - CREATING EMBEDDINGS")
    print("============================================")

    client = create_gemini_client()

    chroma_client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    print(
        f"Chroma collection: {COLLECTION_NAME}"
    )

    print(
        f"Existing vectors: "
        f"{collection.count()}"
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"Embedding chunk "
            f"{index}/{len(chunks)}"
        )

        embedding = generate_embedding(
            client,
            chunk["text"]
        )

        collection.upsert(

            ids=[
                chunk["chunk_id"]
            ],

            embeddings=[
                embedding
            ],

            documents=[
                chunk["text"]
            ],

            metadatas=[
                {
                    "page_number": chunk["page_number"],
                    "chunk_number": chunk["chunk_number"]
                }
            ]
        )

    print("\n============================================")
    print("VECTOR DATABASE COMPLETE")
    print("============================================")

    print(
        f"Total vectors: {collection.count()}"
    )

    return collection


# ============================================================
# STEP 5
# RETRIEVAL
# ============================================================

def retrieve_sac_standards(
    query,
    top_k=5
):

    print("\n============================================")
    print("STEP 4 - RETRIEVAL")
    print("============================================")

    client = create_gemini_client()

    chroma_client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    print(
        f"Query: {query}"
    )

    query_embedding = generate_embedding(
        client,
        query
    )

    results = collection.query(

        query_embeddings=[
            query_embedding
        ],

        n_results=top_k
    )

    retrieved_chunks = []

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    for document, metadata in zip(
        documents,
        metadatas
    ):

        retrieved_chunks.append(
            {
                "text": document,

                "page_number": metadata.get(
                    "page_number"
                ),

                "chunk_number": metadata.get(
                    "chunk_number"
                )
            }
        )

    return retrieved_chunks


# ============================================================
# DISPLAY RETRIEVED RESULTS
# ============================================================

def print_results(results):

    print("\n============================================")
    print("RETRIEVED SAC STANDARDS")
    print("============================================")

    for index, result in enumerate(
        results,
        start=1
    ):

        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Page: {result['page_number']}"
        )

        print(
            f"Chunk: {result['chunk_number']}"
        )

        print(
            result["text"]
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n============================================")
    print("SAC RAG PIPELINE")
    print("============================================")

    # --------------------------------------------------------
    # 1. Extract PDF
    # --------------------------------------------------------

    pages = extract_pdf()

    # --------------------------------------------------------
    # 2. Create chunks
    # --------------------------------------------------------

    chunks = create_chunks(
        pages
    )

    # --------------------------------------------------------
    # 3. Create embeddings + ChromaDB
    # --------------------------------------------------------

    create_vector_database(
        chunks
    )

    # --------------------------------------------------------
    # 4. Test retrieval
    # --------------------------------------------------------

    query = (
        "What are the standards for KPI boxes "
        "in an enterprise dashboard?"
    )

    results = retrieve_sac_standards(
        query,
        top_k=5
    )

    print_results(
        results
    )

    print("\n============================================")
    print("SAC RAG PIPELINE COMPLETE")
    print("============================================")

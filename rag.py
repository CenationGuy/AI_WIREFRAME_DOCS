from google.cloud import storage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb
from pypdf import PdfReader
import os


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

BUCKET_NAME = "ai_wireframe_bucket"

PDF_PATH = "standards/dashboard_design_guidelines_test.pdf"

LOCAL_PDF = "dashboard_guidelines_test.pdf"

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "dashboard_guidelines"


# =========================================================
# DOWNLOAD PDF FROM GCS
# =========================================================

def download_pdf_from_gcs():

    print("Downloading guideline PDF from GCS...")

    storage_client = storage.Client(
        project=PROJECT_ID
    )

    bucket = storage_client.bucket(
        BUCKET_NAME
    )

    blob = bucket.blob(
        PDF_PATH
    )

    blob.download_to_filename(
        LOCAL_PDF
    )

    print(
        f"PDF downloaded to: {LOCAL_PDF}"
    )


# =========================================================
# EXTRACT PDF TEXT
# =========================================================

def extract_pdf_text():

    print("\nExtracting text from PDF...")

    reader = PdfReader(
        LOCAL_PDF
    )

    documents = []

    for page_number, page in enumerate(
        reader.pages
    ):

        text = page.extract_text()

        if text and text.strip():

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": PDF_PATH,
                        "page": page_number + 1
                    }
                )
            )

    print(
        f"Pages extracted: {len(documents)}"
    )

    return documents


# =========================================================
# CHUNK DOCUMENT
# =========================================================

def create_chunks(documents):

    print("\nCreating chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(
        documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    return chunks


# =========================================================
# CREATE VECTOR DATABASE
# =========================================================

def create_vector_store(chunks):

    print("\nCreating Chroma vector database...")

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    # Delete old collection during testing
    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    # -----------------------------------------------------
    # Chroma's default embedding function
    # -----------------------------------------------------

    print(
        "Creating embeddings..."
    )

    ids = []
    documents = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(
            f"chunk_{index}"
        )

        documents.append(
            chunk.page_content
        )

        metadatas.append(
            chunk.metadata
        )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(
        f"Stored {len(chunks)} chunks in Chroma."
    )

    return collection


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("RAG INGESTION PIPELINE")
    print("=" * 60)

    download_pdf_from_gcs()

    documents = extract_pdf_text()

    chunks = create_chunks(
        documents
    )

    collection = create_vector_store(
        chunks
    )

    print("\n" + "=" * 60)
    print("RAG INGESTION COMPLETE")
    print("=" * 60)

    print(
        f"Vector database: {CHROMA_PATH}"
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    print(
        f"Documents indexed: {len(chunks)}"
    )

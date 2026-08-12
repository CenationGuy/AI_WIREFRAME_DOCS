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



 python rag.py
============================================================
RAG INGESTION PIPELINE
============================================================
Downloading guideline PDF from GCS...
Traceback (most recent call last):
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 4718, in _prep_and_do_download
    self._do_download(
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 1094, in _do_download
    response = download.consume(transport, timeout=timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/_media/requests/download.py", line 280, in consume
    return _request_helpers.wait_and_retry(retriable_request, self._retry_strategy)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/_media/requests/_request_helpers.py", line 107, in wait_and_retry
    return func()
           ^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 295, in retry_wrapped_func
    return retry_target(
           ^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 157, in retry_target
    next_sleep = _retry_error_helper(
                 ^^^^^^^^^^^^^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_base.py", line 215, in _retry_error_helper
    raise final_exc from source_exc
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/api_core/retry/retry_unary.py", line 148, in retry_target
    result = target()
             ^^^^^^^^
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/_media/requests/download.py", line 262, in retriable_request
    self._process_response(result)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/_media/_download.py", line 230, in _process_response
    _helpers.require_status_code(
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/_media/_helpers.py", line 100, in require_status_code
    raise InvalidResponse(
google.cloud.storage.exceptions.InvalidResponse: ('Request failed with status code', 404, 'Expected one of', <HTTPStatus.OK: 200>, <HTTPStatus.PARTIAL_CONTENT: 206>)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/abhisheks_s/ai_wireframe/backend/rag.py", line 191, in <module>
    download_pdf_from_gcs()
  File "/home/abhisheks_s/ai_wireframe/backend/rag.py", line 46, in download_pdf_from_gcs
    blob.download_to_filename(
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 1425, in download_to_filename
    self._handle_filename_and_download(
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 1298, in _handle_filename_and_download
    self._prep_and_do_download(
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 4732, in _prep_and_do_download
    _raise_from_invalid_response(exc)
  File "/home/abhisheks_s/.venv/lib/python3.12/site-packages/google/cloud/storage/blob.py", line 5240, in _raise_from_invalid_response
    raise exceptions.from_http_status(response.status_code, message, response=response)
google.api_core.exceptions.NotFound: 404 GET https://storage.googleapis.com/download/storage/v1/b/ai_wireframe_bucket/o/standards%2Fdashboard_design_guidelines_test.pdf?alt=media: No such object: ai_wireframe_bucket/standards/dashboard_design_guidelines_test.pdf: ('Request failed with status code', 404, 'Expected one of', <HTTPStatus.OK: 200>, <HTTPStatus.PARTIAL_CONTENT: 206>)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io


app = FastAPI(
    title="AI Wireframe API"
)


# --------------------------------------------------
# CORS
# Allows your React frontend to call this API
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Wireframe Backend is running"
    }


# --------------------------------------------------
# GENERATE DASHBOARD
# STEP 1:
# Receive CSV and return basic data information
# --------------------------------------------------

@app.post("/generate-dashboard")
async def generate_dashboard(
    file: UploadFile = File(...)
):

    # Check file type
    if not file.filename.endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )


    try:

        # Read uploaded CSV
        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )


        # Basic response for now
        return {

            "status": "success",

            "message": "CSV uploaded successfully",

            "filename": file.filename,

            "rows": len(df),

            "columns": list(df.columns),

            "preview": df.head(5).to_dict(
                orient="records"
            )

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

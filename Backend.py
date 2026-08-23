from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="AI Wireframe API"
)


# ==================================================
# CORS
# Allows React frontend to communicate with FastAPI
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "AI Wireframe Backend is running"
    }


# ==================================================
# GENERATE DASHBOARD
#
# CURRENT STEP:
#
# React / Swagger
#        ↓
# Upload CSV
#        ↓
# FastAPI receives CSV
#        ↓
# Pandas reads CSV
#        ↓
# Convert NaN → None
#        ↓
# Return JSON-safe preview
# ==================================================

@app.post("/generate-dashboard")
async def generate_dashboard(
    file: UploadFile = File(...)
):

    # ----------------------------------------------
    # CHECK FILE TYPE
    # ----------------------------------------------

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )


    try:

        # ------------------------------------------
        # READ UPLOADED FILE
        # ------------------------------------------

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )


        # ------------------------------------------
        # CREATE PREVIEW
        # ------------------------------------------

        preview_df = df.head(5).copy()


        # ------------------------------------------
        # CONVERT DATAFRAME TO OBJECT TYPE
        #
        # This allows us to replace NaN with None
        # ------------------------------------------

        preview_df = preview_df.astype(object)


        # ------------------------------------------
        # REPLACE NaN WITH None
        #
        # JSON understands:
        # None → null
        #
        # JSON does NOT understand:
        # NaN
        # ------------------------------------------

        preview_df = preview_df.where(
            pd.notnull(preview_df),
            None
        )


        # ------------------------------------------
        # CONVERT TO PYTHON DICTIONARY
        # ------------------------------------------

        preview = preview_df.to_dict(
            orient="records"
        )


        # ------------------------------------------
        # RETURN JSON RESPONSE
        # ------------------------------------------

        return {

            "status": "success",

            "message": "CSV uploaded successfully",

            "filename": file.filename,

            "rows": int(len(df)),

            "columns": list(df.columns),

            "preview": preview

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

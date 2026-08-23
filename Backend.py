from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io

# Import our new CSV profiler
from csv_profiler import profile_csv_dataframe


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
# CURRENT FLOW:
#
# Upload CSV
#      ↓
# FastAPI receives CSV
#      ↓
# Pandas reads CSV
#      ↓
# csv_profiler.py analyzes DataFrame
#      ↓
# Return Data Profile
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
        # READ UPLOADED CSV
        # ------------------------------------------

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )


        # ------------------------------------------
        # PROFILE THE CSV
        #
        # We pass the Pandas DataFrame to our
        # csv_profiler.py
        # ------------------------------------------

        data_profile = profile_csv_dataframe(df)


        # ------------------------------------------
        # RETURN RESULT
        # ------------------------------------------

        return {

            "status": "success",

            "message": "CSV profiled successfully",

            "filename": file.filename,

            "data_profile": data_profile

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

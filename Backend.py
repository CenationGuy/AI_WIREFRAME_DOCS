from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io

# ==================================================
# IMPORT OUR BACKEND COMPONENTS
# ==================================================

from csv_profiler import profile_csv_dataframe
from dashboard_planner import create_dashboard_plan


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="AI Wireframe API"
)


# ==================================================
# CORS
#
# Allows the React frontend to communicate with
# the FastAPI backend.
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
# COMPLETE CURRENT FLOW:
#
# User uploads CSV
#        ↓
# FastAPI receives file
#        ↓
# Pandas reads CSV
#        ↓
# CSV Profiler analyzes dataset
#        ↓
# data_profile
#        ↓
# Dashboard Planner sends profile to Gemini
#        ↓
# dashboard_spec
#        ↓
# Return result
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
        # STEP 1:
        # PROFILE THE CSV
        #
        # df
        # ↓
        # data_profile
        # ------------------------------------------

        data_profile = profile_csv_dataframe(
            df
        )


        # ------------------------------------------
        # STEP 2:
        # CREATE DASHBOARD PLAN
        #
        # data_profile
        # ↓
        # Gemini
        # ↓
        # dashboard_spec
        # ------------------------------------------

        dashboard_spec = create_dashboard_plan(
            data_profile
        )


        # ------------------------------------------
        # RETURN FINAL RESPONSE
        # ------------------------------------------

        return {

            "status": "success",

            "message": "Dashboard plan generated successfully",

            "filename": file.filename,

            "data_profile": data_profile,

            "dashboard_spec": dashboard_spec
        }


    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

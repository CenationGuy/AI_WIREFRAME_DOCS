from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import io
import base64
from io import BytesIO


# ==================================================
# IMPORT BACKEND COMPONENTS
# ==================================================

from csv_profiler import profile_csv_dataframe
from dashboard_planner import create_dashboard_plan
from dashboard_summarizer import generate_dashboard_summary
from visual_designer import generate_dashboard_design


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="AI Wireframe API"
)


# ==================================================
# CORS
#
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
# CONVERT PIL IMAGE TO BASE64
#
# React cannot directly receive a PIL Image object.
#
# So:
#
# PIL Image
#     ↓
# PNG bytes
#     ↓
# Base64 string
#     ↓
# JSON response
# ==================================================

def image_to_base64(image):

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    image_bytes = buffer.getvalue()

    base64_string = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return base64_string


# ==================================================
# GENERATE DASHBOARD ENDPOINT
#
# COMPLETE PIPELINE:
#
# CSV
#  ↓
# Pandas DataFrame
#  ↓
# CSV Profiler
#  ↓
# Data Profile
#  ↓
# Dashboard Planner
#  ↓
# Multi-Sheet Dashboard Specification
#  ↓
# ├── Dashboard Summarizer
# │       ↓
# │   Text Summary
# │
# └── Visual Designer
#         ↓
#     One Image Per Sheet
#         ↓
#     Base64 Conversion
#  ↓
# Final API Response
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
        # STEP 1:
        # READ CSV
        # ------------------------------------------

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )


        # ------------------------------------------
        # STEP 2:
        # PROFILE CSV
        #
        # DataFrame
        #     ↓
        # data_profile
        # ------------------------------------------

        data_profile = profile_csv_dataframe(
            df
        )


        # ------------------------------------------
        # STEP 3:
        # CREATE DASHBOARD PLAN
        #
        # data_profile
        #     ↓
        # Gemini
        #     ↓
        # dashboard_spec
        # ------------------------------------------

        dashboard_spec = create_dashboard_plan(
            data_profile
        )


        # ------------------------------------------
        # STEP 4:
        # GENERATE DASHBOARD SUMMARY
        #
        # dashboard_spec
        #     ↓
        # text summary
        # ------------------------------------------

        dashboard_summary = generate_dashboard_summary(
            dashboard_spec
        )


        # ------------------------------------------
        # STEP 5:
        # GENERATE DASHBOARD DESIGNS
        #
        # Each sheet gets its own generated image
        #
        # dashboard_spec
        #     ↓
        # visual_designer.py
        #     ↓
        # PIL Images
        # ------------------------------------------

        generated_sheets = generate_dashboard_design(
            dashboard_spec
        )


        # ------------------------------------------
        # STEP 6:
        # CONVERT ALL IMAGES TO BASE64
        # ------------------------------------------

        response_sheets = []

        for sheet in generated_sheets:

            image_base64 = image_to_base64(
                sheet["image"]
            )

            response_sheets.append(
                {
                    "sheet_number": sheet["sheet_number"],
                    "title": sheet["title"],

                    "image": (
                        f"data:image/png;base64,"
                        f"{image_base64}"
                    )
                }
            )


        # ------------------------------------------
        # STEP 7:
        # RETURN COMPLETE RESPONSE
        # ------------------------------------------

        return {

            "status": "success",

            "message": (
                "Dashboard generated successfully"
            ),

            "filename": file.filename,


            # ----------------------------------
            # CSV ANALYSIS
            # ----------------------------------

            "data_profile": data_profile,


            # ----------------------------------
            # DASHBOARD PLAN
            # ----------------------------------

            "dashboard_spec": dashboard_spec,


            # ----------------------------------
            # TEXT SUMMARY
            # ----------------------------------

            "dashboard_summary": dashboard_summary,


            # ----------------------------------
            # GENERATED DASHBOARD SHEETS
            # ----------------------------------

            "generated_sheets": response_sheets
        }


    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    except Exception as e:

        print(
            f"ERROR: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

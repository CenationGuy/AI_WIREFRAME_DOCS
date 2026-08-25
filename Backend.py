import io
import base64
import os

import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
# PIL Image
#     ↓
# PNG bytes
#     ↓
# Base64 string
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
#     Save PNG Files
#         ↓
#     Convert to Base64
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

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )


    try:

        # ------------------------------------------
        # STEP 1: READ CSV
        # ------------------------------------------

        print("\n========================================")
        print("STEP 1: READING CSV")
        print("========================================")

        contents = await file.read()

        df = pd.read_csv(
            io.BytesIO(contents)
        )

        print(
            f"CSV loaded successfully: {file.filename}"
        )

        print(
            f"Rows: {len(df)}"
        )

        print(
            f"Columns: {len(df.columns)}"
        )


        # ------------------------------------------
        # STEP 2: PROFILE CSV
        # ------------------------------------------

        print("\n========================================")
        print("STEP 2: PROFILING CSV")
        print("========================================")

        data_profile = profile_csv_dataframe(
            df
        )

        print(
            "CSV profiling completed successfully."
        )


        # ------------------------------------------
        # STEP 3: CREATE DASHBOARD PLAN
        # ------------------------------------------

        print("\n========================================")
        print("STEP 3: CREATING DASHBOARD PLAN")
        print("========================================")

        dashboard_spec = create_dashboard_plan(
            data_profile
        )

        print(
            "Dashboard plan generated successfully."
        )

        print(
            f"Dashboard title: "
            f"{dashboard_spec.get('dashboard_title')}"
        )

        print(
            f"Number of sheets: "
            f"{len(dashboard_spec.get('sheets', []))}"
        )


        # ------------------------------------------
        # STEP 4: GENERATE DASHBOARD SUMMARY
        # ------------------------------------------

        print("\n========================================")
        print("STEP 4: GENERATING DASHBOARD SUMMARY")
        print("========================================")

        dashboard_summary = generate_dashboard_summary(
            dashboard_spec
        )

        print(
            "Dashboard summary generated successfully."
        )


        # ------------------------------------------
        # STEP 5: GENERATE DASHBOARD IMAGES
        # ------------------------------------------

        print("\n========================================")
        print("STEP 5: GENERATING DASHBOARD IMAGES")
        print("========================================")

        generated_sheets = generate_dashboard_design(
            dashboard_spec
        )

        print(
            f"Generated {len(generated_sheets)} "
            f"dashboard sheet image(s)."
        )


        # ------------------------------------------
        # STEP 6: CREATE IMAGE OUTPUT FOLDER
        # ------------------------------------------

        print("\n========================================")
        print("STEP 6: SAVING GENERATED IMAGES")
        print("========================================")

        os.makedirs(
            "generated_images",
            exist_ok=True
        )


        # ------------------------------------------
        # STEP 7:
        #
        # SAVE EACH IMAGE
        # +
        # CONVERT EACH IMAGE TO BASE64
        # ------------------------------------------

        response_sheets = []

        for sheet in generated_sheets:

            sheet_number = sheet.get(
                "sheet_number",
                1
            )

            sheet_title = sheet.get(
                "title",
                "Untitled Sheet"
            )


            # --------------------------------------
            # CREATE FILE PATH
            # --------------------------------------

            image_path = os.path.join(
                "generated_images",
                f"sheet_{sheet_number}.png"
            )


            # --------------------------------------
            # SAVE IMAGE AS PNG
            # --------------------------------------

            sheet["image"].save(
                image_path,
                format="PNG"
            )

            print(
                f"Image saved to: {image_path}"
            )


            # --------------------------------------
            # CONVERT IMAGE TO BASE64
            # --------------------------------------

            image_base64 = image_to_base64(
                sheet["image"]
            )


            # --------------------------------------
            # ADD SHEET TO API RESPONSE
            # --------------------------------------

            response_sheets.append(
                {
                    "sheet_number": sheet_number,

                    "title": sheet_title,

                    "image": (
                        "data:image/png;base64,"
                        + image_base64
                    )
                }
            )


        # ------------------------------------------
        # STEP 8: SUCCESS
        # ------------------------------------------

        print("\n========================================")
        print("DASHBOARD GENERATION COMPLETED")
        print("========================================")

        print(
            f"Total sheets generated: "
            f"{len(response_sheets)}"
        )


        # ------------------------------------------
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

        print("\n========================================")
        print("ERROR DURING DASHBOARD GENERATION")
        print("========================================")

        print(
            f"Error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

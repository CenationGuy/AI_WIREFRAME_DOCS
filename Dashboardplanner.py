import json

from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-flash"


# ============================================================
# GEMINI / VERTEX AI
# ============================================================

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    project=PROJECT_ID,
    location=LOCATION,
    vertexai=True,
    temperature=0
)


# ============================================================
# FORMAT SAC RAG RESULTS
# ============================================================

def format_sac_standards(sac_standards):

    if not sac_standards:
        return "No SAC standards were retrieved."

    formatted = []

    for index, standard in enumerate(
        sac_standards,
        start=1
    ):

        page_number = standard.get(
            "page_number",
            "Unknown"
        )

        chunk_number = standard.get(
            "chunk_number",
            "Unknown"
        )

        text = standard.get(
            "text",
            ""
        )

        formatted.append(
            f"""
--- SAC STANDARD {index} ---
Page: {page_number}
Chunk: {chunk_number}

{text}
"""
        )

    return "\n".join(formatted)


# ============================================================
# CREATE DASHBOARD PLAN
# ============================================================

def create_dashboard_plan(
    data_profile,
    sac_standards
):

    # --------------------------------------------------------
    # Format retrieved SAC knowledge
    # --------------------------------------------------------

    sac_context = format_sac_standards(
        sac_standards
    )


    # --------------------------------------------------------
    # Extract data profile
    # --------------------------------------------------------

    dimensions = data_profile.get(
        "dimensions",
        []
    )

    date_dimensions = data_profile.get(
        "date_dimensions",
        []
    )

    measures = data_profile.get(
        "measures",
        []
    )

    columns = data_profile.get(
        "columns",
        []
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are an expert enterprise dashboard planner
and business intelligence analyst.

Your job is to design a dashboard specification
based ONLY on the available dataset and the
relevant dashboard standards provided below.

You must not invent data fields, metrics,
dimensions, or business concepts that do not exist
in the dataset.


============================================================
DATASET PROFILE
============================================================

Available columns:

{columns}


Dimensions:

{dimensions}


Date dimensions:

{date_dimensions}


Measures:

{measures}


============================================================
RETRIEVED SAC DASHBOARD STANDARDS
============================================================

The following standards were retrieved from the
SAC standards knowledge base.

Use these standards as design guidance when deciding:

- KPI selection
- KPI structure
- KPI presentation
- chart selection
- visual hierarchy
- dashboard simplicity
- screen estate
- filters
- interaction
- colours
- layout
- number of metrics
- dashboard usability


{sac_context}


============================================================
IMPORTANT RAG RULE
============================================================

The retrieved SAC standards are GUIDANCE.

They do NOT give you permission to invent
dataset fields or metrics.

The dataset profile determines WHAT data can
actually be displayed.

The SAC standards determine HOW that information
should be presented.


============================================================
DASHBOARD PLANNING
============================================================

Decide whether the dashboard should contain
ONE or MULTIPLE sheets.

Create multiple sheets only when there is a clear
analytical reason to separate different purposes.

Avoid unnecessary sheets.


============================================================
KPI RULES
============================================================

Select meaningful KPIs from the available measures.

Use only measures that actually exist in the dataset.

A KPI should have a clear analytical purpose.

Avoid creating too many separate KPI cards.

Prefer a small number of meaningful KPIs.

Do not invent targets if the dataset does not
contain target information.

Do not invent thresholds if the dataset does not
contain threshold information.

Do not invent RAG status values.


============================================================
CHART RULES
============================================================

Choose chart types appropriate for the available data.

Use:

- line charts for time-based trends
- bar charts for categorical comparisons
- pie charts only when a simple part-to-whole
  relationship is genuinely useful

Do not create charts that require unavailable fields.

Every chart must reference real dataset columns.

Avoid duplicate charts that communicate essentially
the same information.


============================================================
FILTER RULES
============================================================

Use filters only for useful dimensions.

Do not create unnecessary filters.

Filters must reference real dataset columns.

Date filters may be used when an appropriate
date dimension exists.


============================================================
DATA INTEGRITY RULES
============================================================

VERY IMPORTANT:

1. Use ONLY columns present in the dataset.

2. Do NOT invent columns.

3. Do NOT invent measures.

4. Do NOT invent targets.

5. Do NOT invent thresholds.

6. Do NOT invent business values.

7. Do NOT create metrics that require unavailable
   data.

8. Do NOT calculate unsupported metrics.

9. Use appropriate aggregations for available
   measures.

10. Every KPI and chart must be traceable to
    actual dataset fields.


============================================================
VISUAL DESIGN PRINCIPLES
============================================================

Apply relevant SAC standards from the retrieved
knowledge.

In particular:

- avoid unnecessary visual clutter
- make important information visually prominent
- use screen estate effectively
- keep KPI presentation simple
- align KPIs with supporting visuals
- avoid excessive colours
- use neutral colours where status colouring
  is not required
- avoid redundant metrics
- avoid excessive precision
- avoid decorative elements that do not add value
- make interactive elements clear when applicable


============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Do not include:

- markdown
- ```json
- explanations
- commentary
- text before the JSON
- text after the JSON


Use exactly this structure:


{{
    "dashboard_title": "Dashboard title",

    "sheets": [

        {{
            "sheet_number": 1,

            "title": "Sheet title",

            "purpose": "Purpose of this sheet",

            "kpis": [
                {{
                    "title": "KPI title",
                    "field": "actual dataset column",
                    "aggregation": "sum"
                }}
            ],

            "charts": [
                {{
                    "title": "Chart title",
                    "type": "line",
                    "x_axis": "actual dataset column",
                    "y_axis": "actual dataset column"
                }}
            ],

            "filters": [
                "actual dataset column"
            ]
        }}

    ]
}}


============================================================
FINAL CHECK BEFORE RESPONDING
============================================================

Before returning the JSON, verify:

- Every KPI field exists in the dataset.
- Every chart x-axis field exists in the dataset.
- Every chart y-axis field exists in the dataset.
- Every filter exists in the dataset.
- No invented metrics exist.
- No invented targets exist.
- No invented thresholds exist.
- Chart types are appropriate.
- The dashboard is not overcrowded.
- SAC standards are being used as design guidance.
- The output is valid JSON.
"""


    # ========================================================
    # CALL GEMINI
    # ========================================================

    response = llm.invoke(
        prompt
    )


    # ========================================================
    # READ RESPONSE
    # ========================================================

    dashboard_spec_text = response.content


    # --------------------------------------------------------
    # Remove accidental markdown fences
    # --------------------------------------------------------

    dashboard_spec_text = (
        dashboard_spec_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        dashboard_spec = json.loads(
            dashboard_spec_text
        )

    except json.JSONDecodeError as e:

        print("\n========================================")
        print("DASHBOARD PLANNER JSON ERROR")
        print("========================================")

        print(
            "Gemini returned:"
        )

        print(
            dashboard_spec_text
        )

        raise ValueError(
            f"Dashboard planner returned invalid JSON: {e}"
        )


    # ========================================================
    # RETURN
    # ========================================================

    return dashboard_spec

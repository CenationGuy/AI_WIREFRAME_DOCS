import json
import os
from io import BytesIO

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    HttpOptions,
    Modality,
    Part,
)
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

LOCATION = "global"


# ============================================================
# IMAGE MODEL
# ============================================================

IMAGE_MODEL = "gemini-3.1-flash-image"

# Alternative:
#
# IMAGE_MODEL = "gemini-2.5-flash-image"


# ============================================================
# OPTIONAL REFERENCE IMAGE
# ============================================================

REFERENCE_IMAGE = None


# ============================================================
# CREATE VERTEX AI CLIENT
# ============================================================

def create_client():

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        http_options=HttpOptions(
            api_version="v1"
        )
    )

    return client


# ============================================================
# GENERIC VISUAL DESIGN PRINCIPLES
# ============================================================

def get_default_visual_standard():

    return {

        "overall_style": [
            "professional enterprise business intelligence dashboard",
            "clear information hierarchy",
            "consistent alignment",
            "logical grouping of related information",
            "readable typography",
            "effective use of available space"
        ],

        "layout": [
            "use a structured dashboard grid",
            "group KPI metrics logically",
            "give primary analysis more visual importance",
            "place supporting charts in secondary areas",
            "keep filters visually organized"
        ],

        "kpi_cards": [
            "make KPI values visually prominent",
            "maintain consistent KPI card dimensions",
            "align KPI cards cleanly",
            "include supporting information only when useful"
        ],

        "charts": [
            "use the chart type defined in the dashboard specification",
            "maintain readable axis labels",
            "use consistent chart styling",
            "avoid unnecessary decoration",
            "maintain clear legends where required"
        ],

        "filters": [
            "make filters easy to identify",
            "visually separate filters from primary analysis",
            "organize multiple filters logically"
        ],

        "avoid": [
            "unnecessary decorative elements",
            "visual clutter",
            "inconsistent alignment",
            "excessive use of colors",
            "unreadable text"
        ]
    }


# ============================================================
# LOAD OPTIONAL REFERENCE IMAGE
# ============================================================

def load_reference_image():

    if REFERENCE_IMAGE is None:
        return None

    if not os.path.exists(REFERENCE_IMAGE):

        raise FileNotFoundError(
            f"Reference image not found: {REFERENCE_IMAGE}"
        )

    return Image.open(REFERENCE_IMAGE)


# ============================================================
# BUILD VISUAL DESIGN PROMPT
# ============================================================

def build_visual_design_prompt(
    dashboard_title,
    sheet,
    visual_standard
):

    sheet_json = json.dumps(
        sheet,
        indent=2
    )

    visual_standard_json = json.dumps(
        visual_standard,
        indent=2
    )

    prompt = f"""
You are an expert enterprise dashboard designer.

Your task is to create a high-quality visual design for ONE
dashboard sheet.

============================================================
OVERALL DASHBOARD
============================================================

Dashboard title:

{dashboard_title}


============================================================
CURRENT SHEET
============================================================

{sheet_json}


============================================================
VISUAL DESIGN STANDARDS
============================================================

{visual_standard_json}


============================================================
MANDATORY DASHBOARD STRUCTURE
============================================================

You MUST follow this exact high-level structure.

1. RED TOP BAR

The FIRST major visual element must be a prominent
horizontal RED top bar.

The red top bar must:

- span the full width of the dashboard
- use red as the dominant background color
- contain the dashboard title
- optionally contain branding, navigation, or utility icons
- look clean and professional

Do not place charts, KPI cards, or filters above the red
top bar.


2. FILTER PANE

Immediately BELOW the red top bar, create a dedicated
horizontal FILTER PANE.

The filter pane must contain ALL filters defined for the
current sheet.

Each filter should look like a realistic enterprise UI control,
such as:

- dropdown selector
- date selector
- category selector
- search/filter control

The filter controls should:

- be clearly labelled
- be aligned consistently
- be arranged horizontally where possible
- be visually separated from the main content
- appear directly below the red top bar

Do not place filters randomly inside charts.


3. MAIN DASHBOARD CONTENT

Below the filter pane, create the main dashboard content.

Include:

- KPI cards
- primary charts
- secondary supporting charts

Use a structured enterprise dashboard grid.

Place KPI cards near the top of the main content area.

Give the most important chart greater visual prominence.

Arrange supporting charts logically below or beside the
primary chart.


============================================================
SHEET-SPECIFIC RULES
============================================================

This image represents ONLY the current sheet.

Use the current sheet's:

- title
- purpose
- KPIs
- charts
- filters

Do not include charts or KPIs from other sheets.

Do not invent additional metrics or charts.

Use the chart types defined in the sheet specification.


============================================================
GENERAL DESIGN INSTRUCTIONS
============================================================

Create a realistic enterprise business intelligence dashboard.

Prioritize:

- readability
- clear information hierarchy
- professional appearance
- consistent spacing
- clean alignment
- logical grouping
- realistic UI components

Avoid:

- decorative artwork
- unnecessary visual elements
- clutter
- excessive colors
- unreadable text
- unrelated charts

This should look like a dashboard that could realistically
be used inside an enterprise application.

Generate ONLY the dashboard visual design.
"""

    return prompt


# ============================================================
# GENERATE DASHBOARD IMAGE
# ============================================================

def generate_dashboard_image(
    client,
    prompt,
    reference_image=None
):

    contents = []

    # --------------------------------------------------------
    # OPTIONAL REFERENCE IMAGE
    # --------------------------------------------------------

    if reference_image is not None:

        image_buffer = BytesIO()

        reference_image.save(
            image_buffer,
            format="PNG"
        )

        image_bytes = image_buffer.getvalue()

        reference_part = Part.from_bytes(
            data=image_bytes,
            mime_type="image/png"
        )

        contents.append(reference_part)

        contents.append(
            """
Use the reference image as inspiration for overall visual
quality and design style.

Do not copy it exactly.

Adapt the design to the current dashboard sheet specification.
"""
        )


    # --------------------------------------------------------
    # ADD PROMPT
    # --------------------------------------------------------

    contents.append(prompt)


    # --------------------------------------------------------
    # CALL GEMINI IMAGE MODEL
    # --------------------------------------------------------

    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=contents,
        config=GenerateContentConfig(
            response_modalities=[
                Modality.TEXT,
                Modality.IMAGE
            ]
        )
    )

    return response


# ============================================================
# EXTRACT IMAGE FROM GEMINI RESPONSE
# ============================================================

def extract_generated_image(response):

    for candidate in response.candidates:

        for part in candidate.content.parts:

            if (
                hasattr(part, "inline_data")
                and part.inline_data is not None
            ):

                image_bytes = part.inline_data.data

                image = Image.open(
                    BytesIO(image_bytes)
                )

                return image

    raise ValueError(
        "No image was returned by the Gemini model."
    )


# ============================================================
# GENERATE ONE SHEET
# ============================================================

def generate_single_sheet_design(
    client,
    dashboard_title,
    sheet,
    visual_standard,
    reference_image
):

    # --------------------------------------------------------
    # BUILD PROMPT FOR THIS SPECIFIC SHEET
    # --------------------------------------------------------

    prompt = build_visual_design_prompt(
        dashboard_title=dashboard_title,
        sheet=sheet,
        visual_standard=visual_standard
    )


    # --------------------------------------------------------
    # GENERATE IMAGE
    # --------------------------------------------------------

    response = generate_dashboard_image(
        client=client,
        prompt=prompt,
        reference_image=reference_image
    )


    # --------------------------------------------------------
    # EXTRACT IMAGE
    # --------------------------------------------------------

    image = extract_generated_image(
        response
    )

    return image


# ============================================================
# MAIN FUNCTION
#
# THIS IS WHAT main.py WILL CALL
# ============================================================

def generate_dashboard_design(dashboard_spec):

    # --------------------------------------------------------
    # CREATE GEMINI CLIENT
    # --------------------------------------------------------

    client = create_client()


    # --------------------------------------------------------
    # LOAD VISUAL DESIGN RULES
    # --------------------------------------------------------

    visual_standard = (
        get_default_visual_standard()
    )


    # --------------------------------------------------------
    # LOAD OPTIONAL REFERENCE IMAGE
    # --------------------------------------------------------

    reference_image = (
        load_reference_image()
    )


    # --------------------------------------------------------
    # GET DASHBOARD TITLE
    # --------------------------------------------------------

    dashboard_title = dashboard_spec.get(
        "dashboard_title",
        "Business Dashboard"
    )


    # --------------------------------------------------------
    # GET ALL SHEETS
    # --------------------------------------------------------

    sheets = dashboard_spec.get(
        "sheets",
        []
    )


    if not sheets:

        raise ValueError(
            "No sheets found in dashboard specification."
        )


    # --------------------------------------------------------
    # STORE ALL GENERATED SHEET IMAGES
    # --------------------------------------------------------

    generated_sheets = []


    # --------------------------------------------------------
    # GENERATE ONE IMAGE FOR EACH SHEET
    # --------------------------------------------------------

    for sheet in sheets:

        print(
            f"Generating design for: "
            f"{sheet.get('title', 'Untitled Sheet')}"
        )


        image = generate_single_sheet_design(
            client=client,
            dashboard_title=dashboard_title,
            sheet=sheet,
            visual_standard=visual_standard,
            reference_image=reference_image
        )


        # Store the sheet information and image together

        generated_sheets.append(
            {
                "sheet_number": sheet.get(
                    "sheet_number"
                ),

                "title": sheet.get(
                    "title"
                ),

                "image": image
            }
        )


    # --------------------------------------------------------
    # RETURN ALL GENERATED DASHBOARD SHEETS
    # --------------------------------------------------------

    return generated_sheets

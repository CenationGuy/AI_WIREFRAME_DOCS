import json
import os
from pathlib import Path
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

BASE_DIR = Path(__file__).resolve().parent


# ------------------------------------------------------------
# GOOGLE CLOUD / VERTEX AI
# ------------------------------------------------------------

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

# Gemini image models are commonly used with global location.
LOCATION = "global"


# ------------------------------------------------------------
# IMAGE MODEL
# ------------------------------------------------------------

# DEFAULT MODEL
IMAGE_MODEL = "gemini-3.1-flash-image"

# To test the other model later, change to:
#
# IMAGE_MODEL = "gemini-2.5-flash-image"


# ------------------------------------------------------------
# INPUT / OUTPUT FILES
# ------------------------------------------------------------

DASHBOARD_SPEC_FILE = BASE_DIR / "dashboard_spec.json"

# OPTIONAL
#
# If you have a team-specific dashboard reference image,
# place its path here.
#
# Example:
#
# REFERENCE_IMAGE = BASE_DIR / "finance_standard.png"
#
# If there is no reference image:
REFERENCE_IMAGE = None


OUTPUT_PROMPT_FILE = BASE_DIR / "visual_design_prompt.txt"

OUTPUT_CONFIG_FILE = BASE_DIR / "visual_design_config.json"

OUTPUT_IMAGE_FILE = BASE_DIR / "ai_design_concept.png"


# ============================================================
# CREATE VERTEX AI CLIENT
# ============================================================

def create_client():
    """
    Creates a Google Gen AI client configured to use Vertex AI.
    """

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
# LOAD DASHBOARD SPECIFICATION
# ============================================================

def load_dashboard_spec():

    if not DASHBOARD_SPEC_FILE.exists():

        raise FileNotFoundError(
            "\nDashboard specification not found:\n"
            f"{DASHBOARD_SPEC_FILE}\n\n"
            "Run dashboard_planner.py first."
        )

    with open(
        DASHBOARD_SPEC_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


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

            "unreadable text",

            "unnecessary empty space",

            "chart types that conflict with the dashboard specification"

        ]

    }


# ============================================================
# FORMAT KPIs
# ============================================================

def format_kpis(spec):

    kpis = spec.get("kpis", [])

    if not kpis:

        return "No KPI information was provided."

    formatted_kpis = []

    for index, kpi in enumerate(
        kpis,
        start=1
    ):

        if isinstance(kpi, dict):

            name = (

                kpi.get("name")

                or kpi.get("title")

                or kpi.get("label")

                or f"KPI {index}"

            )

            description = (

                kpi.get("description")

                or kpi.get("metric")

                or ""

            )

            text = f"{index}. {name}"

            if description:

                text += f" - {description}"

            formatted_kpis.append(text)

        else:

            formatted_kpis.append(
                f"{index}. {kpi}"
            )

    return "\n".join(
        formatted_kpis
    )


# ============================================================
# FORMAT CHARTS
# ============================================================

def format_charts(spec):

    charts = spec.get("charts", [])

    if not charts:

        return "No chart information was provided."

    formatted_charts = []

    for index, chart in enumerate(
        charts,
        start=1
    ):

        if isinstance(chart, dict):

            title = (

                chart.get("title")

                or chart.get("name")

                or f"Chart {index}"

            )

            chart_type = (

                chart.get("type")

                or chart.get("chart_type")

                or "Not specified"

            )

            x_axis = (

                chart.get("x_axis")

                or chart.get("x")

                or chart.get("dimension")

                or ""

            )

            y_axis = (

                chart.get("y_axis")

                or chart.get("y")

                or chart.get("measure")

                or ""

            )

            chart_text = (
                f"{index}. {title}\n"
                f"   Chart type: {chart_type}"
            )

            if x_axis:

                chart_text += (
                    f"\n   X-axis: {x_axis}"
                )

            if y_axis:

                chart_text += (
                    f"\n   Y-axis: {y_axis}"
                )

            formatted_charts.append(
                chart_text
            )

        else:

            formatted_charts.append(
                f"{index}. {chart}"
            )

    return "\n\n".join(
        formatted_charts
    )


# ============================================================
# FORMAT FILTERS
# ============================================================

def format_filters(spec):

    filters = spec.get("filters", [])

    if not filters:

        return "No filters were specified."

    formatted_filters = []

    for index, filter_item in enumerate(
        filters,
        start=1
    ):

        if isinstance(
            filter_item,
            dict
        ):

            name = (

                filter_item.get("name")

                or filter_item.get("field")

                or filter_item.get("dimension")

                or f"Filter {index}"

            )

            formatted_filters.append(
                f"{index}. {name}"
            )

        else:

            formatted_filters.append(
                f"{index}. {filter_item}"
            )

    return "\n".join(
        formatted_filters
    )


# ============================================================
# FORMAT VISUAL RULES
# ============================================================

def format_visual_rules(
    visual_standard
):

    rules = []

    rules.append(
        "OVERALL DESIGN:"
    )

    for rule in visual_standard[
        "overall_style"
    ]:

        rules.append(
            f"- {rule}"
        )

    rules.append("")

    rules.append(
        "LAYOUT:"
    )

    for rule in visual_standard[
        "layout"
    ]:

        rules.append(
            f"- {rule}"
        )

    rules.append("")

    rules.append(
        "KPI DESIGN:"
    )

    for rule in visual_standard[
        "kpi_cards"
    ]:

        rules.append(
            f"- {rule}"
        )

    rules.append("")

    rules.append(
        "CHART DESIGN:"
    )

    for rule in visual_standard[
        "charts"
    ]:

        rules.append(
            f"- {rule}"
        )

    rules.append("")

    rules.append(
        "FILTER DESIGN:"
    )

    for rule in visual_standard[
        "filters"
    ]:

        rules.append(
            f"- {rule}"
        )

    return "\n".join(
        rules
    )


# ============================================================
# FORMAT RESTRICTIONS
# ============================================================

def format_restrictions(
    visual_standard
):

    restrictions = []

    for item in visual_standard[
        "avoid"
    ]:

        restrictions.append(
            f"- {item}"
        )

    return "\n".join(
        restrictions
    )


# ============================================================
# BUILD VISUAL DESIGN PROMPT
# ============================================================

def build_visual_design_prompt(
    spec,
    visual_standard,
    reference_image_exists=False
):

    dashboard_title = (

        spec.get("dashboard_title")

        or spec.get("title")

        or "Business Performance Dashboard"

    )

    dashboard_description = (

        spec.get("description")

        or spec.get(
            "dashboard_description"
        )

        or ""

    )

    kpis = format_kpis(spec)

    charts = format_charts(spec)

    filters = format_filters(spec)

    visual_rules = format_visual_rules(
        visual_standard
    )

    restrictions = format_restrictions(
        visual_standard
    )


    # --------------------------------------------------------
    # REFERENCE IMAGE INSTRUCTIONS
    # --------------------------------------------------------

    if reference_image_exists:

        reference_instruction = """

A team-specific dashboard reference image is provided.

Use it as a VISUAL STYLE REFERENCE.

Analyze its:

- layout structure
- information hierarchy
- color palette
- KPI styling
- chart arrangement
- spacing
- alignment
- typography
- filter placement
- overall enterprise appearance

IMPORTANT:

Do NOT copy the exact business data, labels,
numbers or charts from the reference image.

The reference image determines HOW the dashboard
should look.

The dashboard specification determines WHAT
the dashboard must contain.
"""

    else:

        reference_instruction = """

No team-specific dashboard reference image
has been provided.

Create the dashboard using the dashboard
specification and visual design principles below.
"""


    # --------------------------------------------------------
    # MAIN PROMPT
    # --------------------------------------------------------

    prompt = f"""

You are an expert enterprise dashboard designer
and business intelligence visualization specialist.

Your task is to generate a realistic visual design
concept for a business dashboard.

{reference_instruction}


============================================================
DASHBOARD SPECIFICATION
============================================================

Dashboard Title:

{dashboard_title}


Dashboard Description:

{dashboard_description}


============================================================
REQUIRED KPIs
============================================================

{kpis}


============================================================
REQUIRED CHARTS
============================================================

{charts}


============================================================
REQUIRED FILTERS
============================================================

{filters}


============================================================
VISUAL DESIGN PRINCIPLES
============================================================

{visual_rules}


============================================================
RESTRICTIONS
============================================================

Avoid:

{restrictions}


============================================================
IMPORTANT REQUIREMENTS
============================================================

- Follow the dashboard specification exactly.
- Include all required KPI metrics.
- Use the required chart types.
- Include the required filters.
- Maintain strong information hierarchy.
- Keep the layout structured and easy to understand.
- Make the output look like a realistic business
  intelligence dashboard screenshot.
- Do not invent unrelated business metrics.
- Do not replace required charts with different chart types.
- Prioritize usability and analytical clarity.
- Keep the dashboard desktop-oriented.
- Use a professional enterprise analytics appearance.


============================================================
FINAL OUTPUT
============================================================

Generate ONE high-quality dashboard design image.

The result should look like a realistic screenshot
of a professional business intelligence dashboard.

The image must visually represent:

1. The dashboard title
2. Required KPIs
3. Required charts
4. Required filters
5. A logical analytical layout

This is a VISUAL DESIGN CONCEPT.

Do not generate a photograph.

Do not generate a mobile application.

Generate a polished enterprise analytics dashboard
interface.
"""

    return prompt.strip()


# ============================================================
# LOAD OPTIONAL REFERENCE IMAGE
# ============================================================

def load_reference_image():

    if REFERENCE_IMAGE is None:

        return None

    if not REFERENCE_IMAGE.exists():

        print()
        print(
            "WARNING:"
        )

        print(
            "Reference image path was configured "
            "but the file does not exist."
        )

        print(
            "Continuing without a reference image."
        )

        return None

    print()

    print(
        "Loading reference image:"
    )

    print(
        REFERENCE_IMAGE
    )

    image_bytes = (
        REFERENCE_IMAGE.read_bytes()
    )

    suffix = (
        REFERENCE_IMAGE.suffix
        .lower()
    )

    mime_types = {

        ".png": "image/png",

        ".jpg": "image/jpeg",

        ".jpeg": "image/jpeg",

        ".webp": "image/webp"

    }

    mime_type = mime_types.get(
        suffix,
        "image/png"
    )

    return Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )


# ============================================================
# GENERATE DASHBOARD IMAGE
# ============================================================

def generate_dashboard_image(
    prompt,
    reference_image_part=None
):

    print()

    print("=" * 60)

    print(
        "CONNECTING TO GEMINI IMAGE MODEL"
    )

    print("=" * 60)

    print()

    print(
        f"Project: {PROJECT_ID}"
    )

    print(
        f"Location: {LOCATION}"
    )

    print(
        f"Model: {IMAGE_MODEL}"
    )

    print()

    client = create_client()


    # --------------------------------------------------------
    # BUILD MULTIMODAL INPUT
    # --------------------------------------------------------

    if reference_image_part is not None:

        contents = [

            prompt,

            reference_image_part

        ]

        print(
            "Sending prompt + reference image..."
        )

    else:

        contents = prompt

        print(
            "Sending prompt..."
        )


    # --------------------------------------------------------
    # GENERATE IMAGE
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


    # --------------------------------------------------------
    # PROCESS RESPONSE
    # --------------------------------------------------------

    image_generated = False

    print()

    print(
        "Processing model response..."
    )

    print()

    for candidate in response.candidates:

        if not candidate.content:

            continue

        for part in candidate.content.parts:

            # ----------------------------------------------
            # TEXT RESPONSE
            # ----------------------------------------------

            if part.text:

                print(
                    "MODEL MESSAGE:"
                )

                print(
                    part.text
                )

                print()


            # ----------------------------------------------
            # IMAGE RESPONSE
            # ----------------------------------------------

            if part.inline_data:

                image_bytes = (
                    part.inline_data.data
                )

                image = Image.open(
                    BytesIO(
                        image_bytes
                    )
                )

                image.save(
                    OUTPUT_IMAGE_FILE
                )

                image_generated = True

                print(
                    "Dashboard image generated successfully!"
                )

                print(
                    f"Saved to:"
                )

                print(
                    OUTPUT_IMAGE_FILE
                )

                print()

                # Only save first generated image
                return OUTPUT_IMAGE_FILE


    # --------------------------------------------------------
    # NO IMAGE GENERATED
    # --------------------------------------------------------

    if not image_generated:

        raise RuntimeError(

            "The Gemini model returned a response, "
            "but no image was found.\n\n"

            "Check:\n"

            "1. The model name is available "
            "in your GCP project.\n"

            "2. Vertex AI API is enabled.\n"

            "3. Your account has permission "
            "to use the model.\n"

            "4. The model supports image generation."

        )


# ============================================================
# SAVE CONFIGURATION
# ============================================================

def save_visual_config(

    spec,

    visual_standard,

    prompt,

    reference_image_exists

):

    config = {

        "project_id": PROJECT_ID,

        "location": LOCATION,

        "image_model": IMAGE_MODEL,

        "dashboard_title": (

            spec.get(
                "dashboard_title"
            )

            or spec.get("title")

            or "Business Performance Dashboard"

        ),

        "reference_image_used":
            reference_image_exists,

        "reference_image": (

            str(REFERENCE_IMAGE)

            if reference_image_exists

            else None

        ),

        "output_image": str(
            OUTPUT_IMAGE_FILE
        ),

        "visual_standard":
            visual_standard,

        "generated_prompt":
            prompt

    }


    with open(

        OUTPUT_CONFIG_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            config,

            file,

            indent=4,

            ensure_ascii=False

        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()

    print("=" * 60)

    print(
        "AI VISUAL DESIGNER"
    )

    print("=" * 60)

    print()


    # --------------------------------------------------------
    # STEP 1: LOAD DASHBOARD SPEC
    # --------------------------------------------------------

    print(
        "STEP 1: Loading dashboard specification..."
    )

    spec = load_dashboard_spec()

    print(
        "Dashboard specification loaded successfully."
    )

    print()


    # --------------------------------------------------------
    # STEP 2: LOAD VISUAL RULES
    # --------------------------------------------------------

    print(
        "STEP 2: Loading visual design principles..."
    )

    visual_standard = (
        get_default_visual_standard()
    )

    print(
        "Visual design principles loaded."
    )

    print()


    # --------------------------------------------------------
    # STEP 3: LOAD OPTIONAL IMAGE
    # --------------------------------------------------------

    print(
        "STEP 3: Checking for optional reference image..."
    )

    reference_image_part = (
        load_reference_image()
    )

    reference_image_exists = (
        reference_image_part is not None
    )

    if reference_image_exists:

        print(
            "Reference image will be used."
        )

    else:

        print(
            "No reference image will be used."
        )

    print()


    # --------------------------------------------------------
    # STEP 4: BUILD PROMPT
    # --------------------------------------------------------

    print(
        "STEP 4: Building visual design prompt..."
    )

    prompt = (
        build_visual_design_prompt(

            spec=spec,

            visual_standard=visual_standard,

            reference_image_exists=
                reference_image_exists

        )
    )

    print(
        "Visual design prompt created successfully."
    )

    print()


    # --------------------------------------------------------
    # STEP 5: SAVE PROMPT
    # --------------------------------------------------------

    print(
        "STEP 5: Saving generated prompt..."
    )

    with open(

        OUTPUT_PROMPT_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(prompt)

    print(
        f"Prompt saved to:"
    )

    print(
        OUTPUT_PROMPT_FILE
    )

    print()


    # --------------------------------------------------------
    # STEP 6: SAVE CONFIG
    # --------------------------------------------------------

    save_visual_config(

        spec=spec,

        visual_standard=visual_standard,

        prompt=prompt,

        reference_image_exists=
            reference_image_exists

    )

    print(
        "Visual configuration saved successfully."
    )

    print()


    # --------------------------------------------------------
    # STEP 7: GENERATE IMAGE
    # --------------------------------------------------------

    print(
        "STEP 6: Generating AI dashboard image..."
    )

    output_path = (
        generate_dashboard_image(

            prompt=prompt,

            reference_image_part=
                reference_image_part

        )
    )


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "AI DASHBOARD DESIGN GENERATED SUCCESSFULLY"
    )

    print("=" * 60)

    print()

    print(
        f"Model used: {IMAGE_MODEL}"
    )

    print()

    print(
        f"Generated image:"
    )

    print(
        output_path
    )

    print()

    print(
        "PIPELINE:"
    )

    print()

    print(
        "dashboard_spec.json"
    )

    print(
        "        +"
    )

    print(
        "optional reference image"
    )

    print(
        "        ↓"
    )

    print(
        "visual_designer.py"
    )

    print(
        "        ↓"
    )

    print(
        IMAGE_MODEL
    )

    print(
        "        ↓"
    )

    print(
        "ai_design_concept.png"
    )

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()

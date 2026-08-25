# =========================================================
# DASHBOARD SUMMARIZER
# =========================================================

def generate_dashboard_summary(dashboard_spec):

    dashboard_title = dashboard_spec.get(
        "dashboard_title",
        "Dashboard"
    )

    sheets = dashboard_spec.get(
        "sheets",
        []
    )


    # =====================================================
    # START SUMMARY
    # =====================================================

    summary = (
        f"This dashboard, '{dashboard_title}', "
        f"contains {len(sheets)} sheet(s).\n\n"
    )


    # =====================================================
    # DESCRIBE EACH SHEET
    # =====================================================

    for sheet in sheets:

        sheet_number = sheet.get(
            "sheet_number",
            ""
        )

        title = sheet.get(
            "title",
            "Untitled Sheet"
        )

        purpose = sheet.get(
            "purpose",
            ""
        )

        summary += (
            f"Sheet {sheet_number}: {title}\n"
        )


        # ---------------------------------------------
        # PURPOSE
        # ---------------------------------------------

        if purpose:

            summary += (
                f"Purpose: {purpose}\n"
            )


        # ---------------------------------------------
        # KPIs
        # ---------------------------------------------

        kpis = sheet.get(
            "kpis",
            []
        )

        if kpis:

            kpi_names = []

            for kpi in kpis:

                kpi_names.append(
                    kpi.get(
                        "title",
                        "Unnamed KPI"
                    )
                )

            summary += (
                "KPIs: "
                + ", ".join(kpi_names)
                + "\n"
            )


        # ---------------------------------------------
        # CHARTS
        # ---------------------------------------------

        charts = sheet.get(
            "charts",
            []
        )

        if charts:

            chart_descriptions = []

            for chart in charts:

                chart_title = chart.get(
                    "title",
                    "Unnamed Chart"
                )

                chart_type = chart.get(
                    "type",
                    "chart"
                )

                chart_descriptions.append(
                    f"{chart_title} ({chart_type})"
                )

            summary += (
                "Charts: "
                + ", ".join(chart_descriptions)
                + "\n"
            )


        # ---------------------------------------------
        # FILTERS
        # ---------------------------------------------

        filters = sheet.get(
            "filters",
            []
        )

        if filters:

            summary += (
                "Filters: "
                + ", ".join(filters)
                + "\n"
            )


        # ADD SPACE BETWEEN SHEETS

        summary += "\n"


    # =====================================================
    # RETURN SUMMARY
    # =====================================================

    return summary

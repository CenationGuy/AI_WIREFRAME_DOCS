cat > test_rag_planner.py <<'EOF'
import pandas as pd

from csv_profiler import profile_csv_dataframe
from rag.Sac_rag import retrieve_sac_standards
from dashboard_planner import create_dashboard_plan


# ============================================================
# STEP 1: LOAD TEST CSV
# ============================================================

print("\n============================================")
print("TEST: CSV → RAG → PLANNER")
print("============================================")

df = pd.read_csv("test_dashboard.csv")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# STEP 2: PROFILE CSV
# ============================================================

print("\n============================================")
print("STEP 1: CSV PROFILING")
print("============================================")

data_profile = profile_csv_dataframe(df)

print("CSV profiling completed.")


# ============================================================
# STEP 3: RETRIEVE SAC STANDARDS
# ============================================================

print("\n============================================")
print("STEP 2: SAC RAG RETRIEVAL")
print("============================================")

sac_query = (
    "Enterprise dashboard design standards "
    "for KPI boxes, KPI selection, charts, "
    "filters, layout, visual hierarchy, "
    "colours, interaction, navigation, "
    "screen estate and dashboard usability."
)

sac_standards = retrieve_sac_standards(
    sac_query,
    top_k=5
)

print(
    f"Retrieved {len(sac_standards)} "
    "SAC standard chunks."
)


# ============================================================
# STEP 4: CREATE DASHBOARD PLAN
# ============================================================

print("\n============================================")
print("STEP 3: DASHBOARD PLANNER")
print("============================================")

dashboard_spec = create_dashboard_plan(
    data_profile,
    sac_standards
)

print("\nDashboard plan generated successfully.")

print("\n============================================")
print("DASHBOARD SPECIFICATION")
print("============================================")

print(
    dashboard_spec
)


# ============================================================
# COMPLETE
# ============================================================

print("\n============================================")
print("CSV → RAG → PLANNER TEST COMPLETE")
print("============================================")
EOF

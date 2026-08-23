import json


# =========================================================
# LOAD DATA PROFILE
# =========================================================

PROFILE_FILE = "data_profile.json"

with open(PROFILE_FILE, "r") as file:
    data_profile = json.load(file)


print("DATA PROFILE LOADED SUCCESSFULLY\n")

print("Dimensions:")
print(data_profile["dimensions"])

print("\nDate dimensions:")
print(data_profile["date_dimensions"])

print("\nMeasures:")
print(data_profile["measures"])

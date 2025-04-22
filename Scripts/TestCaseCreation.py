# *** Do Not Run This Script Multiple Times ***

import requests
from requests.auth import HTTPBasicAuth

# === CONFIG ===
AZURE_ORG = "mnaffuad"
PROJECT = "RobotArmSimulator"
PAT = "vwtc3wCN9fVXkZrVVYzlO3UgwV7fsOBeLGVC944uoKcOGn9afSy2JQQJ99BDACAAAAAAAAAAAAASAZDO3kGb"
PLAN_ID = 1
SUITE_ID = 2

BASE_URL = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis"
HEADERS = {
    "Content-Type": "application/json-patch+json"
}
AUTH = HTTPBasicAuth("", PAT)

# === Test Case Names ===
test_cases = [f"Test{str(i).zfill(2)}" for i in range(1, 21)]  # Test01 to Test20

for title in test_cases:
    # Step 1: Create Test Case Work Item
    create_url = f"{BASE_URL}/wit/workitems/$Test%20Case?api-version=7.1-preview.3"
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        }
    ]

    response = requests.post(create_url, headers=HEADERS, json=payload, auth=AUTH)

    if response.status_code in [200, 201]:
        test_case_id = response.json()["id"]
        print(f"[✔] Created test case: {title} (ID: {test_case_id})")

        # Step 2: Add Test Case to Suite
        add_url = f"{BASE_URL}/test/plans/{PLAN_ID}/suites/{SUITE_ID}/testcases/{test_case_id}?api-version=7.1-preview.3"
        suite_response = requests.post(add_url, auth=AUTH)

        if suite_response.status_code == 200:
            print(f"   → Added to suite {SUITE_ID}")
        else:
            print(f"   [!] Failed to add to suite: {suite_response.status_code} - {suite_response.text}")
    else:
        print(f"[!] Failed to create {title}: {response.status_code} - {response.text}")

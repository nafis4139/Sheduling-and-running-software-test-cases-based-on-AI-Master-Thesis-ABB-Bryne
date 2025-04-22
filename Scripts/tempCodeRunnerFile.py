import requests
from requests.auth import HTTPBasicAuth

# === CONFIG ===
org_url = "https://dev.azure.com/YOUR_ORG"
project = "YOUR_PROJECT"
pat = "YOUR_PERSONAL_ACCESS_TOKEN"
plan_id = 123           # Your Test Plan ID
suite_id = 456          # Your Test Suite ID

# List of test case names to match your RoboTests.cs methods
test_cases = [f"Test{str(i).zfill(2)}" for i in range(1, 21)]  # Test01 to Test20

# === HEADERS ===
headers = {
    "Content-Type": "application/json-patch+json"
}
auth = HTTPBasicAuth("", pat)

for title in test_cases:
    # Step 1: Create test case work item
    create_url = f"{org_url}/{project}/_apis/wit/workitems/$Test%20Case?api-version=7.1-preview.3"
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title
        }
    ]

    response = requests.post(create_url, headers=headers, json=payload, auth=auth)
    if response.status_code in [200, 201]:
        test_case_id = response.json()["id"]
        print(f"[✔] Created test case: {title} (ID: {test_case_id})")

        # Step 2: Add to Test Suite
        add_url = f"{org_url}/{project}/_apis/test/plans/{plan_id}/suites/{suite_id}/testcases/{test_case_id}?api-version=7.1-preview.3"
        suite_response = requests.post(add_url, auth=auth)
        if suite_response.status_code == 200:
            print(f"   → Added to suite {suite_id}")
        else:
            print(f"   [!] Failed to add to suite: {suite_response.status_code} - {suite_response.text}")
    else:
        print(f"[!] Failed to create {title}: {response.status_code} - {response.text}")

import requests
from requests.auth import HTTPBasicAuth

# === CONFIG ===
AZURE_ORG = "mnaffuad"
PROJECT = "RobotArmSimulator"
PAT = "vwtc3wCN9fVXkZrVVYzlO3UgwV7fsOBeLGVC944uoKcOGn9afSy2JQQJ99BDACAAAAAAAAAAAAASAZDO3kGb"

BASE_URL = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis"
HEADERS = {
    "Content-Type": "application/json-patch+json"
}
AUTH = HTTPBasicAuth("", PAT)

# === ID to New Title Mapping ===
rename_map = {
    3:  "Test01 {Autobot1}", 
    4:  "Test02 {Autobot2}",
    5:  "Test03 {Autobot1,Autobot2}",
    6:  "Test04 {Autobot1}",
    7:  "Test05 {Autobot3}",
    8:  "Test06 {Autobot1,Autobot3}",
    9:  "Test07 {Autobot2,Autobot3}",
    10: "Test08 {Autobot1,Autobot2,Autobot3}",
    11: "Test09 {Autobot3}",
    12: "Test10 {Autobot1}",
    13: "Test11 {Autobot2}",
    14: "Test12 {Autobot1,Autobot2}",
    15: "Test13 {Autobot3}",
    16: "Test14 {Autobot1,Autobot3}",
    17: "Test15 {Autobot2,Autobot3}",
    18: "Test16 {Autobot1}",
    19: "Test17 {Autobot2}",
    20: "Test18 {Autobot3}",
    21: "Test19 {Autobot1,Autobot2}",
    22: "Test20 {Autobot1,Autobot2,Autobot3}"
}

# === PATCH each Test Case Title ===
for work_item_id, new_title in rename_map.items():
    url = f"{BASE_URL}/wit/workitems/{work_item_id}?api-version=7.1-preview.3"
    payload = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": new_title
        }
    ]

    response = requests.patch(url, headers=HEADERS, json=payload, auth=AUTH)

    if response.status_code in [200, 201]:
        print(f"[✔] Renamed TestCase #{work_item_id} to '{new_title}'")
    else:
        print(f"[!] Failed to rename TestCase #{work_item_id}: {response.status_code} - {response.text}")

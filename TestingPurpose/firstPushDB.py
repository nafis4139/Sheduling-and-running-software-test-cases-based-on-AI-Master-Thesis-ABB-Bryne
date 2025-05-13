from azure.cosmos import CosmosClient, PartitionKey
import requests
import uuid
import base64

# Azure DevOps config
AZURE_ORG = "mnaffuad"
PROJECT = "RobotArmSimulator"  
PAT = "vwtc3wCN9fVXkZrVVYzlO3UgwV7fsOBeLGVC944uoKcOGn9afSy2JQQJ99BDACAAAAAAAAAAAAASAZDO3kGb" 
# Encode PAT for authentication
auth_str = f":{PAT}".encode("utf-8")
auth_b64 = base64.b64encode(auth_str).decode("utf-8")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_b64}"
}

# Cosmos DB config
COSMOS_ENDPOINT = "https://nafis.documents.azure.com:443/"
COSMOS_KEY = "X4heNu62D2RSqzqP0p3ZpJC3YVZ4PwsGxwnIfmybcnMwhsqqjQX79Bx2Mlcsqmz15eJaj5gxbbwWACDbWGVOCw=="
DATABASE_NAME = "TestResultsDB"
CONTAINER_NAME = "Results"

# Connect to Cosmos DB
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
db = client.create_database_if_not_exists(id=DATABASE_NAME)
container = db.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/testCaseId"),
    offer_throughput=400
)

def upload_test_results(run_id):
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/Runs/{run_id}/results?api-version=7.1"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        results = response.json().get("value", [])
        for result in results:
            doc = {
                "id": str(uuid.uuid4()),
                "runId": run_id,
                "testCaseId": result.get("testCase", {}).get("id"),
                "testCaseName": result.get("testCase", {}).get("name"),
                "outcome": result.get("outcome"),
                "durationInMs": result.get("durationInMs"),
                "agent": result.get("computerName"),
                "completedDate": result.get("completedDate"),
                "buildId": result.get("build", {}).get("id")
            }
            container.upsert_item(doc)
        print(f"✔ Uploaded {len(results)} results for Test Run ID {run_id}")
    else:
        print(f"❌ Failed to fetch results for run {run_id}: {response.status_code}")
        print(response.text)

# ✅ Example usage
run_ids = [52,53]  # Update with actual run IDs from your test history
for run_id in run_ids:
    upload_test_results(run_id)

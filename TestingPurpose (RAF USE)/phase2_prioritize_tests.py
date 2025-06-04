from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime
import os

# Cosmos DB configuration
COSMOS_URI = "https://nafis.documents.azure.com:443/"
COSMOS_KEY = "X4heNu62D2RSqzqP0p3ZpJC3YVZ4PwsGxwnIfmybcnMwhsqqjQX79Bx2Mlcsqmz15eJaj5gxbbwWACDbWGVOCw=="
COSMOS_DB = "TestResultsDB"
COSMOS_CONTAINER = "testRuns"

# Connect to Cosmos DB
client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
container = client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

# Fetch all items from Cosmos DB
query = "SELECT * FROM c"
items = list(container.query_items(query=query, enable_cross_partition_query=True))
df = pd.DataFrame(items)

# Flatten and preprocess fields
df["testCaseId"] = df["testCase"].apply(lambda x: x.get("id") if isinstance(x, dict) else None)
df["testCaseTitle"] = df["testCase"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
df["uploadTimestamp"] = pd.to_datetime(df["uploadTimestamp"], errors="coerce")
df["durationInSec"] = df["durationInMs"] / 1000

# Drop rows missing required fields
df = df.dropna(subset=["testCaseId", "outcome", "uploadTimestamp", "durationInSec"])
df["testCaseId"] = df["testCaseId"].astype(int)

# Aggregate base stats
agg = df.groupby(['testCaseId', 'testCaseTitle']).agg(
    nRuns=('outcome', 'count'),
    nFail=('outcome', lambda x: (x == 'Failed').sum()),
    nPass=('outcome', lambda x: (x == 'Passed').sum()),
    avgTime=('durationInSec', 'mean'),
    last_run=('uploadTimestamp', 'max')
).reset_index()

# Add last run outcome
df_sorted = df.sort_values(by='uploadTimestamp', ascending=False)
last_outcome = df_sorted.drop_duplicates(subset='testCaseId', keep='first')[['testCaseId', 'outcome']]
last_outcome = last_outcome.rename(columns={"outcome": "lastOutcome"})
agg = agg.merge(last_outcome, on="testCaseId", how="left")

# Calculate priority score
agg["normalizedTime"] = (agg["avgTime"] - agg["avgTime"].min()) / (agg["avgTime"].max() - agg["avgTime"].min())
agg["priorityScore"] = (
    agg["nFail"] * 5 +                         # Frequent failures
    agg["normalizedTime"] * 1 +                # Expensive test time
    agg["lastOutcome"].apply(lambda x: 10 if x == "Failed" else 0)  # Recent failure is urgent
)

# Sort by priority
agg = agg.sort_values(by="priorityScore", ascending=False)

# Format timestamp for export
agg["last_run"] = agg["last_run"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Save to CSV
os.makedirs("CosmosDB", exist_ok=True)
priority_file = "CosmosDB/test_priority_summary.csv"
agg.to_csv(priority_file, index=False)

# Display result
print("\n📊 Prioritized Test Case Summary:")
with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(agg)

print(f"\n✅ Prioritized CSV saved to: {priority_file}")

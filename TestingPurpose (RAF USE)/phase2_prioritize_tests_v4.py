from azure.cosmos import CosmosClient
import pandas as pd
from datetime import datetime
import os

# Cosmos DB configuration
COSMOS_URI = "https://nafis.documents.azure.com:443/"
COSMOS_KEY = "X4heNu62D2RSqzqP0p3ZpJC3YVZ4PwsGxwnIfmybcnMwhsqqjQX79Bx2Mlcsqmz15eJaj5gxbbwWACDbWGVOCw=="
COSMOS_DB = "TestResultsDB"
COSMOS_CONTAINER = "testRuns"

# Load last sync time
os.makedirs("CosmosDB", exist_ok=True)
sync_file = "CosmosDB/last_sync.txt"
if os.path.exists(sync_file):
    with open(sync_file, "r") as f:
        last_sync = f.read().strip()
else:
    last_sync = "2020-01-01T00:00:00Z"

# Connect to Cosmos DB
client = CosmosClient(COSMOS_URI, credential=COSMOS_KEY)
container = client.get_database_client(COSMOS_DB).get_container_client(COSMOS_CONTAINER)

# Fetch new items only
query = f"SELECT * FROM c WHERE c.uploadTimestamp > '{last_sync}'"
items = list(container.query_items(query=query, enable_cross_partition_query=True))
print(f"\n📥 New records fetched: {len(items)}")

# Convert to DataFrame
if items:
    df_new = pd.DataFrame(items)
    df_new["testCaseId"] = df_new["testCase"].apply(lambda x: x.get("id") if isinstance(x, dict) else None)
    df_new["testCaseTitle"] = df_new["testCase"].apply(lambda x: x.get("name") if isinstance(x, dict) else None)
    df_new["uploadTimestamp"] = pd.to_datetime(df_new["uploadTimestamp"], errors="coerce")
    df_new["durationInSec"] = df_new["durationInMs"] / 1000
    df_new = df_new.dropna(subset=["testCaseId", "outcome", "uploadTimestamp", "durationInSec"])
    df_new["testCaseId"] = df_new["testCaseId"].astype(int)
else:
    df_new = pd.DataFrame()

# Load full dataset (from cache)
cached_file = "CosmosDB/test_results_all.csv"
if os.path.exists(cached_file):
    df_all = pd.read_csv(cached_file, parse_dates=["uploadTimestamp"])
    if not df_new.empty:
        df_all = pd.concat([df_all, df_new], ignore_index=True)
else:
    df_all = df_new

# Save updated cache
if not df_all.empty:
    df_all.to_csv(cached_file, index=False)

# Save latest timestamp for next run
if not df_all.empty:
    latest_time = df_all["uploadTimestamp"].max().isoformat()
    with open(sync_file, "w") as f:
        f.write(latest_time)

# ---------- PRIORITY CALCULATION ----------

# Aggregate base stats
agg = df_all.groupby(['testCaseId', 'testCaseTitle']).agg(
    nRuns=('outcome', 'count'),
    nFail=('outcome', lambda x: (x == 'Failed').sum()),
    nPass=('outcome', lambda x: (x == 'Passed').sum()),
    avgTime=('durationInSec', 'mean'),
    last_run=('uploadTimestamp', 'max')
).reset_index()

# Add last run outcome
df_sorted = df_all.sort_values(by='uploadTimestamp', ascending=False)
last_outcome = df_sorted.drop_duplicates(subset='testCaseId', keep='first')[['testCaseId', 'outcome']]
last_outcome = last_outcome.rename(columns={"outcome": "lastOutcome"})
agg = agg.merge(last_outcome, on="testCaseId", how="left")

# Priority score logic
now = pd.Timestamp.now()

# Add derived features
agg["daysSinceLastRun"] = (now - pd.to_datetime(agg["last_run"])).dt.days
agg["failRate"] = agg["nFail"] / agg["nRuns"] # Failure rate: 0.0 (no fails) to 1.0 (always fails), scaled
agg["recentFailureBoost"] = agg["lastOutcome"].apply(lambda x: 1 if x == "Failed" else 0) # Recent failure bonus: 1 if last failed, else 0

# Normalize average time to [0,1]
agg["normalizedTime"] = (
    (agg["avgTime"] - agg["avgTime"].min()) /
    (agg["avgTime"].max() - agg["avgTime"].min())
).fillna(0)

# Normalize recency: more stale = higher value
agg["recencyScore"] = (
    agg["daysSinceLastRun"] / agg["daysSinceLastRun"].max()
).fillna(0)

# Final priority score [0–1], tunable weights
agg["priorityScore"] = (
    0.4 * agg["failRate"] +
    0.2 * agg["normalizedTime"] +
    0.3 * agg["recentFailureBoost"] +
    0.1 * agg["recencyScore"]
)

agg = agg.sort_values(by="priorityScore", ascending=False)
agg["last_run"] = agg["last_run"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Save priority results
priority_file = "CosmosDB/test_priority_summary.csv"
agg.to_csv(priority_file, index=False)

# Display result
print("\n📊 Prioritized Test Case Summary:")
with pd.option_context("display.max_rows", None, "display.max_columns", None):
    print(agg)

print(f"\n✅ Priority CSV saved to: {priority_file}")

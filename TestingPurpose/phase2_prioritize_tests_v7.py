# Download a JSON File
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from azure.cosmos import CosmosClient


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

# Save full raw data to JSON file from Cosmos DB
query = "SELECT * FROM c"
items = list(container.query_items(query=query, enable_cross_partition_query=True))
print(f"\n📥 Records fetched: {len(items)}")
with open("CosmosDB/raw_cosmos_dump.json", "w", encoding="utf-8") as f:
    import json
    json.dump(items, f, indent=2, ensure_ascii=False)

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


# Prepare features
df = df_all.dropna(subset=["testCaseId", "outcome", "durationInSec", "uploadTimestamp"])
df["testCaseId"] = df["testCaseId"].astype(int)

# Create features for each test case
agg = df.groupby("testCaseId").agg(
    nRuns=('outcome', 'count'),
    nFail=('outcome', lambda x: (x == 'Failed').sum()),
    nPass=('outcome', lambda x: (x == 'Passed').sum()),
    avgTime=('durationInSec', 'mean'),
    lastRun=('uploadTimestamp', 'max'),
).reset_index()

# Compute derived features
now = pd.Timestamp.now()
agg["failRate"] = agg["nFail"] / agg["nRuns"]
agg["recency"] = (now - agg["lastRun"]).dt.total_seconds() / 3600  # hours since last run
# Normalize avgTime and recency
agg["normTime"] = (agg["avgTime"] - agg["avgTime"].min()) / (agg["avgTime"].max() - agg["avgTime"].min())
agg["normRecency"] = (agg["recency"] - agg["recency"].min()) / (agg["recency"].max() - agg["recency"].min())

# Normalize features
scaler = MinMaxScaler()
features = scaler.fit_transform(agg[["failRate", "avgTime", "recency"]])

# Set up Q-table
n_states = len(agg)
n_actions = 2  # 0 = skip, 1 = run
Q_table = np.zeros((n_states, n_actions))

# Rewards based on outcome history
reward_lookup = {}


# Define reward lookup with weighted features
# Total weight = 1.0, split by priority
weight_failRate = 0.5
weight_recency  = 0.3
weight_time     = 0.2

reward_lookup = {
    row["testCaseId"]: (
        weight_failRate * row["failRate"] +
        weight_recency  * row["normRecency"] +
        weight_time     * row["normTime"]
    )
    for _, row in agg.iterrows()
}

# Q-learning parameters
alpha = 0.1
gamma = 0.9
epsilon = 0.1
episodes = 500

# Train Q-table
for _ in range(episodes):
    for i in range(n_states):
        test_id = agg.loc[i, "testCaseId"]
        reward = reward_lookup.get(test_id, 0)

        for action in [0, 1]:  # 0 = skip, 1 = run
            old_value = Q_table[i, action]
            next_max = Q_table[i].max()

            # If action is "run", assign real reward; else small penalty
            r = reward if action == 1 else -0.1

            new_value = (1 - alpha) * old_value + alpha * (r + gamma * next_max)
            Q_table[i, action] = new_value

# Select best action for each test case
best_actions = Q_table.argmax(axis=1)
agg["runDecision"] = best_actions
agg["Q_value"] = Q_table[np.arange(n_states), best_actions]

# Only return those marked for "run"
selected_tests = agg[agg["runDecision"] == 1]

# Add back testCaseTitle for reference
titles = df[["testCaseId", "testCaseTitle"]].drop_duplicates("testCaseId")
selected_tests = selected_tests.merge(titles, on="testCaseId", how="left")

# Sort by Q_value (descending)
selected_tests = selected_tests.sort_values(by="Q_value", ascending=False)

# Save to CSV
selected_tests.to_csv("CosmosDB/scheduled_tests_qlearning.csv", index=False)

# Show output
print("\n📊 Q-Learning Selected Test Cases:")
print(selected_tests[["testCaseId", "testCaseTitle", "Q_value", "failRate", "avgTime", "recency"]])

print("\n✅ Saved to: CosmosDB/scheduled_tests_qlearning.csv")

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

# Discretize features for state mapping
agg["state_fail"] = pd.qcut(agg["failRate"], q=4, labels=False, duplicates='drop')
agg["state_recency"] = pd.qcut(agg["recency"], q=4, labels=False, duplicates='drop')
agg["state_time"] = pd.qcut(agg["avgTime"], q=4, labels=False, duplicates='drop')

# Combine into a single state string and map to integer
agg["state_index"] = (
    agg["state_fail"].astype(str) + "-" +
    agg["state_recency"].astype(str) + "-" +
    agg["state_time"].astype(str)
)
state_mapping = {s: i for i, s in enumerate(agg["state_index"].unique())}
agg["state_index"] = agg["state_index"].map(state_mapping)

# Q-learning setup
n_states = len(state_mapping)
n_actions = 2  # 0 = skip, 1 = run
Q_table = np.zeros((n_states, n_actions))

# Reward function
reward_lookup = {
    row["testCaseId"]: (
        0.5 * row["failRate"] +
        0.3 * row["normRecency"] +
        0.2 * row["normTime"]
    )
    for _, row in agg.iterrows()
}

# Q-learning hyperparameters
alpha = 0.1
gamma = 0.9
epsilon = 0.1
episodes = 500

# Train Q-table
for _ in range(episodes):
    for _, row in agg.iterrows():
        s = row["state_index"]
        test_id = row["testCaseId"]
        reward = reward_lookup.get(test_id, 0)

        for a in [0, 1]:
            if np.random.rand() < epsilon:
                chosen_action = np.random.choice([0, 1])
            else:
                chosen_action = np.argmax(Q_table[s])
            old_value = Q_table[s, a]
            next_max = Q_table[s].max()
            r = reward if a == 1 else -0.1
            Q_table[s, a] = (1 - alpha) * old_value + alpha * (r + gamma * next_max)

# Apply learned policy
agg["runDecision"] = agg["state_index"].apply(lambda s: np.argmax(Q_table[s]))
agg["Q_value"] = agg.apply(lambda row: Q_table[row["state_index"], row["runDecision"]], axis=1)

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

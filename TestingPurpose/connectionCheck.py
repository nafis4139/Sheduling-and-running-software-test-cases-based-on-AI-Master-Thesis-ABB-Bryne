from azure.cosmos import CosmosClient

# Replace these with your actual values
endpoint = "https://nafis.documents.azure.com:443/"
key = "X4heNu62D2RSqzqP0p3ZpJC3YVZ4PwsGxwnIfmybcnMwhsqqjQX79Bx2Mlcsqmz15eJaj5gxbbwWACDbWGVOCw=="

client = CosmosClient(endpoint, key)
database = client.get_database_client("TestResultsDB")
container = database.get_container_client("Results")

for item in container.read_all_items():
    print(item)

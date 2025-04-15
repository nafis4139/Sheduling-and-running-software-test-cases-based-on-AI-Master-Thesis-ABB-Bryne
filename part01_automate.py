### Create Two Seperate Test Runs for Different TestCases based on Agents ✅
### Trigger Two Release ✅
### Launch Different Stages in Each Release ✅
### Use Different Agents for Different Stages ✅

import requests
import json
import base64
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()  # Loads the variables from .env into the environment


# Fake Historical Data (Test Case ID: 21-26)
historical_data = {
    6: {"test_case_id": 21, "execution_time": 50, "pass_rate": 50},  # Test Point ID: 6 -> Test Case ID: 21
    7: {"test_case_id": 22, "execution_time": 40, "pass_rate": 70},  # Test Point ID: 7 -> Test Case ID: 22
    8: {"test_case_id": 23, "execution_time": 10, "pass_rate": 95},  # Test Point ID: 8 -> Test Case ID: 23
    9: {"test_case_id": 24, "execution_time": 80, "pass_rate": 20},  # Test Point ID: 9 -> Test Case ID: 24
    10: {"test_case_id": 25, "execution_time": 10, "pass_rate": 100}, # Test Point ID: 10 -> Test Case ID: 25
    11: {"test_case_id": 26, "execution_time": 25, "pass_rate": 75}, # Test Point ID: 11 -> Test Case ID: 26
}

# Azure DevOps Configuration
AZURE_ORG = "bmnafisfuad14"
PROJECT = "ShoppingCart"  
PAT = os.getenv("GITHUB_PAT") 
SUITE_ID = 20
POOL_ID = 12

# Encode PAT for authentication 
auth_str = f":{PAT}".encode("utf-8")
auth_b64 = base64.b64encode(auth_str).decode("utf-8")
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_b64}"
}

BASE_URL = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis"

# Add a utility to get environment variables from a release
def get_release_environments(release_id):
    url = f"https://vsrm.dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/release/releases/{release_id}?api-version=7.1-preview.7"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("environments", [])
    else:
        print(f"Failed to get environments for release {release_id}")
        return []

# Cancel environment if needed
def cancel_environment(release_id, environment_id):
    url = f"https://vsrm.dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/release/releases/{release_id}/environments/{environment_id}?api-version=7.1-preview.7"
    payload = {"status": "canceled"}
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Canceled environment {environment_id} of release {release_id}")
    else:
        print(f"Failed to cancel environment {environment_id}: {response.status_code}")
        

### Stage
def deploy_environment(release_id, environment_id, stage_name):
    url = f"https://vsrm.dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/release/releases/{release_id}/environments/{environment_id}?api-version=7.1-preview.7"
    payload = {"status": "inProgress"}  # To start manual deployment
    response = requests.patch(url, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Starting Stage '{stage_name}' (Environment ID: {environment_id}) for Release ID: {release_id}")
    else:
        print(f"❌ Failed to start environment {environment_id} (Stage: '{stage_name}'): {response.status_code}")

### 1. Fetch Test Plan ID
def get_test_plan():
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/testplan/plans?api-version=7.1-preview.1"
    print("Test Plan API:", url)
    response = requests.get(url, headers=HEADERS).json()

    print("Available Test Plans:")
    for plan in response.get("value", []):
        print(f"✔ Test Plan Name: {plan['name']} (ID: {plan['id']})")

    # Selecting a specific test plan
    for plan in response.get("value", []):
        if plan["name"] == "ShoppingCart_TP":  # Test Plan Name
            print(f"Using Test Plan: {plan['name']} (ID: {plan['id']})")
            return plan["id"]

    print("❌ Test Plan not found!")
    return None

### 2. Fetch Test Suite ID
def get_test_suite(test_plan_id):
    """ Fetches and prints available Test Suites for a given Test Plan, selecting the correct one """
    url = f"{BASE_URL}/testplan/plans/{test_plan_id}/suites?api-version=7.1-preview.1"
    print("Test Suite API:", url)
    response = requests.get(url, headers=HEADERS).json()

    print("Available Test Suites:")
    test_suite_id = None 

    for suite in response.get("value", []):
        print(f"✔ Test Suite Name: {suite['name']} (ID: {suite['id']})")

        # Test Suite ID : 20 (Declared in the beginning)
        if suite["id"] == SUITE_ID:  
            test_suite_id = suite["id"]
            selected_suite_name = suite["name"]

    if test_suite_id:
        print(f"Using Test Suite: {selected_suite_name} (ID: {test_suite_id})")
        return test_suite_id
    else:
        print("❌ Test Suite with ID 20 not found! Please check Azure DevOps setup.")
        return None

### 3. Fetch Test Case IDs
def get_test_cases(test_plan_id, test_suite_id):
    """ Fetches all test cases inside a given Test Suite and prints them. """
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/Plans/{test_plan_id}/Suites/{test_suite_id}/TestCases?api-version=7.1"
    print("Test Case API:", url)
    response = requests.get(url, headers=HEADERS)

    #print("Status Code:", response.status_code)
    #print("Response Text:", response.text)  # Debugging output

    if response.status_code == 200:
        response_json = response.json()
        test_case_ids = [tc["testCase"]["id"] for tc in response_json.get("value", [])]

        if test_case_ids:
            print("Available Test Case IDs:", test_case_ids)
        else:
            print("⚠ No test cases found in this test suite!")

        return test_case_ids

    elif response.status_code == 404:
        print("❌ Error: Test Suite or Test Cases not found. Check if this suite contains test cases.")
    elif response.status_code == 401:
        print("❌ Error: Unauthorized. Check your PAT permissions.")
    else:
        print(f"❌ Unexpected Error: {response.status_code} - {response.text}")

    return []

### 4. Fetch Test Cases Names and Point IDs
def get_test_points(test_plan_id, test_suite_id, silent=False):
    """ Fetches test point IDs along with test case names, IDs, and assigned agent names. """
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/plans/{test_plan_id}/suites/{test_suite_id}/points?api-version=7.0"

    if not silent:
        print(f"Test Point API: {url}")
    
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        test_points = {}  # Dictionary: {test_point_id: (test_case_id, test_case_name, assigned_agents)}
        test_point_ids = []  # List of all test point IDs

        for point in response.json().get("value", []):
            test_case_id = point.get("testCase", {}).get("id", "Unknown Test Case ID")
            test_case_name = point.get("testCase", {}).get("name", "Unknown Test Case")
            test_point_id = point.get("id")

            # Extract all agent names within {} and split by comma
            assigned_agents = []
            if "{" in test_case_name and "}" in test_case_name:
                start = test_case_name.index("{") + 1
                end = test_case_name.index("}")
                assigned_agents = [agent.strip() for agent in test_case_name[start:end].split(",")]

            # Store as {point_id: (test_case_id, test_case_name, assigned_agents)}
            test_points[test_point_id] = (test_case_id, test_case_name, assigned_agents)
            test_point_ids.append(test_point_id)  # Add ID to list

        if not silent and test_points:
            print("Available Test Cases:")
            for point_id, (case_id, case_name, agents) in test_points.items():
                agents_str = ", ".join(agents) if agents else "Unassigned"
                print(f"✔ Test Case ID: {case_id}; Point ID: {point_id}; Case Name: {case_name}; Assigned Agents: {agents_str}")
        
        return test_points, test_point_ids  # Return both dictionary & list

    if not silent:
        print(f"❌ Failed to fetch test points. Status Code: {response.status_code}")
        print("Response:", response.text)

    return {}, []  # Return empty dictionary & list if failed

### 5. Fetch Agent Availability
def get_agent_pool(pool_id):
    """ Fetches all available agent pools and identifies the one being used. """
    url = f"https://dev.azure.com/{AZURE_ORG}/_apis/distributedtask/pools?api-version=7.1-preview.1"
    print(f"Agent Pool API: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        pools = response.json().get("value", [])
        print("Available Agent Pools:")
        selected_pool_name = None

        for pool in pools:
            print(f"✔ Pool Name: {pool['name']} (ID: {pool['id']})")

            # Check if this is the pool we are using
            if pool["id"] == pool_id:
                selected_pool_name = pool["name"]

        if selected_pool_name:
            print(f"Using Agent Pool: {selected_pool_name} (ID: {pool_id})")
            return selected_pool_name
        else:
            print(f"❌ Agent Pool with ID {pool_id} not found! Please check Azure DevOps setup.")
            return None
    else:
        print(f"❌ Failed to fetch agent pools. Status Code: {response.status_code}")
        print("Response:", response.text)
        return None
      
### 6. Fetch Agents in Pool
def fetch_agents_in_pool(pool_id, silent=False):
    """ Fetches agents in the specified pool and their availability statuses. """
    url = f"https://dev.azure.com/{AZURE_ORG}/_apis/distributedtask/pools/{pool_id}/agents?api-version=7.1-preview.1"
    if not silent:
        print(f"\nAgent API: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        agents = response.json().get("value", [])
        available_agents = {}

        if not silent:
            print("Agent Name and Status in Pool ID:", pool_id)
        for agent in agents:
            agent_name = agent.get("name", "Unknown Agent")
            agent_status = agent.get("status", "offline").lower()  # 'online' or 'offline'
            assigned_request = agent.get("assignedRequest", None)  # Check if agent is running a job

            # Agent is available if it's online and not currently assigned to a job
            is_available = agent_status == "online" and assigned_request is None
            available_agents[agent_name] = is_available

            if not silent:
                status = "Available" if is_available else "Unavailable"
                print(f"✔ Agent Name: {agent_name}; Status: {status}")
        return available_agents
    else:
        if not silent:
            print(f"❌ Failed to fetch agents for pool ID {pool_id}. Status Code: {response.status_code}")
            print("Response:", response.text)
        return {}

def assign_test_cases_to_agents(test_points, available_agents):
    assigned_tests_to_agents = {}  # Dictionary to store tests per agent
    unassigned_tests = []

    # Get a list of available agent names
    active_agents = [agent for agent, is_available in available_agents.items() if is_available]

    if not active_agents:
        print("❌ No available agents found! Cannot schedule test cases.")
        return {}

    # Initialize empty lists for each active agent
    for agent in active_agents:
        assigned_tests_to_agents[agent] = []

    # Assign test cases dynamically to available agents (Round Robin distribution)
    agent_index = 0
    for point_id, (case_id, case_name, agents) in test_points.items():
        execution_time = historical_data.get(point_id, {}).get("execution_time", float("inf"))
        pass_rate = historical_data.get(point_id, {}).get("pass_rate", 0)

        assigned_agent = None

        # Try to assign the test case to one of its preferred agents
        for agent in agents:
            if agent in active_agents:  # Check if preferred agent is available
                assigned_agent = agent
                break  # Stop searching after finding an available preferred agent

        # If no preferred agent is available, skip the test case
        if not assigned_agent:
            print(f"⚠ Skipping Test Point ID {point_id} → No preferred agent available from: {agents}")
            unassigned_tests.append({
                "test_point_id": point_id,
                "test_case_id": case_id,
                "test_case_name": case_name,
                "preferred_agents": agents
            })
            continue


        assigned_tests_to_agents[assigned_agent].append({
            "test_point_id": point_id,
            "test_case_id": case_id,
            "test_case_name": case_name,
            "assigned_agent": assigned_agent,
            "execution_time": execution_time,
            "pass_rate": pass_rate,
        })

    # Print scheduled tests for each agent
    for agent, tests in assigned_tests_to_agents.items():
        print(f"✔ Test Cases Assigned to {agent}:")
        for test in tests:
            print(f"  - {test['test_case_name']} ({test['test_case_id']})")

    if unassigned_tests:
        print("\n⚠ Skipped Test Cases (No preferred agent available):")
        for test in unassigned_tests:
            agents_str = ", ".join(test["preferred_agents"])
            print(f"  - {test['test_case_name']} ({test['test_case_id']}) → Preferred: {agents_str}")


    return assigned_tests_to_agents

### 4. Get Latest Build ID
def get_latest_build():
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/build/builds?api-version=7.1-preview.7&statusFilter=completed"
    print("Test Build API:", url)
    response = requests.get(url, headers=HEADERS).json()

    builds = response.get("value", [])
    if not builds:
        print("❌ No builds found!")
        return None

    print("Available Builds:")
    for build in builds[:5]:  # Print only the latest 5 builds
        print(f"✔ Build Name: {build['buildNumber']} (ID: {build['id']})")

    latest_build = builds[0]
    print(f"Using Latest Build: {latest_build['buildNumber']} (ID: {latest_build['id']})")
    return latest_build["id"]

### Updated 7. Create Two Separate Test Runs
def create_test_runs(test_plan_id, assigned_tests_to_agents):
    """ Creates two separate test runs for two different agents. """
    
    test_run_ids = {}
    
    for agent, test_cases in assigned_tests_to_agents.items():
        if not test_cases:
            print(f"⚠ No test cases assigned to {agent}, skipping test run creation.")
            continue
        
        test_point_ids = [test["test_point_id"] for test in test_cases]
        url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/runs?api-version=7.1"

        payload = {
            "name": f"Automated Test Run for {agent} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "plan": {"id": test_plan_id},
            "pointIds": test_point_ids,
            "automated": True,
            "state": "NotStarted"
        }

        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code in [200, 201]:
            test_run_id = response.json().get("id")
            test_run_ids[agent] = test_run_id
            print(f"✔ Created Test Run {test_run_id} for {agent}")
        else:
            print(f"❌ Failed to create test run for {agent}. Status Code: {response.status_code}")
            print("Response:", response.text)

    return test_run_ids

### 6. Trigger Release Pipeline
def trigger_release(build_id, test_run_id, target_stage, is_agent_available):
    """ Triggers the 'Agent5 Pipeline' and passes the test run ID as a settable variable. """
    release_url = f"https://vsrm.dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/release/releases?api-version=7.1-preview.7"
    print(f"Release Pipeline API: {release_url}")
    payload = {
        "definitionId": 4,  # Agent5 Pipeline ID
        "description": f"Triggered by script - Test Run ID: {test_run_id}",
        "artifacts": [
            {
                "alias": "_ShoppingCartRepo",  # ✅ Use correct artifact alias
                "instanceReference": {
                    "id": str(build_id),
                    "name": "Automated Build"
                }
            }
        ],
        "reason": "manual",
        "variables": {  
            "test.RunId": {  
                "value": str(test_run_id),  
                "isSecret": False  
            },
            "StageToRun": {  
                "value": target_stage,  # Dynamically set variable
                "isSecret": False  
            },
            "isAgentAvailable": {
                "value": str(is_agent_available).lower(),  # 'true' or 'false'
                "isSecret": False
            }
        }
    }

    #print(f"Triggering Release with Payload: {json.dumps(payload, indent=2)}")  # Debugging output

    response = requests.post(release_url, headers=HEADERS, json=payload)

    if response.status_code in [200, 201]:
        release_id = response.json().get("id")
        print(f"Release Triggered Successfully! Release ID: {release_id}")
        return release_id
    else:
        print(f"❌ Failed to trigger release. Status Code: {response.status_code}")
        print("Response:", response.text)
        return None

### Stage
def manually_start_correct_stage(release_id, agent_name):
    environments = get_release_environments(release_id)
    for env in environments:
        if agent_name == "Nafis5" and env["name"] == "N5 Stage":
            deploy_environment(release_id, env["id"], env["name"])
        elif agent_name == "Nafis6" and env["name"] == "N6 Stage":
            deploy_environment(release_id, env["id"], env["name"])
        else:
            print(f"⏭ Skipping stage '{env['name']}' for agent '{agent_name}' (not required)")

### Updated 8. Monitor Two Separate Test Runs
def monitor_multiple_test_runs(release_id, test_run_ids, test_points):
    """ Monitors execution of two separate test runs. """
    
    for agent, test_run_id in test_run_ids.items():
        print(f"\n▶ Monitoring Test Run {test_run_id} for {agent}...")

        monitor_release_and_tests(release_id, test_run_id, test_points)

### 6. Monitor Execution Status
def monitor_release_and_tests(release_id, test_run_id, test_points):
    """ Monitors the status of the release pipeline stages and test run status. """
    release_url = f"https://vsrm.dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/release/releases/{release_id}?api-version=7.1-preview.7"
    test_run_url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/runs/{test_run_id}?api-version=7.1"

    print(f"Release Pipeline ({release_id}) API: {release_url}")
    print(f"Test Run ({test_run_id}) API: {test_run_url}")

    timeout = timedelta(minutes=2)
    start_time = datetime.now()
    completed_stages = set()
    test_run_completed = False

    while True:
        # Fetch release status
        release_response = requests.get(release_url, headers=HEADERS)
        if release_response.status_code == 200:
            release_json = release_response.json()
            release_status = release_json.get("status", "Unknown").lower()

            for env in release_json.get("environments", []):
                env_name = env.get("name", "Unknown")
                env_status = env.get("status", "Unknown")

                if env_name not in completed_stages and env_status in ["succeeded", "failed", "canceled", "rejected"]:
                    print(f"Stage: {env_name} → Status: {env_status.upper()}")
                    completed_stages.add(env_name)

            if len(completed_stages) == len(release_json.get("environments", [])):
                print("All Stages Completed!")
                break
        else:
            print(f"❌ Failed to fetch release status. Status Code: {release_response.status_code}")
            print("Response:", release_response.text)
            break

        # Fetch test run status
        if not test_run_completed:
            test_response = requests.get(test_run_url, headers=HEADERS)
            if test_response.status_code == 200:
                test_json = test_response.json()
                test_run_status = test_json.get("state", "Unknown")

                if test_run_status in ["Completed", "Aborted", "Failed"]:
                    print(f"Test Run ID {test_run_id} → Status: {test_run_status.upper()}")
                    test_run_completed = True

                    # Fetch and print detailed test results
                    fetch_test_run_results(test_run_id, test_points)

            else:
                print(f"❌ Failed to fetch test run status. Status Code: {test_response.status_code}")
                print("Response:", test_response.text)

        # Timeout check
        if datetime.now() - start_time > timeout:
            print("⚠ Timeout reached! Some stages or tests are still running.\n")
            break

        time.sleep(20)

def fetch_test_run_results(test_run_id, test_points):
    """ Fetches the results of the test cases in a test run and displays correct test case names, IDs, point IDs, agent name, and execution time. """
    url = f"https://dev.azure.com/{AZURE_ORG}/{PROJECT}/_apis/test/Runs/{test_run_id}/results?api-version=7.1"

    print(f"Fetching Test Results from: {url}")
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        response_json = response.json()
        print(f"Test Run ({test_run_id}) Results :")

        for result in response_json.get("value", []):
            test_case_id = result.get("testCase", {}).get("id", "Unknown Test Case ID")
            outcome = result.get("outcome", "Unknown")  # Pass / Fail / NotExecuted
            agent_name = result.get("computerName", "Unknown Agent")  # Fetch Agent Name
            execution_time = round(result.get("durationInMs", 0) / 1000, 2)  # Convert ms to seconds

            # Find the test case name, test point ID, and assigned agents using test_case_id
            test_case_name = "Unknown Test Case"
            test_point_id = "Unknown Point ID"
            assigned_agents = []

            for point_id, (case_id, case_name, agents) in test_points.items():
                if str(case_id) == str(test_case_id):
                    test_case_name = case_name
                    test_point_id = point_id
                    assigned_agents = agents
                    break  # Stop searching once found

            agents_str = ", ".join(assigned_agents) if assigned_agents else "Unassigned"
            print(f"Test Case ID: {test_case_id}; Point ID: {test_point_id}; Name: {test_case_name}, Assigned Agents: {agents_str}")
            print(f"     → Status: {outcome.upper()}, Executed on: {agent_name}, Execution Time: {execution_time:.2f} sec")

        print("✔ Test Run Results Fetched Successfully!")
    else:
        print(f"❌ Failed to fetch test results. Status Code: {response.status_code}")
        print("Response:", response.text)


### **Main Execution Flow**
if __name__ == "__main__":
    print("\nStep 01: Fetching Test Plan...")
    test_plan_id = get_test_plan()
    if not test_plan_id:
        print("❌ Test Plan not found! Exiting.")
        exit()

    print("\nStep 02: Fetching Test Suite...")
    test_suite_id = get_test_suite(test_plan_id)
    if not test_suite_id:
        print("❌ Test Suite not found! Exiting.")
        exit()

    print("\nStep 03: Fetching Test Case IDs...")
    test_cases = get_test_cases(test_plan_id, test_suite_id)
    if not test_cases:
        print("❌ No Test Cases found! Exiting.")
        exit()

    print("\nStep 04: Fetching Test Cases Name and Point IDs...")
    test_points, test_point_ids = get_test_points(test_plan_id, test_suite_id)
    if not test_points:
        print("❌ No Test Points found! Exiting.")
        exit()

    print("\nStep 05: Fetching Available Agent Pools and Agents...")
    selected_pool_name = get_agent_pool(POOL_ID)
    if not selected_pool_name:
        print("❌ Failed to identify the Agent Pool! Exiting.")
        exit()

    # Fetch and display agents in the specified pool
    available_agents = fetch_agents_in_pool(POOL_ID)
    if not available_agents:
        print(f"❌ No Agents found in Pool ID {POOL_ID}! Exiting.")
        exit()

    print("\nStep 06: Assigning Test Cases to Specific Agents...")
    assigned_tests_to_agents = assign_test_cases_to_agents(test_points, available_agents)
    if not assigned_tests_to_agents:
        print("❌ No Test Cases scheduled! Exiting.")
        exit()

    # Extract test_point_ids from scheduled tests
    scheduled_test_point_ids = [test["test_point_id"] for agent_tests in assigned_tests_to_agents.values() for test in agent_tests]


    print("\nStep 07: Fetching Latest Build...")
    build_id = get_latest_build()
    if not build_id:
        print("❌ No build found! Exiting.")
        exit()

    print("\nStep 08: Creating Test Run for Each Agent...")
    test_run_ids = create_test_runs(test_plan_id, assigned_tests_to_agents)
    if not test_run_ids:
        print("❌ Test Run Creation Failed! Exiting.")
        exit()

    print("\nStep 09: Triggering Release Pipelines for Each Test Run...")
    release_ids = {}  # test_run_id → release_id
    release_agents = {}  # release_id → agent

    for agent, test_run_id in test_run_ids.items():
        if agent == "Nafis5":
            target_stage = "N5 Stage"
        elif agent == "Nafis6":
            target_stage = "N6 Stage"
        else:
            print(f"⚠ Unknown agent: {agent}. Skipping.")
            continue

        print(f"🚀 Triggering Release for Test Run ID: {test_run_id} assigned to {agent}")
        is_agent_available = available_agents.get(agent, False)
        release_id = trigger_release(build_id, test_run_id, target_stage, is_agent_available)

        if release_id:
            release_ids[test_run_id] = release_id
            release_agents[release_id] = agent  # ✅ track which agent goes with which release

        else:
            print(f"❌ Failed to trigger release for Test Run ID: {test_run_id}")
    if not release_ids:
        print("❌ Failed to trigger releases! Exiting.")
        exit()

    print("\nStep 10: Starting Specific Release Stages for Specific Agents...")
    for release_id, agent_name in release_agents.items():
        manually_start_correct_stage(release_id, agent_name)


    print("\nStep 11: Monitoring Each Release and Test Run Execution...")
    for test_run_id, release_id in release_ids.items():
        print(f"▶ Monitoring Release {release_id} for Test Run {test_run_id}...")
        monitor_release_and_tests(release_id, test_run_id, test_points)


    print("✔ Test execution completed!")

# Sheduling and Running Software TestCases Based on AI (Master Thesis | ABB Bryne)

## 🔄 Part 01: Azure DevOps Automated Test Run & Release Orchestration

This Python script automates **test execution** and **release deployment** across multiple agents in Azure DevOps. It dynamically assigns test cases based on agent availability and preferred assignments, then triggers separate release pipelines and test runs accordingly.

---

### 🚀 Features

- ✅ **Creates Separate Test Runs** for different agents
- ✅ **Triggers Independent Releases** with targeted stages
- ✅ **Assigns Test Cases** to agents based on availability & embedded `{Agent}` tags
- ✅ **Launches Different Pipeline Stages** based on the Test Run
- ✅ **Monitors Release & Test Run Execution** and prints detailed results

---

### 📁 Project Structure

The key stages of the script include:

1. **Fetch Test Plan, Test Suites & Test Cases**
2. **Gather Test Points and Agent Preferences**
3. **Assign Test Cases to Available Agents**
4. **Create Per-Agent Test Runs**
5. **Trigger Stage-Specific Releases**
6. **Monitor and Report Results**

---

### ⚙ Prerequisites

- Python 3.7+
- Active Azure DevOps organization
- A test plan (`RoboTestPlan`) and test suite with test cases
- Release pipeline configured with stages (e.g., `Autobot1 Stage`, `Autobot2 Stage`)
- Valid **Personal Access Token (PAT)** with appropriate permissions

---

### 🔧 Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/azure-devops-test-release-automation.git
   cd azure-devops-test-release-automation

2. **Install Required Packages**

   (Only if you add new packages in the future; current code uses requests, which is standard)
   ```bash
   pip install requests

3. **Deploy Self-Hosted Agents**

   This script uses two self-hosted agents:
      - Autobot1
      - Autobot2

   You can do the same by following the below steps :
      - Install the [Azure Pipelines Agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/windows-agent?view=azure-devops&tabs=IP-V4) on your machine.
      - Register them under the same Agent Pool (POOL_ID) in Azure DevOps.
      - Ensure both agents are online and idle before running the script.
  
4. **Update the Configuration**

   In the script, set your environment variables and values:
   ```python
   AZURE_ORG = "your-org"
   PROJECT = "your-project"
   PAT = "your-personal-access-token"
   TEST_PLAN_NAME = "your-plan"
   SUITE_ID = your-suite-id
   POOL_ID = your-agent-pool-id
   RELEASE_PIPELINE_ID = your-pipeline-definition-id
   ARTIFACT_ALIAS = "_YourAlias"
   AGENT_01 = "your-preferred-agent"
   AGENT_02 = "your-preferred-agent"
   TARGET_STAGE_01 = "your-targeted-stage"
   TARGET_STAGE_02 = "your-targeted-stage"
   
---

### 🧠 How It Works

1. Test cases are tagged with agent preferences using curly braces in their names:

   ```vbnet
   Test01 {Autobot1}
   Test02 {Autobot2}
   Test03 {Autobot1,Autobot2}

2. Script fetches test points and determines which agent should run each case based on:

   - Preferred agents in the name
   - Availability from the Azure DevOps agent pool
   - Historical execution data (for now, simulated in this script)
  
3. Separate test runs are created — one per agent.
   
4. Release pipelines are triggered with different stages depending on the assigned agent.

5. Each release starts its corresponding stage.

6. The script monitors both the release status and test execution in parallel and prints out results.
   
---

### 📊 Sample Output

   ```yaml
   Step 01: Fetching Test Plan...
   Available Test Plans:
   ✔ Test Plan Name: RoboTestPlan (ID: 1)
   Using Test Plan: RoboTestPlan (ID: 1)
   
   Step 02: Fetching Test Suite...
   Available Test Suites:
   ✔ Test Suite Name: RoboTestPlan (ID: 2)
   Using Test Suite: RoboTestPlan (ID: 2)
   
   Step 03: Fetching Test Case IDs...
   Available Test Case IDs: ['3', '4', '5', '6', '7', ...]
   
   Step 04: Fetching Test Cases Name and Point IDs...
   Available Test Cases:
   ✔ Test Case ID: 3; Point ID: 1; Case Name: Test01 {Autobot1}; Assigned Agents: Autobot1
   ✔ Test Case ID: 4; Point ID: 2; Case Name: Test02 {Autobot2}; Assigned Agents: Autobot2
   ✔ Test Case ID: 5; Point ID: 3; Case Name: Test03 {Autobot1,Autobot2}; Assigned Agents: Autobot1, Autobot2
   
   Step 05: Fetching Available Agent Pools and Agents...
   Available Agent Pools:
   ✔ Pool Name: Default (ID: 1)
   ✔ Pool Name: Autobots (ID: 10)
   Using Agent Pool: Autobots (ID: 10)

   Step 06: Fetching Agents in Selected Pool...
   Agent Name and Status in Pool ID: 10
   ✔ Agent Name: Autobot1; Status: Available
   ✔ Agent Name: Autobot2; Status: Available
   
   Step 07: Assigning Test Cases to Specific Agents...
   ✔ Test Cases Assigned to Autobot1:
     - Test01 {Autobot1} (ID: 3)
     - Test03 {Autobot1,Autobot2} (ID: 5)

   ✔ Test Cases Assigned to Autobot2:
     - Test02 {Autobot2} (ID: 4)
     - Test05 {Autobot2} (ID: 7)
   
   Step 08: Fetching Latest Build...
   Available Builds:
   ✔ Build Name: 20250422.3 (ID: 3)
   ✔ Build Name: 20250422.2 (ID: 2)
   Using Latest Build: 20250422.3 (ID: 3)
   
   Step 09: Creating Seperate Test Run for Each Agent...
   ✔ Created Test Run 19 for Autobot1
   ✔ Created Test Run 20 for Autobot2
   
   Step 10: Triggering Release Pipelines for Each Test Run...
   🚀 Triggering Release for Test Run ID: 19 assigned to Autobot1
   Release Triggered Successfully! Release ID: 18
   🚀 Triggering Release for Test Run ID: 20 assigned to Autobot2
   Release Triggered Successfully! Release ID: 19
   
   Step 11: Starting Specific Release Stages for Specific Agents...
   ✅ Starting Stage 'Autobot1 Stage' (Environment ID: 35) for Release ID: 18
   ⏭ Skipping stage 'Autobot2 Stage' for agent 'Autobot1' (not required)
   ⏭ Skipping stage 'Autobot1 Stage' for agent 'Autobot2' (not required)
   ✅ Starting Stage 'Autobot2 Stage' (Environment ID: 38) for Release ID: 19

   Step 12: Monitoring Each Release and Test Run Execution...
   ▶ Monitoring Release 18 for Test Run 19...
   Stage: Autobot1 Stage → Status: SUCCEEDED
   Test Run ID 19 → Status: COMPLETED
   Test Run (19) Results :
   Test Case ID: 3; Point ID: 1; Name: Test01 {Autobot1}, Assigned Agents: Autobot1
        → Status: PASSED, Executed on: NAFIS (Autobot1), Execution Time: 1.02 sec
   Test Case ID: 5; Point ID: 3; Name: Test03 {Autobot1,Autobot2}, Assigned Agents: Autobot1, Autobot2
        → Status: PASSED, Executed on: NAFIS (Autobot1), Execution Time: 3.02 sec
   Test Case ID: 6; Point ID: 4; Name: Test04 {Autobot1}, Assigned Agents: Autobot1
        → Status: PASSED, Executed on: NAFIS (Autobot1), Execution Time: 4.01 sec
   ✔ Test Run Results Fetched Successfully!
   
   ▶ Monitoring Release 19 for Test Run 20...
   Stage: Autobot2 Stage → Status: SUCCEEDED 
   Test Run ID 20 → Status: COMPLETED
   Test Run (20) Results :
   Test Case ID: 4; Point ID: 2; Name: Test02 {Autobot2}, Assigned Agents: Autobot2
        → Status: PASSED, Executed on: NAFIS (Autobot1), Execution Time: 2.01 sec
   Test Case ID: 7; Point ID: 5; Name: Test05 {Autobot2}, Assigned Agents: Autobot2
        → Status: PASSED, Executed on: NAFIS (Autobot1), Execution Time: 5.01 sec
   ✔ Test Run Results Fetched Successfully!
     
   ✔ Test execution completed!
   ```

---

### 📊 Historical Data

---

### 🛠️ Future Improvements

---

## 🔄 Part 02: Scheduling and Optimization of Automated TestCases Based on AI

---

## 🙌 Acknowledgments

Special thanks to Morten Mossige - our supervisor, for his continuous guidance and support.

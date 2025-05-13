# Scheduling and Running Software TestCases Based on AI
**Master Thesis | ABB Bryne**

## 🔄 Part 01: Automated Test Orchestration via Azure DevOps & Python Automation

This project automates software test execution and release orchestration in Azure DevOps using Python. It dynamically assigns test cases to agents based on embedded preferences and availability, runs agent-specific pipelines, and stores test results in Cosmos DB for analysis.


---

### 🚀 Workflow Overview

- ✅ Dynamically assigns test cases using `{Autobot1}`, `{Autobot2}`, etc. in test names  
- ✅ Creates **separate test runs per agent**  
- ✅ Triggers a **fresh build** on every script run  
- ✅ Deploys targeted stages via **release pipelines**  
- ✅ Fetches test results and uploads them to **Azure Cosmos DB**  
- ✅ Supports **randomized test failures** for scheduling model simulation 

---

### 📁 Script Location

```plaintext
   /scripts/AutomatedTestCasesWithLogsNBuild.py
```
This is the main script. Run it locally to initiate the entire DevOps workflow.

---

### ⚙ Prerequisites

- Python 3.7+
- Active Azure DevOps organization with
   - A test plan (`RoboTestPlan`) and test suite with test cases
   - Build & Release pipelines (IDs specified in the script)
   - Self-hosted agents named `Autobot1`, `Autobot2`, etc.
- Azure Cosmos DB instance with SQL (Core) API
- Required Python packages:
   ```bash
   pip install requests azure-cosmos
   
---

### 🔧 Setup

1. **Install Required Packages**

   (Only if you add new packages in the future; current code uses requests, which is standard)
   ```bash
   pip install requests azure-cosmos

2. **Deploy Self-Hosted Agents**

   This script uses three self-hosted agents:
      - Autobot1
      - Autobot2
      - Autobot3

   You can do the same by following the below steps :
      - Install the [Azure Pipelines Agent](https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/windows-agent?view=azure-devops&tabs=IP-V4) on your machine.
      - Register them under the same Agent Pool (POOL_ID) in Azure DevOps.
      - Ensure both agents are online and idle before running the script.
  
3. **Update the Configuration**

   In the script, set your environment variables and values. For example,
   ```python
   AZURE_ORG = "your-org"
   PROJECT = "your-project"
   PAT = "your-personal-access-token"
   TEST_PLAN_NAME = "your-plan"
   SUITE_ID = your-suite-id
   POOL_ID = your-agent-pool-id
   ARTIFACT_ALIAS = "_YourAlias"
   AGENT_01 = "your-preferred-agent"
   TARGET_STAGE_01 = "your-targeted-stage"
   
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
  
3. Separate test runs are created — one per agent.
   
4. Release pipelines are triggered with different stages depending on the assigned agent.

5. Each release starts its corresponding stage.

6. The script monitors both the release status and test execution in parallel and prints out results.
   
---

### 📦 Cosmos DB

Each test result is stored as a document in Cosmos DB under:
- **Database:** TestResultsDB
- **Container:** testRuns
- **Partition Key:** /testRunId

This enables analytics and AI-based scheduling.

---

### 🧠 Random Test Failures

Test methods in `RobotTests.cs` simulate failures with configurable probabilities. This mimics real-world test flakiness and helps train predictive models.
   ```csharp
   await SimulateTest(new Robot(), 2000, 0.4); // 40% chance to fail
   await SimulateTest(new Robot(), 1000, 0.0); // always pass
   await SimulateTest(new Robot(), 1000, 1.0); // always fail


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

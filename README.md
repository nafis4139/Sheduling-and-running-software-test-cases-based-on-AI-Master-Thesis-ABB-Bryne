# Sheduling and Running Software TestCases Based on AI (Master Thesis | ABB Bryne)

## 🔄 Part 01: Azure DevOps Automated Test Run & Release Orchestration

This Python script automates **test execution** and **release deployment** across multiple agents in Azure DevOps. It dynamically assigns test cases based on agent availability and preferred assignments, then triggers separate release pipelines and test runs accordingly.

---

### 🚀 Features

- ✅ **Creates two separate test runs** for different agents
- ✅ **Triggers two independent releases** with targeted stages
- ✅ **Assigns test cases** to agents based on availability & preferences
- ✅ **Launches different pipeline stages** based on the test run
- ✅ **Monitors release & test run execution** and prints detailed results

---

## 📁 Project Structure

The key stages of the script include:

1. **Fetch Test Plan & Suite**
2. **Gather Test Points** and Agent Preferences
3. **Check Agent Availability**
4. **Schedule Test Cases** across agents
5. **Create Test Runs**
6. **Trigger Releases** with targeted stages
7. **Automatically Start Correct Stage**
8. **Monitor Execution**
9. **Print Results**

---

## ⚙ Prerequisites

- Python 3.7+
- Active Azure DevOps organization
- A test plan (`ShoppingCart_TP`) and test suite with test cases
- Release pipeline configured with stages (e.g., `N5 Stage`, `N6 Stage`)
- Valid **Personal Access Token (PAT)** with appropriate permissions

---

## 🔧 Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/azure-devops-test-release-automation.git
   cd azure-devops-test-release-automation

2. **Install Required Packages**

   (Only if you add new packages in the future; current code uses requests, which is standard)
   ```bash
   pip install requests

3. Update the Configuration

   In the script, set your environment variables and values:
   ```python
   AZURE_ORG = "your_organization_name"
   PROJECT = "your_project_name"
   PAT = "your_personal_access_token"
   SUITE_ID = your_suite_id          # e.g., 20
   POOL_ID = your_pool_id            # e.g., 12
   
---

## 🧠 How It Works

1. Test cases are tagged with agent preferences using curly braces in their names:

   ```vbnet
   Example: "Login Test {Nafis5, Nafis6}"

2. Script fetches test points and determines which agent should run each case based on:

   - Preferred agents in the name
   - Availability from the Azure DevOps agent pool
   - Historical execution data (for now, simulated in this script)
  
3. Two separate test runs are created — one per agent.
   
4. Release pipelines are triggered with different stages (N5 Stage or N6 Stage) depending on the assigned agent.

5. Each release starts its corresponding stage.

6. The script monitors both the release status and test execution in parallel and prints out results.
   
---

## 📊 Sample Output

   ```yaml
   Step 01: Fetching Test Plan...
   Available Test Plans:
   ✔ Test Plan Name: ShoppingCart_TP (ID: 18)
   Using Test Plan: ShoppingCart_TP (ID: 18)
   
   Step 02: Fetching Test Suite...
   Available Test Suites:
   ✔ Test Suite Name: ShoppingCart_TP (ID: 19)
   ✔ Test Suite Name: ShoppingCart_Suite (ID: 20)
   Using Test Suite: ShoppingCart_Suite (ID: 20)
   
   Step 03: Fetching Test Case IDs...
   Available Test Case IDs: ['21', '22', '23', '24', '25', '26']
   
   Step 04: Fetching Test Cases Name and Point IDs...
   Available Test Cases:
   ✔ Test Case ID: 21; Point ID: 6; Case Name: TestCase1 {Nafis5}; Assigned Agents: Nafis5
   ✔ Test Case ID: 22; Point ID: 7; Case Name: TestCase2 {Nafis6}; Assigned Agents: Nafis6
   ✔ Test Case ID: 23; Point ID: 8; Case Name: TestCase3 {Nafis5,Nafis6}; Assigned Agents: Nafis5, Nafis6
   ✔ Test Case ID: 24; Point ID: 9; Case Name: TestCase4 {Nafis5}; Assigned Agents: Nafis5
   ✔ Test Case ID: 25; Point ID: 10; Case Name: TestCase5 {Nafis6}; Assigned Agents: Nafis6
   ✔ Test Case ID: 26; Point ID: 11; Case Name: TestCase6 {Nafis5}; Assigned Agents: Nafis5
   
   Step 05: Fetching Available Agent Pools and Agents...
   Agent Pool API: https://dev.azure.com/bmnafisfuad14/_apis/distributedtask/pools?api-version=7.1-preview.1
   Available Agent Pools:
   ✔ Pool Name: Default (ID: 1)
   ✔ Pool Name: Hosted Ubuntu 1604 (ID: 8)
   ✔ Pool Name: Azure Pipelines (ID: 9)
   ✔ Pool Name: SelfHosted2 (ID: 12)
   Using Agent Pool: SelfHosted2 (ID: 12)
   
   Agent Name and Status in Pool ID: 12
   ✔ Agent Name: Nafis5; Status: Available
   ✔ Agent Name: Nafis6; Status: Available
   
   Step 06: Assigning Test Cases to Specific Agents...
   ✔ Test Cases Assigned to Nafis5:
     - TestCase1 {Nafis5} (21)
     - TestCase3 {Nafis5,Nafis6} (23)
     - TestCase4 {Nafis5} (24)
     - TestCase6 {Nafis5} (26)
   ✔ Test Cases Assigned to Nafis6:
     - TestCase2 {Nafis6} (22)
     - TestCase5 {Nafis6} (25)
   
   Step 07: Fetching Latest Build...
   Available Builds:
   ✔ Build Name: 20250305.42 (ID: 2787)
   ✔ Build Name: 20250305.41 (ID: 2786)
   Using Latest Build: 20250305.42 (ID: 2787)
   
   Step 08: Creating Test Run for Each Agent...
   ✔ Created Test Run 378 for Nafis5
   ✔ Created Test Run 379 for Nafis6
   
   Step 09: Triggering Release Pipelines for Each Test Run...
   🚀 Triggering Release for Test Run ID: 378 assigned to Nafis5
   Release Triggered Successfully! Release ID: 257
   🚀 Triggering Release for Test Run ID: 379 assigned to Nafis6
   Release Triggered Successfully! Release ID: 258
   
   Step 10: Starting Specific Release Stages for Specific Agents...
   ✅ Starting Stage 'N5 Stage' (Environment ID: 337) for Release ID: 257
   ⏭ Skipping stage 'N6 Stage' for agent 'Nafis5' (not required)
   ⏭ Skipping stage 'N5 Stage' for agent 'Nafis6' (not required)
   ✅ Starting Stage 'N6 Stage' (Environment ID: 340) for Release ID: 258
   
   Step 11: Monitoring Each Release and Test Run Execution...
   ▶ Monitoring Release 257 for Test Run 378...
   Test Run ID 378 → Status: COMPLETED
   Test Run (378) Results :
   Test Case ID: 21; Point ID: 6; Name: TestCase1 {Nafis5}, Assigned Agents: Nafis5
        → Status: PASSED, Executed on: NAFIS (Nafis5), Execution Time: 0.00 sec
   Test Case ID: 23; Point ID: 8; Name: TestCase3 {Nafis5,Nafis6}, Assigned Agents: Nafis5, Nafis6
        → Status: PASSED, Executed on: NAFIS (Nafis5), Execution Time: 0.00 sec
   Test Case ID: 24; Point ID: 9; Name: TestCase4 {Nafis5}, Assigned Agents: Nafis5
        → Status: PASSED, Executed on: NAFIS (Nafis5), Execution Time: 0.00 sec
   Test Case ID: 26; Point ID: 11; Name: TestCase6 {Nafis5}, Assigned Agents: Nafis5
        → Status: PASSED, Executed on: NAFIS (Nafis5), Execution Time: 0.00 sec
   ✔ Test Run Results Fetched Successfully!
   
   ▶ Monitoring Release 258 for Test Run 379...
   Test Run ID 379 → Status: COMPLETED
   Test Run (379) Results :
   Test Case ID: 22; Point ID: 7; Name: TestCase2 {Nafis6}, Assigned Agents: Nafis6
        → Status: PASSED, Executed on: NAFIS (Nafis6), Execution Time: 0.00 sec
   Test Case ID: 25; Point ID: 10; Name: TestCase5 {Nafis6}, Assigned Agents: Nafis6
        → Status: PASSED, Executed on: NAFIS (Nafis6), Execution Time: 0.00 sec
   ✔ Test Run Results Fetched Successfully!
   
   ✔ Test execution completed!
   ```

---

## 📊 Historical Data

---

## 🛠️ Future Improvements

---

## 🙌 Acknowledgments

Special thanks to Morten Mossige - our supervisor, for his continuous guidance and support.





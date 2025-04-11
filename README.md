# Sheduling and Running Software TestCases Based on AI (Master Thesis | ABB Bryne)

# 🔄 Part 01: Azure DevOps Automated Test Run & Release Orchestration

This Python script automates **test execution** and **release deployment** across multiple agents in Azure DevOps. It dynamically assigns test cases based on agent availability and preferred assignments, then triggers separate release pipelines and test runs accordingly.

---

## 🚀 Features

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
✔ Created Test Run 1234 for Nafis5
✔ Created Test Run 1235 for Nafis6
🚀 Triggered Release ID: 4567 for Test Run 1234
✅ Manually started stage 'N5 Stage' (Environment ID: 789)
Test Case ID: 22; Point ID: 7; Name: "Checkout Test", Assigned Agents: Nafis5
     → Status: PASSED, Executed on: Nafis5, Execution Time: 12.3 sec


   

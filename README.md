# Sheduling and Running Software TestCases Based on AI (Master Thesis | ABB Bryne)

# 🔄 Azure DevOps Automated Test Run & Release Orchestration

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
7. **Manually Start Correct Stage**
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

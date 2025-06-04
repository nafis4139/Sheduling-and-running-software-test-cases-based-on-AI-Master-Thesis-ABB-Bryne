# Scheduling and Running Software TestCases Based on AI
**Master Thesis | ABB Bryne**


### 📁 Script Location
   ```plaintext
   /scripts/phase1_RunAllTests.py - Run this to run all available tests
   /scripts/phase2_prioritize_tests.py - Run this to do the prioritization using qLearning
   /scripts/phase3_schedule_tests.py - Run this to do the scheduling using Google-OR
   /scripts/phase4_RunScheduledTests.py - Run this to run the final scheduled tests

   ```
Run it locally to initiate the entire DevOps workflow.

---

### ⚙ Prerequisites

- Python 3.7+
- Active Azure DevOps organization with
   - A test plan (`RoboTestPlan`) and test suite with test cases
   - Build & Release pipelines (IDs specified in the script)
   - Self-hosted agents named `Autobot1`, `Autobot2`, `Autobot3`.
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
   ```

---

## 🙌 Acknowledgments

Special thanks to Morten Mossige - our supervisor, for his continuous guidance and support.

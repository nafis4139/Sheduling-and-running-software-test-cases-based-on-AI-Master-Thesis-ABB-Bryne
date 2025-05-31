import pandas as pd
from ortools.linear_solver import pywraplp

# Load the test priority data
df = pd.read_csv("CosmosDB/test_priority_summary.csv")

# Define scheduling parameters
#MAX_TOTAL_TIME = 60 * 60  # in seconds (1 hour budget)
MAX_TOTAL_TIME = 20  # in seconds (testing with 20-second budget)

# Initialize solver
solver = pywraplp.Solver.CreateSolver("SCIP")

# Define binary decision variables
x = {}
for i, row in df.iterrows():
    x[i] = solver.IntVar(0, 1, f"x_{i}")

# Constraint: total duration of selected tests must be within budget
solver.Add(solver.Sum(x[i] * row["avgTime"] for i, row in df.iterrows()) <= MAX_TOTAL_TIME)

# Objective: maximize total priority score
solver.Maximize(solver.Sum(x[i] * row["priorityScore"] for i, row in df.iterrows()))

# Solve
status = solver.Solve()

# Output results
if status == pywraplp.Solver.OPTIMAL:
    print("✅ Optimal test schedule found!\n")
    selected = df[[x[i].solution_value() > 0.5 for i in df.index]]
    print(f"\n📌 Selected {len(selected)} out of {len(df)} test cases.")

    print(selected[["testCaseId", "testCaseTitle", "priorityScore", "avgTime"]])
    print(f"\n⏱ Total Scheduled Time: {selected['avgTime'].sum():.2f} sec")
    print(f"⭐ Total Priority Score: {selected['priorityScore'].sum():.4f}")
    selected.to_csv("CosmosDB/scheduled_tests.csv", index=False)
    print("📁 Saved selected tests to CosmosDB/scheduled_tests.csv")

else:
    print("❌ No optimal solution found.")

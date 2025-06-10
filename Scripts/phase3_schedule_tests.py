import pandas as pd
from ortools.sat.python import cp_model

# Load the Q-learning output CSV
df = pd.read_csv("CosmosDB/scheduled_tests_qlearning.csv")

# Time budget (seconds)
MAX_TOTAL_TIME = 20  # adjust as needed

# Create the CP model
model = cp_model.CpModel()

# Define binary decision variables for each test case
x = {}
for i, row in df.iterrows():
    x[i] = model.NewBoolVar(f"x_{i}")

# Constraint: total time must be within the budget
model.Add(sum(int(row["avgTime"] * 1000) * x[i] for i, row in df.iterrows()) <= int(MAX_TOTAL_TIME * 1000))

# Objective: maximize total Q_value
scaling = 1000  # scale Q_values to integers for CP-SAT
model.Maximize(sum(int(row["Q_value"] * scaling) * x[i] for i, row in df.iterrows()))

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("✅ Schedule found using CP-SAT!\n")
    selected = df[[solver.Value(x[i]) > 0 for i in df.index]]
    print(f"\n📌 Selected {len(selected)} out of {len(df)} test cases.")
    print(selected[["testCaseId", "testCaseTitle", "Q_value", "avgTime"]])
    print(f"\n⏱ Total Scheduled Time: {selected['avgTime'].sum():.2f} sec")
    print(f"⭐ Total Q Value: {selected['Q_value'].sum():.4f}")

    # Save result
    selected.to_csv("CosmosDB/scheduled_tests_qlearning_solved_cpsat.csv", index=False)
    print("📁 Saved to CosmosDB/scheduled_tests_qlearning_solved_cpsat.csv")
else:
    print("❌ No feasible schedule found.")

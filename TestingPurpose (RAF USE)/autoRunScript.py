import time
import subprocess

script_path = r"D:\Master Thesis 2025 UiS\RobotArmSimulator Project\RobotArmSolution\Scripts\AutomatedTestCaseWithLogsNBuild.py"

while True:
    print(f"Running: {script_path}")
    try:
        subprocess.run(["python", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
    time.sleep(15 * 60)

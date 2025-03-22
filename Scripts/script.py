import subprocess

# Dataset 1
available_bandwidth = 100                               # i)   100
cross_traffic_values = [25, 50, 75]                     #      25, 50, 75

# Dataset 2
# available_bandwidth = 50                                # ii)  50
# cross_traffic_values = [12.5, 25, 37.5]                 #      12.5, 25, 37.5
num_runs = 100

# Run the command for each crosstraffic value, 100 times each
for cross_traffic in cross_traffic_values:
    print(f"Cross traffic = {cross_traffic}")
    for test_num in range(num_runs):
        print(f"Test no. : {test_num}")
        subprocess.run(["mn", "-c"], check=True)                # Clear any previous Mininet environment

        command = ["python", "mini.py", str(available_bandwidth), str(cross_traffic)]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Command executed: {' '.join(command)}")
            print("Output:", result.stdout)
        
        except subprocess.CalledProcessError as e:
            print(f"Error executing command {' '.join(command)}: {e}")
            print("Error Output:", e.stderr)
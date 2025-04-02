import subprocess

# Dataset 1
available_bandwidth = 100                               # i)   100                  (all units are in Mbps)
cross_traffic_values = [25, 50, 75]                     #      25, 50, 75

# Dataset 2
# available_bandwidth = 50                                # ii)  50
# cross_traffic_values = [12.5, 25, 37.5]                 #      12.5, 25, 37.5

num_iterations = 800

# Simulating for each cross traffic value   x   (num_iterations)
for cross_traffic in cross_traffic_values:
    print(f"[INFO] Cross traffic = {cross_traffic}")
    for itr in range(num_iterations):
        print(f"[INFO] Test no. : {itr}")
        subprocess.run(["sudo", "mn", "-c"], check=True)                # Clear any previous Mininet environment

        command = ["sudo", "python", "mini.py", str(available_bandwidth), str(cross_traffic)]
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"[SUCCESS] Command executed: {' '.join(command)}")
            print(f"[OUTPUT] {result.stdout}")
        
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to execute command: {' '.join(command)}")
            print(f"[ERROR] {e.stderr}")
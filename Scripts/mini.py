import sys
import subprocess
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import csv

class SimpleLinkTopo(Topo):
    def build(self, availbw):
        # Add two hosts
        h1 = self.addHost('h1')  # Server
        h2 = self.addHost('h2')  # Client

        h3 = self.addHost('h3')  # Server
        h4 = self.addHost('h4')  # Client
        
        # Add a single switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')


        # Add links with 100 Mbps bandwidth, no loss, and no delay
        self.addLink(h1, s1, bw=availbw, loss=0, delay='0ms')
        self.addLink(h3, s1, bw=availbw, loss=0, delay='0ms')
        
        self.addLink(h2, s2, bw=availbw, loss=0, delay='0ms')
        self.addLink(h4, s2, bw=availbw, loss=0, delay='0ms')
        
        self.addLink(s1, s2, bw=availbw, loss=0, delay='0ms')


# check if the SDN controller is running
def check_controller(controller_ip, controller_port):
    print(f"[INFO] Checking if SDN Controller is running at {controller_ip}:{controller_port}...")
    try:
        result = subprocess.run(
            ["nc", "-z", controller_ip, str(controller_port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            print(f"[SUCCESS] SDN Controller is UP at {controller_ip}:{controller_port}")
            return True
        else:
            print(f"[ERROR] SDN Controller is NOT running at {controller_ip}:{controller_port}. Please start the controller first!")
            return False
    
    except FileNotFoundError:
        print("[ERROR] 'nc' command not found. Install netcat(nc) to check the controller status.")
        return False
    

# run a Mininet simulation with a remote OpenFlow SDN controller & crosstraffic
def run(availbw, crosstraffic):
    setLogLevel('info')
    
    # IP and port of the remote Openflow SDN controller
    controller_ip = '10.17.5.63'        # Change to the controller's IP address if not local
    controller_port = 6653              # Default OpenFlow controller port
    
    # Check if controller is running before proceeding
    if not check_controller(controller_ip, controller_port):
        sys.exit(1)

    # Initialize the topology
    topo = SimpleLinkTopo(availbw=availbw)

    # Initialize the network with the custom topology and TCLink for link configuration
    net = Mininet(topo=topo, link=TCLink, controller=None)

    # Adding remote SDN controller named 'c0' to the network
    remote_controller = RemoteController('c0', ip=controller_ip, port=controller_port)
    net.addController(remote_controller)

    # Start the network -> launch topology and connect the nodes
    print("[INFO] Starting Mininet network...")
    net.start()

    # retrieve the hosts IP addresses
    h1, h2, h3, h4 = net.get('h1'), net.get('h2'), net.get('h3'), net.get('h4')
    print(f"[INFO] IPs assigned: \nh1={h1.IP()},\t h2={h2.IP()}, \nh3={h3.IP()},\t h4={h4.IP()}")


    print(f"\n[INFO] -------------Introducing crosstraffic---------\n")
    # CLI(net)
    h4.cmd(f"iperf -s -u > ../Logs/h4_iperf.txt 2>&1 &")                    # start the UDP iperf server on h4
    print("[SUCCESS] Started UDP iperf server on h4")
    time.sleep(2)

    # running the UDP iperf client on h3, to send crosstraffic to h4 for 30 seconds
    h3.cmd(f"iperf -c {h4.IP()} -u -b {crosstraffic}M -t 30 > ../Logs/h3_iperf.txt 2>&1 &") 
    print("[SUCCESS] Started UDP iperf client on h3")  
    
    # Setting the environment variable for Go
    h1.cmd(f"export PATH=$PATH:/usr/local/go/bin")
    h2.cmd(f"export PATH=$PATH:/usr/local/go/bin")
    # CLI(net)

    print("[INFO] Starting receiver(client) on h2")
    h2.cmd(f"go run receiver.go > ../Logs/h2_output.txt 2>&1 &")
    time.sleep(1)           # allow receiver to start

    print("[INFO] Starting sender(server) on h1")
    h1.cmd(f"go run sender.go > ../Logs/h1_output.txt 2>&1 &")

    time.sleep(30)          # wait for the server to finish
    net.stop()


    with open("../NewData/test_info.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([availbw, crosstraffic])

    print("[SUCCESS] Results saved to '../NewData/test_info.csv'")
    # (Optional) To run Mininet's CLI for manual interaction, if needed
    # CLI(net)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: sudo python mini.py <bandwidth> <crosstraffic>")
        sys.exit(1)

    bandwidth=float(sys.argv[1])
    crosstraffic= float(sys.argv[2])
    run(availbw = bandwidth, crosstraffic = crosstraffic)
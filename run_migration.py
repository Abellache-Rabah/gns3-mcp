import sys
import os
import yaml
import time
import re

# Add project root to path to verify imports
sys.path.append(os.getcwd())

from shared.gns3_utils import GNS3Console, load_inventory

def get_device_port(device_name, inventory):
    return inventory['hosts'][device_name]['port']

def run_migration():
    print("Loading Inventory...")
    inventory = load_inventory()
    
    # Configuration Targets
    # PC1 -> 40.0.0.10/24 gw .99
    # PC2 -> 40.0.0.20/24 gw .99
    # PC3 -> 20.0.0.10/24 gw .99
    
    configs = [
        {
            "device": "pc1",
            "ip": "40.0.0.10",
            "cidr": "24",
            "mask": "255.255.255.0",
            "gw": "40.0.0.99",
            "cmd": "ip 40.0.0.10 255.255.255.0 40.0.0.99"
        },
        {
            "device": "pc2",
            "ip": "40.0.0.20",
            "cidr": "24",
            "mask": "255.255.255.0",
            "gw": "40.0.0.99",
            "cmd": "ip 40.0.0.20 255.255.255.0 40.0.0.99"
        },
        {
            "device": "pc3",
            "ip": "20.0.0.10",
            "cidr": "24",
            "mask": "255.255.255.0",
            "gw": "20.0.0.99",
            "cmd": "ip 20.0.0.10 255.255.255.0 20.0.0.99"
        }
    ]

    print("\n--- PHASE 1: Deployment ---")
    for config in configs:
        device = config["device"]
        port = get_device_port(device, inventory)
        print(f"Deploying to {device} (localhost:{port})...")
        
        try:
            # Connect
            console = GNS3Console("localhost", port, platform="linux") # VPCS behaves like linux/shell in util
            console.connect()
            
            # Send Config
            print(f"  Sending: {config['cmd']}")
            output = console.configure_linux(config['cmd'])
            output += console.configure_linux("save") # Persist
            
            print(f"  Output: {output.strip()}")
            console.close()
            
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n--- PHASE 2: Updating Inventory File ---")
    # Update loaded inventory object
    for config in configs:
        device = config["device"]
        inventory['hosts'][device]['data']['ip'] = config['ip']
        # Note: Inventory yaml structure might just record IP, or IP/CIDR. 
        # Looking at original file: `ip: 40.0.0.1`
        # We will update strictly the IP field.

    # Write back to file
    inv_path = "shared/inventory.yaml"
    with open(inv_path, 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False, sort_keys=False)
    print(f"Updated {inv_path}")

    print("\n--- PHASE 3: Verification (Pings) ---")
    
    # Test Connectivity
    # PC1 -> PC2 (Same Subnet)
    # PC1 -> PC3 (Cross Subnet)
    # PC2 -> PC3 (Cross Subnet)
    
    verifications = [
        ("pc1", "40.0.0.20"), # to PC2
        ("pc1", "20.0.0.10"), # to PC3
        ("pc2", "20.0.0.10"), # to PC3
    ]

    for src, target_ip in verifications:
        device_port = get_device_port(src, inventory)
        print(f"Testing {src} -> {target_ip}...")
        
        try:
            console = GNS3Console("localhost", device_port, platform="linux")
            console.connect()
            
            # VPCS ping: ping <ip>
            output = console.ping(target_ip)
            print(f"  Result: {output.strip()}")
            
            if "not reachable" in output or "timeout" in output:
                print("  [FAIL]")
            else:
                print("  [PASS]")
                
            console.close()
            
        except Exception as e:
            print(f"  ERROR: {e}")

if __name__ == "__main__":
    run_migration()

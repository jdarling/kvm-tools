# KVM Test Scripts

This repository contains four bash scripts for managing virtual machines in a KVM environment:

## Scripts Overview

### 1. `init-vm` - Initialize and Configure Virtual Machine
**Purpose**: Initializes a new VM by copying SSH keys, transferring the update script, and configuring the VM with a new hostname and IP address.

**Usage**:
```bash
./init-vm [options]
```

**Options**:
- `--new-ip, -n <ip>` - Set the new VM IP address (default: 192.168.122.104)
- `--existing-ip, -e <ip>` - Set the existing VM IP address (default: 192.168.122.114)
- `--ssh-user, -u <user>` - Set the SSH user (default: current user)
- `--ssh-key, -i <key>` - Set the SSH key path (default: ~/.ssh/id_rsa)
- `--hostname, -N <name>` - Set the new VM hostname (default: u22-server-4)
- `--password, -p [pass]` - Set the remote user password (prompts if not provided)
- `--help, -h` - Show help message

**Dependencies**: 
- `expect` package (auto-installed if missing)
- SSH access to the existing VM

**Process**:
1. Waits for existing VM to come online
2. Copies SSH keys to the VM using `ssh-copy-id`
3. Transfers the `update-vm` script to the remote machine
4. Executes the update script remotely to configure new hostname and IP
5. Waits for the VM to reboot and come online with new settings
6. Verifies SSH connectivity and hostname configuration

### 2. `show-names` - Display VM Hostnames
**Purpose**: Connects to a range of VMs and displays their IP addresses and hostnames.

**Usage**:
```bash
./show-names [options]
```

**Options**:
- `-s, --start-ip <octet>` - Set start IP (last octet, default: 101)
- `-e, --end-ip <octet>` - Set end IP (last octet, default: 103)
- `-b, --base-ip <base>` - Set base IP (default: 192.168.122.)
- `-h, --help` - Show help message

**Process**:
- Iterates through IP range (e.g., 192.168.122.101 to 192.168.122.103)
- Connects via SSH to each IP using hardcoded user `jdarling` and key `~/.ssh/id_rsa`
- Displays format: `<IP>: <hostname>`

### 3. `new-vm` - Clone Virtual Machine
**Purpose**: Creates a new VM by cloning an existing VM using virt-clone.

**Usage**:
```bash
./new-vm [options]
```

**Options**:
- `-n, --new-vm-name NAME` - Set the new VM name (required)
- `-e, --existing-vm-name NAME` - Set the existing VM name to clone (default: u22-server)
- `-h, --help` - Show help message

**Dependencies**: 
- `virt-clone` command (part of libvirt tools)
- Appropriate permissions to manage VMs via virsh

**Process**:
1. Prompts for new VM name if not provided
2. Detects the disk path of the existing VM
3. Shuts down the source VM if it's running
4. Clones the VM with virt-clone, creating a new disk file
5. The new VM is ready to be started and configured

### 4. `update-vm` - Update VM Configuration
**Purpose**: Updates the hostname and IP address configuration on the local machine (intended to run on the VM being configured).

**Usage**:
```bash
./update-vm [options]
```

**Options**:
- `-n, --hostname <hostname>` - Set the new hostname
- `-i, --ip <ip>` - Set the new IP address
- `-h, --help` - Show help message

**Process**:
1. Updates package repositories
2. Installs `net-tools` if not present (for `ifconfig`)
3. Prompts for hostname and IP if not provided via arguments
4. Disables cloud-init network configuration
5. Updates `/etc/hosts` file (replaces 'u22-base' with new hostname)
6. Sets system hostname using `hostnamectl`
7. Creates static network configuration in `/etc/netplan/50-cloud-init.yaml`
8. Installs Open vSwitch if not present
9. Reboots the system to apply changes

**Network Configuration**:
- Disables DHCP
- Sets static IP with /24 subnet
- Auto-detects gateway (first 3 octets + .1)
- Uses Google DNS servers (8.8.8.8, 8.8.4.4)
- Auto-detects primary network interface

## Workflow Examples

### Method 1: Clone and Configure New VM
1. **Clone a VM** using the new-vm script:
   ```bash
   ./new-vm --new-vm-name my-new-server
   ```
2. **Start the cloned VM** and get its IP:
   ```bash
   virsh start my-new-server
   # Wait for it to boot, then find its IP
   ```
3. **Configure the VM** with new hostname and IP:
   ```bash
   ./init-vm --existing-ip <current-ip> --new-ip 192.168.122.105 --hostname my-new-server
   ```

### Method 2: Direct VM Configuration  
1. **Prepare a base VM** with Ubuntu 22.04 Server and ensure SSH access
2. **Run `init-vm`** to configure the VM with new hostname and IP:
   ```bash
   ./init-vm --existing-ip 192.168.122.114 --new-ip 192.168.122.104 --hostname my-server
   ```
3. **Use `show-names`** to verify multiple VMs are configured correctly:
   ```bash
   ./show-names --start-ip 101 --end-ip 105
   ```

## Prerequisites

- KVM/QEMU hypervisor environment
- SSH key-based authentication set up
- Ubuntu-based VMs (scripts assume Ubuntu package management and systemd)
- Network access between host and VMs on 192.168.122.x subnet

## Security Notes

- Scripts use SSH key authentication for secure connections
- Password authentication is available as fallback during initial setup
- Network configurations use static IPs for predictable VM addressing
- Open vSwitch is installed for advanced networking capabilities

## Limitations

- Hardcoded network subnet (192.168.122.x)
- Assumes Ubuntu/Debian-based systems  
- `show-names` script has hardcoded username 'jdarling'
- `new-vm` shuts down source VM during cloning process
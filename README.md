# Ansible Inventory Updater
This script adds and deletes hosts from the ansible hosts file. It will backup the hosts file and reverse the changes in case something goes wrong.
## Usage example:
```
./inventory_updater print_hosts_file
all:
  children:
    lxc:
      hosts:
        test 1:
          ansible_host: 192.168.1.100
          ansible_python_interpreter: /usr/bin/python3
    ungrouped: {}

./inventory_updater --group lxc set_host test2 192.168.1.101
./inventory_updater print_hosts_file 
all:
  children:
    lxc:
      hosts:
        test 1:
          ansible_host: 192.168.1.100
          ansible_python_interpreter: /usr/bin/python3
        test 2:
          ansible_host: 192.168.1.101
          ansible_python_interpreter: /usr/bin/python3
    ungrouped: {}

./inventory_updater --group lxc delete_host test 
./inventory_updater print_hosts_file  
all:
  children:
    lxc:
      hosts:
        test 1:
          ansible_host: 192.168.1.100
          ansible_python_interpreter: /usr/bin/python3
    ungrouped: {}
```
from logging import warning
import yaml
import argparse
import os
import datetime
import sys

class AnsibleInventoryEditor:
    def __init__(self, group, ansible_hosts_file):
        self._hosts = None
        self._group = group
        self._ansible_hosts_file = ansible_hosts_file
        if os.access(os.path.dirname(self._ansible_hosts_file), os.W_OK) and os.access(os.path.dirname(self._ansible_hosts_file), os.R_OK):
            if os.path.exists(self._ansible_hosts_file):
                if os.stat("file").st_size > 0:
                    if os.access(self._ansible_hosts_file, os.W_OK) and os.access(self._ansible_hosts_file, os.R_OK):
                        with open(self._ansible_hosts_file, "r") as stream:
                            self._hosts = yaml.safe_load(stream)
                    else:
                        error('File: ' + self._ansible_hosts_file +
                              ' is not read and/or writeable! Check permissions!')
                else:
                    warning('File: ' + self._ansible_hosts_file + 'Is empty!')
                    self._hosts = {'all': {'children': {'ungrouped': {}}}}
                    self._write_ansible_hosts_file(True, 0)
            else:
                warning('File: ' + self._ansible_hosts_file +
                        'Does not exists! Creating new ansible hosts file')
                self._hosts = {'all': {'children': {'ungrouped': {}}}}
                self._write_ansible_hosts_file(True, 0)
        else:
            error('Directory: ' + os.path.dirname(self._ansible_hosts_file) +
                  ' is not read and/or writeable! Check permissions!')

    def _write_ansible_hosts_file(self, no_backup, backups_to_keep):
        if not no_backup:
            modifiedTime = os.path.getmtime(self._ansible_hosts_file)
            timeStamp = datetime.datetime.fromtimestamp(
                modifiedTime).strftime("%Y-%m-%d_%H-%M-%S")
            os.rename(self._ansible_hosts_file,
                      self._ansible_hosts_file + '_' + timeStamp)

        with open(self._ansible_hosts_file, "w") as stream:
            try:
                yaml.safe_dump(self._hosts, stream, default_flow_style=False)
            except Exception:
                os.rename(self._ansible_hosts_file + '_' +
                          timeStamp, self._ansible_hosts_file)
                raise

        if not no_backup:
            _, _, files = next(
                os.walk(os.path.dirname(self._ansible_hosts_file)))
            if len(files) > backups_to_keep:
                files.sort()
                os.remove(os.path.join(os.path.dirname(
                    self._ansible_hosts_file), files[0]))

    def check_if_hostname_is_taken(self, hostname):
        return hostname in list(self._hosts['all']['children'][self._group]['hosts'].keys())

    def check_if_ip_is_taken(self, ip_address):
        ip_address_taken = False
        for host_data in list(self._hosts['all']['children'][self._group]['hosts'].values()):
            if ip_address == host_data['ansible_host']:
                ip_address_taken = True
        return ip_address_taken

    def get_hostname_form_ip(self, ip_address):
        if self.check_if_ip_is_taken(ip_address):
            for hostname, host_data in self._hosts['all']['children'][self._group]['hosts'].items():
                if ip_address == host_data['ansible_host']:
                    return hostname
        else:
            error('The IP-Address: ' + ip_address + ' not found')

    def update_ip_address(self, hostname, ip_address, no_backup, backups_to_keep):
        self._hosts['all']['children'][self._group]['hosts'][hostname]['ansible_host'] = ip_address
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def set_host(self, hostname, ip_address, ansible_python_interpreter, no_backup, backups_to_keep):
        if self.check_if_hostname_is_taken(hostname):
            error('The Hostname: ' + hostname + ' allready exists')

        if self.check_if_ip_is_taken(ip_address):
            error('IP:' + host_data['ansible_host'] +
                    'is already take by: ' + self.get_hostname_form_ip(ip_address))

        self._hosts['all']['children'][self._group]['hosts'][hostname] = {
            'ansible_host': ip_address,
            'ansible_python_interpreter': ansible_python_interpreter
        }
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def delete_host(self, hostname, no_backup, backups_to_keep):
        self._hosts['all']['children'][self._group]['hosts'].pop(
            hostname)
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def print_ansible_hosts_file(self, json):
        print(yaml.dump(self._hosts, default_flow_style=json))

    def print_hosts(self):
        for hostname, host_data in self._hosts['all']['children'][self._group]['hosts'].items():
            print(hostname + ': ' + host_data['ansible_host'])


# Parser
parser = argparse.ArgumentParser(
    prog='ansible_inventory_editor', description='This script will add or delete entries in your ansible inventory')
parser.add_argument('--hosts_file', metavar='PATH',
                    default='/etc/ansible/hosts',
                    help='Path to your ansible hosts file')
parser.add_argument('--group', metavar='GROUP',
                    default='ungrouped',
                    help='Ansible Inventory group')

subparsers = parser.add_subparsers(title='subcommands', dest='command',
                                   help='For additional help type: ansible_inventory_editor COMMAND --help')

parser_print_hosts = subparsers.add_parser(
    'print_hosts', help='Print all host and IP\'s of the group')

parser_print_ansible_hosts_file = subparsers.add_parser(
    'print_hosts_file', help='Print the ansible hosts file')
parser_print_ansible_hosts_file.add_argument(
    '--json', action='store_true', help='Print in json format')

parser_set_host = subparsers.add_parser(
    'set_host', help='Add new host to the ansible hosts file')
parser_set_host.add_argument(
    'hostname', metavar='NAME', type=str, help='Name of the host')
parser_set_host.add_argument(
    'ip_address', metavar='IP', type=str, help='IP of the host')
parser_set_host.add_argument('--path', metavar='PATH', default='/usr/bin/python3',
                             type=str, help='Ansible python interpreter path on host')
parser_set_host.add_argument('--keep', metavar='N', default=10,
                             type=int, help='Backups to keep of the ansible hosts file')
parser_set_host.add_argument(
    '--no_backup', action='store_true', help='DON\'T (!!!) Backup ansible hosts file')

parser_delete_host = subparsers.add_parser(
    'delete_host', help='Delete a host from the ansible hosts file')
parser_delete_host.add_argument(
    'hostname', metavar='NAME', type=str, help='Name of the host')
parser_delete_host.add_argument('--keep', metavar='N', default=10,
                                type=int, help='Backups to keep of the ansible hosts file')
parser_delete_host.add_argument(
    '--no_backup', action='store_true', help='DON\'T (!!!) Backup ansible hosts file')

parser_update_ip_address = subparsers.add_parser(
    'update_ip_address', help='Update IP address of host in ansible hosts file')
parser_update_ip_address.add_argument(
    'hostname', metavar='NAME', type=str, help='Name of the host')
parser_update_ip_address.add_argument(
    'ip_address', metavar='IP', type=str, help='New IP of the host')
parser_update_ip_address.add_argument('--keep', metavar='N', default=10,
                                type=int, help='Backups to keep of the ansible hosts file')
parser_update_ip_address.add_argument(
    '--no_backup', action='store_true', help='DON\'T (!!!) Backup ansible hosts file')

if len(sys.argv) == 1:
    parser.print_help()

args = parser.parse_args()

ansible_invetory_editor = AnsibleInventoryEditor(
    group=args.group,
    ansible_hosts_file=args.hosts_file
)

if args.command == 'print_hosts':
    ansible_invetory_editor.print_hosts()

if args.command == 'print_hosts_file':
    ansible_invetory_editor.print_ansible_hosts_file(json=args.json)

if args.command == 'set_host':
    ansible_invetory_editor.set_host(
        hostname=args.hostname,
        ip_address=args.ip_address,
        ansible_python_interpreter=args.path,
        backups_to_keep=args.keep,
        no_backup=args.no_backup
    )

if args.command == 'delete_host':
    ansible_invetory_editor.delete_host(
        hostname=args.hostname,
        backups_to_keep=args.keep,
        no_backup=args.no_backup
    )

if args.command == 'update_ip_address':
    ansible_invetory_editor.update_ip_address(
        hostname=args.hostname,
        ip_address=args.ip_address,
        backups_to_keep=args.keep,
        no_backup=args.no_backup
    )
    
if args.command == 'get_hostname_form_ip':
    ansible_invetory_editor.get_hostname_form_ip(
        ip_address=args.ip_address
    )

if args.command == 'check_if_ip_is_taken':
    ansible_invetory_editor.check_if_ip_is_taken(
        ip_address=args.ip_address
    )

if args.command == 'check_if_hostname_is_taken':
    ansible_invetory_editor.check_if_hostname_is_taken(
        hostname=args.hostname
    )

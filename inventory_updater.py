from logging import warning
import yaml
import argparse
import os
import datetime
import sys

class InventoryAdhocUpdater:
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

    def set_host(self, container_name, container_ip, ansible_python_interpreter, no_backup, backups_to_keep):
        if container_name in list(self._hosts['all']['children'][self._group]['hosts'].keys()):
            error('The Hostname: ' + container_name + ' allready exists')

        for host_name, host_data in self._hosts['all']['children']['lxc']['hosts'].items():
            if container_ip == host_data['ansible_host']:
                error('IP:' + host_data['ansible_host'] +
                      'is already take by: ' + host_name)

        self._hosts['all']['children']['lxc']['hosts'][container_name] = {
            'ansible_host': container_ip,
            'ansible_python_interpreter': ansible_python_interpreter
        }
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def delete_host(self, container_name, no_backup, backups_to_keep):
        self._hosts['all']['children'][self._group]['hosts'].pop(
            container_name)
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def print_ansible_hosts_file(self, json):
        print(yaml.dump(self._hosts, default_flow_style=json))

    def print_hosts(self):
        for host_name, host_data in self._hosts['all']['children'][self._group]['hosts'].items():
            print(host_name + ': ' + host_data['ansible_host'])


# Parser
parser = argparse.ArgumentParser(
    prog='inventory_updater', description='This script will add or delete entries in your ansible inventory')
parser.add_argument('--hosts_file', metavar='PATH',
                    default='/etc/ansible/hosts',
                    help='Path to your ansible hosts file')
parser.add_argument('--group', metavar='GROUP',
                    default='ungrouped',
                    help='Ansible Inventory group')

subparsers = parser.add_subparsers(title='subcommands', dest='command',
                                   help='For additional help type: inventory_updater COMMAND --help')

parser_print_hosts = subparsers.add_parser(
    'print_hosts', help='Print all host and IP\'s of the group')

parser_print_ansible_hosts_file = subparsers.add_parser(
    'print_hosts_file', help='Print the ansible hosts file')
parser_print_ansible_hosts_file.add_argument(
    '--json', action='store_true', help='Print in json format')

parser_set_host = subparsers.add_parser(
    'set_host', help='Add new host to the ansible hosts file')
parser_set_host.add_argument(
    'container_name', metavar='NAME', type=str, help='Name of the container')
parser_set_host.add_argument(
    'container_ip', metavar='IP', type=str, help='IP of the container')
parser_set_host.add_argument('--path', metavar='PATH', default='/usr/bin/python3',
                             type=str, help='Ansible python interpreter path on host')
parser_set_host.add_argument('--keep', metavar='N', default=10,
                             type=int, help='Backups to keep of the ansible hosts file')
parser_set_host.add_argument(
    '--no_backup', action='store_true', help='DON\'T (!!!) Backup ansible hosts file')

parser_delete_host = subparsers.add_parser(
    'delete_host', help='Delete a host from the ansible hosts file')
parser_delete_host.add_argument(
    'container_name', metavar='NAME', type=str, help='Name of the container')
parser_delete_host.add_argument('--keep', metavar='N', default=10,
                                type=int, help='Backups to keep of the ansible hosts file')
parser_delete_host.add_argument(
    '--no_backup', action='store_true', help='DON\'T (!!!) Backup ansible hosts file')

if len(sys.argv) == 1:
    parser.print_help()

args = parser.parse_args()

invetory_adhoc_updater = InventoryAdhocUpdater(
    group=args.group,
    ansible_hosts_file=args.hosts_file
)

if args.command == 'print_hosts':
    invetory_adhoc_updater.print_hosts()

if args.command == 'print_hosts_file':
    invetory_adhoc_updater.print_ansible_hosts_file(json=args.json)

if args.command == 'set_host':
    invetory_adhoc_updater.set_host(
        container_name=args.container_name,
        container_ip=args.container_ip,
        ansible_python_interpreter=args.path,
        backups_to_keep=args.keep,
        no_backup=args.no_backup
    )

if args.command == 'delete_host':
    invetory_adhoc_updater.delete_host(
        container_name=args.container_name,
        backups_to_keep=args.keep,
        no_backup=args.no_backup
    )

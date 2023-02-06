import argparse
import sys
from ansible_inventory_editor.editor import AnsibleInventoryEditor, AnsibleInventoryEditorError

def main():
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

if __name__ == "__main__":
    try:
        main()
    except AnsibleInventoryEditorError:
        sys.exit(1)

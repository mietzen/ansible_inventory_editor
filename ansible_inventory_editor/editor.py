import yaml
import os
import datetime
import logging

class AnsibleInventoryEditor:
    def __init__(self, group, ansible_hosts_file):
        self._hosts = None
        self._group = group
        self._ansible_hosts_file = ansible_hosts_file
        logging.basicConfig(
            format='%(levelname)s: %(message)s', level=logging.DEBUG)
        if os.access(os.path.dirname(self._ansible_hosts_file), os.W_OK) and os.access(os.path.dirname(self._ansible_hosts_file), os.R_OK):
            if os.path.exists(self._ansible_hosts_file):
                if os.stat(self._ansible_hosts_file).st_size > 0:
                    if os.access(self._ansible_hosts_file, os.W_OK) and os.access(self._ansible_hosts_file, os.R_OK):
                        with open(self._ansible_hosts_file, "r") as stream:
                            self._hosts = yaml.safe_load(stream)
                    else:
                        logging.error('File: ' + self._ansible_hosts_file +
                                ' is not read and/or writeable! Check permissions!')
                else:
                    logging.warning(
                        'File: ' + self._ansible_hosts_file + 'Is empty!')
                    self._hosts = {'all': {'children': {'ungrouped': {}}}}
                    self._write_ansible_hosts_file(True, 0)
            else:
                logging.warning('File: ' + self._ansible_hosts_file +
                                'Does not exists! Creating new ansible hosts file')
                self._hosts = {'all': {'children': {'ungrouped': {}}}}
                self._write_ansible_hosts_file(True, 0)
        else:
            logging.error('Directory: ' + os.path.dirname(self._ansible_hosts_file) +
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
                    self._ansible_hosts_file), files[1]))

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
            logging.warning('The IP-Address: ' + ip_address + ' not found')

    def update_ip_address(self, hostname, ip_address, no_backup, backups_to_keep):
        self._hosts['all']['children'][self._group]['hosts'][hostname]['ansible_host'] = ip_address
        self._write_ansible_hosts_file(no_backup, backups_to_keep)

    def set_host(self, hostname, ip_address, ansible_python_interpreter, no_backup, backups_to_keep):
        if self.check_if_hostname_is_taken(hostname):
            logging.warning('The Hostname: ' + hostname + ' allready exists')

        if self.check_if_ip_is_taken(ip_address):
            logging.warning('IP: ' + ip_address +
                            ' is already take by: ' + self.get_hostname_form_ip(ip_address))

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

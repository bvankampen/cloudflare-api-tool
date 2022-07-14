#!/usr/bin/env python3

"""Cloudflare API Tool.

Usage:
    cf-api-tool.py get [--json] [--long]
    cf-api-tool.py get <name> [--json] [--long]
    cf-api-tool.py delete <name>
    cf-api-tool.py update <name> <type> <content> [--proxy]
    cf-api-tool.py (-h | --help)
    cf-api-tool.py --version

Options:
    -h --help   Show this screen
    --version   Show version
    --proxy     Proxy in case of CNAME (default not)
    --json      Print output as json
    --long      Print long format (default not)

"""

import CloudFlare
import configparser
import os.path
from docopt import docopt

from sys import argv

from pprint import pprint

CONFIG_FILE = '~/.config/cloudflare/config.ini'


class Output:

    def print_long(self, record):
        print(f"Name    : {record['name']}")
        print(f"Type    : {record['type']}")
        print(f"Content : {record['content']}")
        print(f"TTL     : {record['ttl']}")
        print(f"Proxied : {record['proxied']}")
        print()

    def print_short(self, record):
        name = f"{record['name']}."
        print(
            f"{name:50} {str(record['ttl']):7} IN      {record['type']:7} {record['content']}")

    def print(self, data, as_json=False, as_long=False):
        for record in data:
            if as_json:
                print(record)
            elif as_long:
                self.print_long(record)
            else:
                self.print_short(record)


class CloudflareApi:

    def __init__(self, token, domain):
        self.domain = domain
        self.cf = CloudFlare.CloudFlare(token=token)
        self.zone = self.cf.zones.get(
            params={'name': domain, 'per_page': 1})[0]

    def check_name(self, name):
        if self.domain not in name:
            return f"{name}.{self.domain}"
        else:
            return name

    def get_record_from_cf(self, name):
        record = self.cf.zones.dns_records.get(
            self.zone['id'], params={'name': name})
        if len(record) == 0:
            return None
        else:
            return record[0]

    def get_record(self, name):
        name = self.check_name(name)
        return self.cf.zones.dns_records.get(self.zone['id'], params={'name': name})

    def get_all_records(self):
        return self.cf.zones.dns_records.get(self.zone['id'])

    def update_record(self, name, type, content, proxy=False):
        name = self.check_name(name)
        record = self.get_record_from_cf(name)

        dns_record = {
            'name': name,
            'type': type,
            'content': content
        }

        if proxy:
            dns_record['proxied'] = True
        else:
            dns_record['proxied'] = False

        if record == None:
            self.cf.zones.dns_records.post(
                self.zone['id'],
                data=dns_record
            )
        else:
            self.cf.zones.dns_records.put(
                self.zone['id'],
                record['id'],
                data=dns_record
            )

    def delete_record(self, name):
        name = self.check_name(name)
        record = self.get_record_from_cf(name)
        if record != None:
            self.cf.zones.dns_records.delete(
                self.zone['id'],
                record['id'],
            )


def main():
    config = configparser.ConfigParser()

    if not os.path.exists(os.path.expanduser(CONFIG_FILE)):
        print(f"Config file {CONFIG_FILE} doesn't exists")
        exit(1)

    config.read(os.path.expanduser(CONFIG_FILE))

    args = docopt(__doc__, version='Cloudflare API Tool 1.0')

    cf = CloudflareApi(config['DEFAULT']['Token'], config['DEFAULT']['Domain'])
    output = Output()

    if args['get']:
        if args['<name>'] == None:
            data = cf.get_all_records()
        else:
            data = cf.get_record(args['<name>'])
        output.print(data, as_json=args['--json'], as_long=args['--long'])

    if args['delete']:
        cf.delete_record(args['<name>'])

    if args['update']:
        cf.update_record(
            args['<name>'],
            args['<type>'],
            args['<content>'],
            args['--proxy']
        )


if __name__ == "__main__":
    main()

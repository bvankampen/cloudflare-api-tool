#!/usr/bin/env python3

"""Cloudflare API Tool.

Usage:
    cf-api-tool.py get <name>
    cf-api-tool.py delete <name>
    cf-api-tool.py update <name> <type> <content> [--proxy]
    cf-api-tool.py (-h | --help)
    cf-api-tool.py --version

Options:
    -h --help   Show this screen
    --version   Show version
    --proxy     Proxy in case of CNAME (default not)

"""

import CloudFlare
import configparser
import os.path
from docopt import docopt

from sys import argv

from pprint import pprint

CONFIG_FILE = '~/.config/cloudflare/config.ini'

class CloudflareApi:

    def __init__(self, token, domain):
        self.domain = domain
        self.cf = CloudFlare.CloudFlare(token=token)
        self.zone = self.cf.zones.get(
            params={'name': domain, 'per_page': 1})[0]

    def get_record_from_cf(self, name):
        record = self.cf.zones.dns_records.get(
            self.zone['id'], params={'name': name})
        if len(record) == 0:
            return None
        else:
            return record[0]

    def get_record(self, name):
        name = f"{name}.{self.domain}"
        pprint(self.cf.zones.dns_records.get(self.zone['id'], params={'name': name}))

    def update_record(self, name, type, content, proxy=False):
        name = f"{name}.{self.domain}"
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
        name = f"{name}.{self.domain}"
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

    if args['get']:
        cf.get_record(args['<name>'])
    
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

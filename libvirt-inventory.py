#!/usr/bin/python3

import libvirt
import sys
import json
import argparse
import os

#
# Want to create ansible_ssh_host entries for each server.
# _meta is a high level entry in the json output, same level
# as the server groups.
#

NETWORK = os.environ.get('VIRT_NETWORK')
CONNECTION = os.environ.get('VIRT_CONN')
if not NETWORK or not CONNECTION:
    print('Missing variables')
    sys.exit(1)


def addMeta(vmName, inventory):


    return True

def get_inventory():
    #
    # Connect to the hypervisor
    #

    conn = libvirt.open(CONNECTION)
    if conn == None:
        print('Failed to open connection to hypervisor')
        sys.exit(1)

    #
    # Create all the groups in the inventory
    #
    #groups = ['authentication', 'lbssl', 'swiftclient', 'package_cache', 'proxy', 'storage']
    groups = ['elk']
    inventory = {}
    inventory['_meta'] = {}
    for group in groups:
        if not group in inventory:
            inventory[group] = []

    #
    # Find all active vms and add them into the inventory by finding
    # their IP from the default.leases file
    #
    for leases in conn.networkLookupByName(NETWORK).DHCPLeases():
        hostname = leases['hostname']
        ip = leases['ipaddr']
        if 'tower' not in hostname:
            inventory['elk'].append(hostname)
        if not inventory['_meta']:
            inventory['_meta'] = {}
            inventory['_meta']['hostvars'] = {}

        if not hostname in inventory['_meta']:
            inventory['_meta']['hostvars'][hostname] = {}
            inventory['_meta']['hostvars'][hostname]['ansible_ssh_host'] = ip
    return inventory

def get_args(args_list):
    parser = argparse.ArgumentParser(
        description='ansible inventory libvirt')
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    help_list = 'list all hosts libvirt network'
    mutex_group.add_argument('--list', action='store_true', help=help_list)
    help_host = 'display variables for a host'
    mutex_group.add_argument('--host', help=help_host)
    return parser.parse_args(args_list)

def print_list():
    inventory = get_inventory()
    print(json.dumps(inventory, indent=4))

def print_host(host):
    inventory = get_inventory()
    print(json.dumps(inventory['_meta']['hostvars'][host], indent=4))


def main(args_list):

    args = get_args(args_list)
    if args.list:
        print_list()
    if args.host:
        print_host(args.host)


if __name__ == '__main__':
    main(sys.argv[1:])



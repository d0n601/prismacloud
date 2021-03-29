#!/usr/bin/env python3

import sys
import getpass
import argparse
import json
import os
import requests
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



def parse_args():
    """
    CLI argument handling
    """

    desc = 'Create Collection and add Namespace/n'

    epilog = 'The console and user arguments can be supplied using the environment variables TL_CONSOLE and TL_USER.'
    epilog += ' The password can be passed using the environment variable TL_USER_PW.'
    epilog += ' The user will be prompted for the password when the TL_USER_PW variable is not set.'
    epilog += ' The collection and namespace arguments can be suppled using the TL_CLLECTION and TL_NAMESPACE variables.'
    epilog += ' Environment variables override CLI arguments.'

    p = argparse.ArgumentParser(description=desc,epilog=epilog)
    p.add_argument('-c','--console',metavar='TL_CONSOLE', help='query the API of this Console')
    p.add_argument('-u','--user',metavar='TL_USER',help='Console username')
    p.add_argument('-l','--collection',metavar='TL_COLLECTION',help='collection to create')
    p.add_argument('-n','--namespace',metavar='TL_NAMESPACE',help='namespace to add to collection')
    args = p.parse_args()

    # Populate args by env vars if they're set
    envvar_map = {
        'TL_USER':'user',
        'TL_CONSOLE':'console',
        'TL_USER_PW':'password',
        'TL_COLLECTION':'collection',
        'TL_NAMESPACE':'namespace'
    }
    for evar in envvar_map.keys():
        evar_val = os.environ.get(evar,None)
        if evar_val is not None:
            setattr(args,envvar_map[evar],evar_val)

    arg_errs = []
    if getattr(args,'console',None) is None:
        arg_errs.append('console (-c,--console)')
    if getattr(args,'user',None) is None:
        arg_errs.append('user (-u,--user)')
    if getattr(args,'collection',None) is None:
        arg_errs.append('collection (-l,--collection)')
    if getattr(args,'namespace',None) is None:
        arg_errs.append('namespace (-n,--namespace)')

    if len(arg_errs) > 0:
        err_msg = 'Missing argument(s): {}'.format(', '.join(arg_errs))
        p.error(err_msg)

    if getattr(args,'password',None) is None:
        args.password = getpass.getpass('Enter password: ')

    return args

def get_collections_json(console,user,password):
    api_endpt = '/api/v1/collections'
    request_url = console + api_endpt
    collection_req = requests.get(request_url, verify=False, auth=HTTPBasicAuth(user,password))
    return collection_req.text

def create_new_collection(console,user,password,collection_meta):
    print("Create new collection and add namespace")
    api_endpt = '/api/v1/collections'
    request_url = console + api_endpt
    print(request_url)
    collection_req = requests.post(request_url, headers={"Authorization": "Bearer " + console_token}, data=json.dumps(collection_meta), verify=False)
    collection_req = requests.post(
        request_url,
        verify=False,
        data=json.dumps(collection_meta),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(user,password)
    )
    if collection_req.status_code != 200:
        # This means something went wrong.
        raise colRequestError('GET /api/v1/collections {} {}'.format(collection_req.status_code,collection_req.reason))
    return collection_req.text

def check_collection_for_ns(ns,col,collections_str):
    for row in (collections_str.split("\n")):
        if (row):
            collection_dict = json.loads(row[1:])
            if (collection_dict['name'] == col):
                if ns not in collection_dict['namespaces']:
                    collection_dict['namespaces'].append(ns)
                    return (101, collection_dict)
                else:
                    return (102, collection_dict)
    collection_dict = {
        "namespaces": ns,
        "name": col
    }
    return (100, collection_dict)

def main():

    args = parse_args()

    try:
        collections_json = get_collections_json(args.console,args.user,args.password)

    except colRequestError as e:
        print("Error querying API: {}".format(e))
        return 3

    col_status, collection_update_dict = check_collection_for_ns(args.namespace,args.collection,collections_json[:-1])
    if col_status == 100:
        col_put = create_new_collection(args.console,args.user,args.password,collection_update_dict)
    elif col_status == 101:
        print("Add namespace to existing collection")
    else:
        print("Nothing to do here")

    return 0

if __name__ == '__main__':
    sys.exit(main())

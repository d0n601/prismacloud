#!/usr/bin/env python3

import sys
import getpass
import argparse
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import urllib.parse
urllib3.disable_warnings()

# set debug to 0 to enable
debug = 0

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

def print_debug(message):
    if debug == 0:
        print(message)
    return 0

def get_token(console,user,password):
    print_debug("Getting bearer token.")
    api = console + '/api/v1/authenticate'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    print_debug(response)
    token = response.json()['token']
    bearer = "Bearer " + token
    headers = {'content-type':'application/json', 'Authorization': bearer}
    return(headers)

def get_collections(console,auth_headers,collection,namespace):
    print_debug("Getting collections from console.")
    api = console + '/api/v1/collections'
    collection_req = requests.get(api, verify=False, headers=auth_headers)
    print_debug(collection_req)
    return collection_req.text

def process_collections(namespace,collection,collections_str):
    print_debug("Processing collections to look for duplicate.")
    for row in (collections_str.split("\n")):
        if (row):
            collection_dict = json.loads(row[1:])
            if (collection_dict['name'] == collection):
                print_debug("Duplicate collection found, checking for duplicate namespace.")
                if namespace not in collection_dict['namespaces']:
                    collection_dict['namespaces'].append(namespace)
                    print_debug("No duplicate namespace found.  Appending.")
                    return (101, collection_dict)
                else:
                    print_debug("Duplicate collection with duplicate namespace found.")
                    return (102, collection_dict)
    collection_dict = { 
        'namespaces' : [namespace],
        'name' : collection,
        'functions' : ['*'],
        'codeRepos' : ['*'],
        'accountIDs' : ['*'],
        'clusters' : ['*'],
        'containers' : ['*'],
        'hosts' : ['*'],
        'images' : ['*'],
        'labels' : ['*'],
        'appIDs' : ['*']
    }
    print_debug("No collection found.  Will need to make one.")
    return (100, collection_dict)

def process_vuln_deployed_pol(collection,vuln_deployed_pol_str):
    print_debug("Analyze current Deployed Image Vulnerability rules to see if duplicate exists.")
    deploy_vulns_dict = json.loads(vuln_deployed_pol_str)
    for top_key in deploy_vulns_dict.keys():
        if (top_key == 'rules'):
            rule_exists = 100
            for rule in (deploy_vulns_dict[top_key]):
                if ((rule['name']) == collection):
                    print_debug("Duplicate rule exists.  No need to create.")
                    rule_exists = 0
    if (rule_exists != 0):
        print_debug("Rule doesn't exist.  Will need to create new and add collection to scope.")
        new_rule_pol = {
            'name' : collection,
            'collections' : [ { 'name' : collection } ],
            'effect' : 'alert'
        }
        print_debug("Adding new rule to top of policy json.")
        deploy_vulns_dict['rules'].insert(0, new_rule_pol)
    return (rule_exists, deploy_vulns_dict)

def new_collection(console,auth_headers,payload):
    print_debug("Creating new collection.")
    api = console + '/api/v1/collections'
    response = requests.post(api, headers=auth_headers, data=json.dumps(payload), verify=False)
    print_debug(response)
    if response.ok:
        return 0
    else:
        return 1

def update_collection(console,auth_headers,collection,payload):
    print_debug("Updating existing collection.")
    collection = urllib.parse.quote(collection)
    api = console + '/api/v1/collections/' + collection
    response = requests.put(api, headers=auth_headers, data=json.dumps(payload), verify=False)
    print_debug(response)
    if response.ok:
        return 0
    else:
        return 1

def get_vuln_deployed_pol(console,auth_headers,collection):
    print_debug("Get current Deployed Image Vulnerability rules.")
    collection = urllib.parse.quote(collection)
    api = console + '/api/v1/policies/vulnerability/images'
    deployed_vuln_pol_req = requests.get(api, verify=False, headers=auth_headers)
    print_debug(deployed_vuln_pol_req)
    return deployed_vuln_pol_req.text

def update_vuln_deployed_pol(console,auth_headers,payload):
    print_debug("Updating Deployed Image Vulnerability rules with new matching collection scope.")
    api = console + '/api/v1/policies/vulnerability/images'
    response = requests.put(api, headers=auth_headers, data=json.dumps(payload), verify=False)
    print_debug(response)
    if response.ok:
        return 0
    else:
        return 1
    return 0

def main():
    # load argumants
    args = parse_args()
    # return bearer token
    headers = get_token(args.console,args.user,args.password)
    # return all collections structured as json in string
    collections_json = get_collections(args.console,headers,args.collection,args.namespace)
    # process collections, comparing to desired new collection and namespace
    col_status, collection_update_dict = process_collections(args.namespace,args.collection,collections_json[:-1])
    # based on col_status, either create new collection with namespace (100) or add namespace to existing collection (101)
    if col_status == 100:
        if (new_collection(args.console,headers,collection_update_dict) != 0):
            print("Error creating new collection")
            sys.exit(1)
    elif col_status == 101:
        if (update_collection(args.console,headers,args.collection,collection_update_dict) != 0):
            print("Error add namespace to existing collection")
            sys.exit(1)
    else:
        print("Collection exists with namespace already added.")
    # return all vulnerability image deployed rules as string
    vuln_pol_json = get_vuln_deployed_pol(args.console,headers,args.collection)
    # process the rules to see if we need to add a new one for the new collection
    vuln_dep_status, vuln_deployed_pol_dict = process_vuln_deployed_pol(args.collection,vuln_pol_json)
    # based on the vuln_dep_status, add new rule to the deployed images vuln policy
    if vuln_dep_status == 100:
        if (update_vuln_deployed_pol(args.console,headers,vuln_deployed_pol_dict) != 0):
            print("Error adding new rule to Deployed Vulnerabilities policy")
            sys.exit(1)
    print_debug("Success")
    return 0

if __name__ == '__main__':
    sys.exit(main())
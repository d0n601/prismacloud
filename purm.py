#!/usr/bin/env python3

# Prisma User Role Manager

import os
import sys
import getpass
import argparse
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import urllib.parse
urllib3.disable_warnings()

# set debug to 0 to enable
debug = 0

def parseArgs():
    """
    CLI argument handling
    """

    desc = 'Create Prisma Cloud User Account'

    epilog = 'The console and user arguments can be supplied using the environment variables PC_CONSOLE and PC_USER.'
    epilog += ' The password can be passed using the environment variable PC_USER_PW.'
    epilog += ' The user will be prompted for the password when the PC_USER_PW variable is not set.'
    epilog += ' Environment variables override CLI arguments.'

    p = argparse.ArgumentParser(description=desc,epilog=epilog)
    p.add_argument('-c','--console',metavar='CONSOLE',help='query the API of this Console')
    p.add_argument('-pcu','--pcuser',metavar='USER',help='Prisma Cloud Console username')
    args = p.parse_args()

    # Populate args by env vars if they're set
    envvar_map = {
        'PC_CONSOLE':'console',
        'PC_USER':'pcuser',
        'PC_USER_PW':'password'
    }
    for evar in envvar_map.keys():
        evar_val = os.environ.get(evar,None)
        if evar_val is not None:
            setattr(args,envvar_map[evar],evar_val)

    arg_errs = []
    if getattr(args,'console',None) is None:
        arg_errs.append('console (-c,--console)')
    if getattr(args,'pcuser',None) is None:
        arg_errs.append('user (-pcu,--pcuser)')

    if len(arg_errs) > 0:
        err_msg = 'Missing argument(s): {}'.format(', '.join(arg_errs))
        p.error(err_msg)

    if getattr(args,'password',None) is None:
        args.password = getpass.getpass('Enter password: ')

    return args

def printDebug(message):
    if debug == 0:
        print(message)
    return 0

def getToken(console,user,password):
    printDebug("Getting bearer token.")
    api = console + '/login'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    printDebug(response)
    token = response.json()['token']
    bearer = "Bearer " + token
    headers = {'content-type':'application/json', 'Authorization': bearer}
    return(headers)


def main():
    # load argumants
    args = parseArgs()
    # return bearer token
    headers = getToken(args.console,args.pcuser,args.password)
    print(headers['Authorization'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3

import sys
import json
import getpass
import argparse
import os
import requests
from requests.auth import HTTPBasicAuth
import urllib3
import urllib.parse
urllib3.disable_warnings()

debug = 0

def parse_args():
    parser = argparse.ArgumentParser(description='Connect Infomration')
    parser.add_argument('--pcc_console', dest='pccConsole', type=str, help='Prisma Cloud Compute API URL', required=True)
    parser.add_argument('--api_key', dest='apiKey', type=str, help='API Key', required=True)
    parser.add_argument('--api_secret', dest='apiSecret', type=str, help='API Secret')
    args = parser.parse_args()
    if getattr(args,'apiSecret',None) is None:
        args.api_secret = getpass.getpass('Enter password: ')
    return args

def printDebug(message):
    if debug == 0:
        print(message)
    return 0

def getPCCToken(console,user,password):
    printDebug("\nGetting PCC bearer token.")
    api = console + '/api/v1/authenticate'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    printDebug(response)
    token = response.json()['token']
    return(token)

def getActiveIncidents(console,token):
    allIncidents=[]
    printDebug("\nGetting all PCC Active Compute Incidents")
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    url = console + '/api/v1/audits/incidents?acknowledged=false'
    response = requests.get(url, headers=auth_headers, verify=False) 
    printDebug(response)
    for incident in json.loads(response.text):
        allIncidents.append(incident["_id"])
    return allIncidents

def archiveIncidents(console,token,incidents):
    printDebug("\nArchiving incidents: ")
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    for incident in incidents:
        api = console + '/api/v1/audits/incidents/acknowledge/' + incident
        response = requests.patch(api, headers=auth_headers, data="{\"acknowledged\":true}", verify=False)
        if response.status_code == 200:
            printDebug("\t" + incident + " Successfully archived")
        else:
            printDebug("\t" + incident + " Failed archiving")

def main():
    args = parse_args()
    pccToken = getPCCToken(args.pccConsole,args.apiKey,args.apiSecret)
    allActiveIncidents = getActiveIncidents(args.pccConsole,pccToken)
    while allActiveIncidents:
        archiveIncidents(args.pccConsole,pccToken,allActiveIncidents)
        allActiveIncidents = getActiveIncidents(args.pccConsole,pccToken)

if __name__ == '__main__':
    sys.exit(main())

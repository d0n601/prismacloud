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

# Set debug to 0 for logging
debug = 1

def parse_args():
    parser = argparse.ArgumentParser(description='Connect Infomration')
    parser.add_argument('--pc_console', dest='pcConsole', type=str, help='Prisma Cloud API URL', required=True)
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

def getPCToken(console,user,password):
    printDebug("\nGetting PC bearer token.")
    api = console + '/login'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    printDebug(response)
    token = response.json()['token']
    return(token)

def getAlertsV2(console,token):
    printDebug("\nGetting Alerts.")
    headers = {
        'content-type':'application/json',
        'x-redlock-auth': token
    }
    url = console + '/v2/alert'
    query = {
        "detailed": "false",
        "fields": [
          "alert.id",
          "alert.status",
          "alert.time"
        ],
        "filters": [
          {
            "name":"timeRange.type",
            "operator":"=",
            "value":"ALERT_UPDATED"
          }
        ],
        "timeRange": {
          "relativeTimeType": "BACKWARD",
          "type": "relative",
          "value": {
            "amount": 7,
            "unit": "day"
          }
        }
    }
    response = requests.post(url, headers=headers, json=query)
    printDebug(response)
    return (response.text)

def main():
    args = parse_args()
    pcToken = getPCToken(args.pcConsole,args.apiKey,args.apiSecret)
    printDebug (pcToken)
    alerttext = getAlertsV2 (args.pcConsole,pcToken)
    print(alerttext)

if __name__ == '__main__':
    sys.exit(main())
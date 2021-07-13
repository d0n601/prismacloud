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
    parser.add_argument('--pc_console', dest='pcConsole', type=str, help='Prisma Cloud API URL', required=True)
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

def getPCToken(console,user,password):
    printDebug("\nGetting PC bearer token.")
    api = console + '/login'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    printDebug(response)
    token = response.json()['token']
    return(token)

def getPCCToken(console,user,password):
    printDebug("\nGetting PCC bearer token.")
    api = console + '/api/v1/authenticate'
    data = {'username': user, 'password': password}
    response = requests.post(api, json=data, verify=False)
    printDebug(response)
    token = response.json()['token']
    return(token)

def getPCAzureAccounts(console,token):
    azureAccounts = dict()
    printDebug("\nGetting all PC Azure Accounts in Root Tenant")
    headers = {
        'content-type':'application/json',
        'x-redlock-auth': token
    }
    parent_id = "eb06985d-06ca-4a17-81da-629ab99f6505"
    url = console + "/cloud/azure/"+parent_id+"/project"
    query = {
       'excludeAccountGropupDetails':'true'
    }
    response = requests.get(url, headers=headers, params=query, verify=False)
    printDebug(response)
    for account in json.loads(response.text):
        #printDebug(account['accountId'] +" = "+account['name'])
        azureAccounts[account['accountId']] = account['name'] 
    return azureAccounts

def getPCCCredentials(console,token):
    azureCreds = []
    printDebug("\nGetting all PCC Mapped PC Azure Creds")
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    url = console + '/api/v1/credentials'
    response = requests.get(url, headers=auth_headers, verify=False)
    printDebug(response)
    credDictList = json.loads(response.text)
    for credRow in credDictList:
        if (credRow["type"] == "azure"):
            azureCreds.append(credRow["_id"])
    printDebug("Found " + str(len(azureCreds)) + " Azure Credentials")
    return azureCreds

def getPccAddAccounts(pcAccounts,pccAccounts):
    acctsToAdd = {key:val for key, val in pcAccounts.items() if val not in pccAccounts}
    # returns all accounts to be added in a dict with key = id and value = name
    return acctsToAdd

def setUpPCCAccounts(console,token,addAccountsToPCC):
    printDebug("\nSetting up PCC Accounts")
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    api = console + '/api/v1/credentials'
    for acct in addAccountsToPCC:
        printDebug("Setting up account "+addAccountsToPCC[acct])
        data = {
            '_id': addAccountsToPCC[acct],
            'accountID': acct,
            'type': 'azure'
        }
        #response = requests.post(api, json=data, headers=auth_headers, verify=False)
        #printDebug(response)
    

def main():
    args = parse_args()
    pcToken = getPCToken(args.pcConsole,args.apiKey,args.apiSecret)
    pccToken = getPCCToken(args.pccConsole,args.apiKey,args.apiSecret)
    pcAzureAccounts = getPCAzureAccounts(args.pcConsole,pcToken)
    pccAzureCredentials = getPCCCredentials(args.pccConsole,pccToken)
    addAccountsToPCC = getPccAddAccounts(pcAzureAccounts,pccAzureCredentials)
    setUpPCCAccounts(args.pccConsole,pccToken,addAccountsToPCC)

if __name__ == '__main__':
    sys.exit(main())
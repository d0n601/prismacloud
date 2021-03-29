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


# set debug to 0 to enable
debug = 0

def parse_args():
    """
    CLI argument handling
    """

    desc = 'Extract Azure Container Registry URLs from Prisma Cloud/n'

    epilog = 'The console and user arguments can be supplied using the environment variables TL_CONSOLE and TL_USER.'
    epilog += ' The password can be passed using the environment variable TL_USER_PW.'
    epilog += ' The user will be prompted for the password when the TL_USER_PW variable is not set.'
    epilog += ' The collection and namespace arguments can be suppled using the TL_CLLECTION and TL_NAMESPACE variables.'
    epilog += ' Environment variables override CLI arguments.'

    p = argparse.ArgumentParser(description=desc,epilog=epilog)
    p.add_argument('-pccc','--pcc-console',metavar='PCC_CONSOLE', help='query the API of this Console')
    p.add_argument('-pcc','--pc-console',metavar='PC_CONSOLE', help='query the API of this Console')
    p.add_argument('-k','--api-key',metavar='API_KEY',help='API Key')
    p.add_argument('-rc','--registry-credential',metavar='REG_CRED',help='Registry Credential')
    args = p.parse_args()

    # Populate args by env vars if they're set
    envvar_map = {
        'API_KEY':'apiKey',
        'API_SECRET':'apiSecret',
        'PCC_CONSOLE':'pccConsole',
        'PC_CONSOLE':'pcConsole',
        'REG_CRED':'regCred'
    }
    for evar in envvar_map.keys():
        evar_val = os.environ.get(evar,None)
        if evar_val is not None:
            setattr(args,envvar_map[evar],evar_val)

    arg_errs = []
    if getattr(args,'pcConsole',None) is None:
        arg_errs.append('pcConsole (-pcc,--pc-console)')
    if getattr(args,'pccConsole',None) is None:
        arg_errs.append('pccConsole (-pccc,--pcc-console)')
    if getattr(args,'apiKey',None) is None:
        arg_errs.append('apiKey (-k,--api-key)')
    if getattr(args,'regCred',None) is None:
        arg_errs.append('regCred (-rc,--registry-credential)')

    if len(arg_errs) > 0:
        err_msg = 'Missing argument(s): {}'.format(', '.join(arg_errs))
        p.error(err_msg)

    if getattr(args,'apiSecret',None) is None:
        args.password = getpass.getpass('Enter API Secret: ')

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

def getACRLoginServers(console,token):
    printDebug("\nGetting all ACR Registries")
    headers = {
        "accept": "text/csv; charset=UTF-8",
        "content-type": "application/json; charset=UTF-8",
        "x-redlock-auth": token
    }
    url = console + '/search/config'
    payload = "{\"timeRange\":{\"value\":{\"unit\":\"hour\",\"amount\":24},\"type\":\"relative\"},\"withResourceJson\":true,\"query\":\"config from cloud.resource where api.name = 'azure-container-registry' addcolumn properties.loginServer \"}"
    response = requests.request("POST", url, data=payload, headers=headers)
    printDebug(response)
    ACRList = []
    for row in (response.text.splitlines())[2:]:
        ACRInfoList = row.split(",")
        printDebug("Found Azure Container Registry: " + ACRInfoList[-1])
        ACRList.append(ACRInfoList[-1])
    printDebug("Found " + str(len(ACRList)) + " Azure Container Registries")
    return(ACRList)

def getPCCCreds(console,token):
    azureCreds = []
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    printDebug("\nGetting all PCC Credentials")
    url = console + '/api/v1/credentials'
    response = requests.get(url, headers=auth_headers, verify=False)
    printDebug(response)
    credDictList = json.loads(response.text)
    for credRow in credDictList:
        if (credRow["type"] == "azure"):
            print("Found Azure Credential: " + credRow["_id"])
            azureCreds.append(credRow["_id"])
    printDebug("Found " + str(len(azureCreds)) + " Azure Credentials")
    return(azureCreds)

def getPCCRegistries(console,token):
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    printDebug("\nGetting all PCC Registries")
    url = console + '/api/v1/settings/registry'
    response = requests.get(url, headers=auth_headers, verify=False)
    printDebug(response)
    return (json.loads(response.text))

def getAzureRegistryList(regDictList):
    registries = []
    printDebug("Found " + str(len(regDictList["specifications"])) + " total PCC registries")
    for regRow in regDictList["specifications"]:
        if (regRow["version"] == "azure"):
            regRow["registry"] = regRow["registry"].lstrip("https://")
            regRow["registry"] = regRow["registry"].split('/', 1)[0]
            printDebug("Found PCC Azure Container registry: " + regRow["registry"])
            registries.append(regRow["registry"])
    printDebug("Found " + str(len(registries)) + " Azure PCC Registries already added")
    return(registries)

def getAzureRegistriesToAdd(pcRegisitries, pccRegistries):
    return list(set(pcRegisitries) - set(pccRegistries))

def updatePCCRulesJSON(PCCRegDict, regToAdd, regCred):
    registryRuleTemplate = {
        'version': 'azure',
        'registry' : '',
        'repository' : '',
        'tag' : '',
        'os' : 'linux',
        'cap' : 5,
        'credentialID': '',
        'scanners': 2
    }
    workingRegistryDict = registryRuleTemplate 
    workingRegistryDict["registry"] = regToAdd
    workingRegistryDict["credentialID"] = regCred
    PCCRegDict["specifications"].append(workingRegistryDict)
    printDebug("Added " + regToAdd + " and " + regCred + " to registry specifications Dict")
    return (PCCRegDict)

def updateRegJSONRules(console,token,regDict):
    printDebug("\nUpdating all PCC Registries")
    bearer = "Bearer " + token
    auth_headers = {'content-type':'application/json', 'Authorization': bearer}
    url = console + '/api/v1/settings/registry'
    regDictSpec = { "specifications" : regDict }
    response = requests.put(url, headers=auth_headers, data=json.dumps(regDictSpec), verify=False)
    printDebug(response)
    return 0

def main():
    args = parse_args()
    pcToken = getPCToken(args.pcConsole,args.apiKey,args.apiSecret)
    pccToken = getPCCToken(args.pccConsole,args.apiKey,args.apiSecret)
    ACRLoginServers = getACRLoginServers(args.pcConsole,pcToken)
    PCCCreds = getPCCCreds(args.pccConsole,pccToken)
    if args.regCred not in PCCCreds:
        print(args.regCred + " not found in Prisma Cloud Compute credentials.")
        sys.exit(1)
    PCCRegistries = getPCCRegistries(args.pccConsole,pccToken)
    PCCAzureRegistries = getAzureRegistryList(PCCRegistries)
    if (str(len(PCCAzureRegistries)) != 0):
        PCCAzureRegistriesToAdd = getAzureRegistriesToAdd(ACRLoginServers,PCCAzureRegistries)
    else:
        PCCAzureRegistriesToAdd = ACRLoginServers
    printDebug("Found " + str(len(PCCAzureRegistriesToAdd)) + " Azure Registries to Add")
    printDebug("\nUpdating PCC registry specifications Dict")
    for reg in  PCCAzureRegistriesToAdd:
        PCCRegistries = updatePCCRulesJSON(PCCRegistries,reg,args.regCred)
    updateStatus = updateRegJSONRules(args.pccConsole,pccToken,PCCRegistries["specifications"])


if __name__ == '__main__':
    sys.exit(main())
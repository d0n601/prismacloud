
#######################################################################
#  Function: read_user
#  Inputs: None
#  Returns:
#    User name - string
#######################################################################
def read_user():
    name = input("Username: ")
    return (name)


#######################################################################
#  Function: read_pw
#  Inputs: None
#  Returns:
#    pw - string
#######################################################################
def read_pw():
    import getpass
    pw = getpass.getpass()
    return (pw)


#######################################################################
#  Function: read_api
#  Inputs: String of comma seperated api endpoints
#  Returns:
#    select api url - string
#######################################################################
def read_api(apiEndpoints):
    iteration = 1
    endpoints = []
    for endpoint in apiEndpoints.split(', '):
        print(iteration, ": ", endpoint)
        endpoints.append(endpoint)
        iteration += 1
    selected = (int(input("API: "))-1)
    api = endpoints[selected]
    return (api)


#######################################################################
#  Function: get_pc_token
#  Inputs:
#    user - string, username
#    password - string, password
#    api - string, api url
#  Returns:
#    token - string, auth token
#######################################################################
def get_pc_token(user,pw,api):
    import requests
    import json
    url = api + "/login"
    payload = "{\"username\":\"" + user + "\",\"password\":\"" + pw + "\"}"
    headers = {
        "accept": "application/json; charset=UTF-8",
        "content-type": "application/json; charset=UTF-8"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    token = (response.text)
    jtoken = json.loads(token)
    return (jtoken["token"])


#######################################################################
#  Function: get_query_csv
#  Inputs:
#    jwt - string
#    query api - string
#    api - string, api url
#  Returns:
#    csv file
#######################################################################
def get_query_csv(jwt,queryresource,api):
    import requests
    url = api + "/search/config"
    payload = "{\"query\":\"config where api.name = '" + queryresource + "' \",\"timeRange\":{\"type\":\"relative\",\"value\":{\"unit\":\"hour\",\"amount\":24}}}"
    headers = {
        "accept": "text/csv; charset=UTF-8",
        "content-type": "application/json; charset=UTF-8",
        "x-redlock-auth": jwt
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return(response.text)


#######################################################################
#  Function: get_rql_csv
#  Inputs:
#    jwt - string
#    rql - string
#  Returns:
#    csv file
#######################################################################
def get_rql_csv(jwt,rql,api):
    import requests
    url = api + "/search/config"
    payload = "{\"query\":\"" + rql + "\",\"timeRange\":{\"type\":\"relative\",\"value\":{\"unit\":\"hour\",\"amount\":24}}}"
    headers = {
        "accept": "text/csv; charset=UTF-8",
        "content-type": "application/json; charset=UTF-8",
        "x-redlock-auth": jwt
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return(response.text)



#######################################################################
#  Function: get_pcc_token
#  Inputs:
#    user - string, username
#    password - string, password
#    api - string, api url
#  Returns:
#    token - string, auth token
#######################################################################
def get_pcc_token(user,password,api):
    import requests
    import json
    url = api + "/api/v1/authenticate"
    payload = "{\"username\":\"" + user + "\",\"password\":\"" + password + "\"}"
    headers = {
        "accept": "application/json; charset=UTF-8",
        "content-type": "application/json; charset=UTF-8"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    token = (response.text)
    jtoken = json.loads(token)
    return (jtoken["token"])



#######################################################################
#  Function: get_input_string
#  Inputs: question - string, request for information
#  Returns:
#    answer - string
#######################################################################
def get_input_string(question):
    answer = input(question + ": ")
    return (answer)


#######################################################################
#  Function: get_resource_to_query
#  Inputs: 
#          
#  Returns:
#    apiToQuery - string
#######################################################################
def get_resource_to_query(resourceoptions):
    iteration = 1
    resources = []
    for resource in resourceoptions:
        print(iteration, ": ", resource)
        resources.append(resource)
        iteration += 1
    selected = (int(input("Resource: "))-1)
    resourceToQuery = resources[selected]
    return(resourceToQuery)


#######################################################################
#  Function: get_cloud_accounts
#  Inputs: jwt authentication token
#          api endoint to connect to
#  Returns:
#    accounts
#######################################################################
def get_cloud_accounts(jwt,api):
    import requests
    import json
    url = api + "/cloud/name"
    headers = {
        "accept": "application/json; charset=UTF-8",
        "x-redlock-auth": jwt
    }
    response = requests.request("GET", url, headers=headers)
    print (response.text)
    cloudAccounts = json.loads(response.text)
    print (cloudAccounts["name"])
    return (response.json())

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
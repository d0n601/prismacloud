import getpass
import requests
import json
import pprint
from deepdiff import DeepDiff
from __builtin__ import raw_input

stacks = [
    'https://api.prismacloud.io',
    'https://api2.prismacloud.io',
    'https://api3.prismacloud.io'
]


def read_credentials():
    name = raw_input("Username: ")
    pw = getpass.getpass()
    return ([name, pw])


def get_stack():
    stack_number = 1
    for stack in stacks:
        print stack_number, stacks[stack_number - 1]
        stack_number += 1
    stack_index = int(raw_input("Select Stack: "))
    stack_index -= 1
    return stacks[stack_index]


def get_jwt(j_name, j_pw, j_api_stack):
    url = j_api_stack + "/login"
    payload = "{\"username\":\"" + j_name + "\",\"password\":\"" + j_pw + "\"}"
    headers = {
        'accept': "application/json; charset=UTF-8",
        'content-type': "application/json; charset=UTF-8"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    jwt_json = json.loads(response.text)
    customer_number = 1
    for customer in jwt_json["customerNames"]:
        print customer_number,
        customer_number += 1
        print (customer["customerName"])
    tenant_index = int(raw_input("Select Tenant: "))
    tenant_index -= 1
    tenant = jwt_json["customerNames"][tenant_index]["customerName"]
    payload = "{\"username\":\"" + j_name + "\",\"password\":\"" + j_pw + "\",\"customerName\":\"" + tenant + "\"}"
    headers = {
        'accept': "application/json; charset=UTF-8",
        'content-type': "application/json; charset=UTF-8"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    jwt_json = json.loads(response.text)
    return jwt_json["token"]


def get_db_rrn(d_jwt, d_api_stack):
    url = d_api_stack + "/search/config"
    payload = "{\"timeRange\":{\"type\":\"to_now\",\"value\":\"epoch\"},\"query\":\"config where api.name = 'azure-sql-db-list' \"}"
    headers = {
        'accept': "application/json; charset=UTF-8",
        'content-type': "application/json; charset=UTF-8",
        'x-redlock-auth': d_jwt
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    sql_db_json = json.loads(response.text)
    sql_db_count = sql_db_json["data"]["totalRows"]
    db_counter = 0
    while db_counter < sql_db_count:
        print db_counter + 1, sql_db_json["data"]["items"][db_counter]["name"]
        db_counter += 1
    db_index = int(raw_input("Select DB: ")) - 1
    return sql_db_json["data"]["items"][db_index]["rrn"]


def get_rrn_raw(r_jwt, r_api_stack, r_rrn, r_cfg_id):
    url = r_api_stack + "/resource/raw"
    payload = "{\"rrn\":\"" + r_rrn + "\",\"timelineItemId\":\"" + r_cfg_id + "\"}"
    headers = {
        'accept': "application/json; charset=UTF-8",
        'content-type': "application/json",
        'x-redlock-auth': r_jwt
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return json.loads(response.text)


def get_rrn_diffs(t_jwt, t_api_stack, t_rrn):
    url = t_api_stack + "/resource/timeline"
    payload = "{\"rrn\":\"" + t_rrn + "\"}"
    headers = {
        'accept': "application/json; charset=UTF-8",
        'content-type': "application/json",
        'x-redlock-auth': t_jwt
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    timeline_json = json.loads(response.text)
    loop = "0"
    tl_iteration = 0
    current_cfg_id = ""
    previous_cfg_id = ""
    while loop == "0":
        if timeline_json[tl_iteration]["type"] == "state_change" \
                and timeline_json[tl_iteration]["firstState"] is False:
            current_cfg_id = timeline_json[tl_iteration]["id"]
            previous_cfg_id = timeline_json[tl_iteration]["previousStateId"]
            loop = 1
        elif timeline_json[tl_iteration]["type"] == "state_change" \
                and timeline_json[tl_iteration]["firstState"] is True:
            current_cfg_id = timeline_json[tl_iteration]["id"]
            previous_cfg_id = "NULL"
            print "Current Config is First Config"
            exit()
            loop = 1
        else:
            tl_iteration += 1
    current_json = get_rrn_raw(t_jwt, t_api_stack, t_rrn, current_cfg_id)
    previous_json = get_rrn_raw(t_jwt, t_api_stack, t_rrn, previous_cfg_id)
    return DeepDiff(previous_json, current_json)


def print_diff(local_diffs):
    pretty_diffs = pprint.PrettyPrinter(indent=1)
    pretty_diffs.pprint(local_diffs)


api_stack = get_stack()
(name,pw)=(read_credentials())
jwt = (get_jwt(name, pw, api_stack))
db_rrn = get_db_rrn(jwt, api_stack)
diffs = get_rrn_diffs(jwt, api_stack, db_rrn)
print_diff(diffs)
exit()


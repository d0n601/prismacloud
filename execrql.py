import pclib
import configparser

####################################################################
# Read In config.ini
####################################################################
config = configparser.ConfigParser()
config.read("config.ini")
user = config['prismacloud']['accessKey']
pw = config['prismacloud']['secret']
api = config['prismacloud']['api']
resourceoptions = config.options('pccresources')


####################################################################
# Check for user and password from config
# If not, then get creds
####################################################################
if (user == ""): user = pclib.read_user()
if (pw == ""): pw = pclib.read_pw()


####################################################################
# Obtain Prisma Cloud Stack
####################################################################
if (api == ""):
    apiEndpoints = config['prismacloud']['apiEndpoints']
    api = pclib.read_api(apiEndpoints)


####################################################################
# Obtain Prisma Cloud token
####################################################################
jwt = pclib.get_pc_token(user,pw,api)


####################################################################
# Read in RQL
####################################################################
rql = input("RQL: ")

####################################################################
# Get RQL Response
####################################################################
print(pclib.get_rql_csv(jwt,rql,api))
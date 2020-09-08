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
if (user is ""): user = pclib.read_user()
if (pw is ""): pw = pclib.read_pw()


####################################################################
# Obtain Prisma Cloud Stack
####################################################################
if (api is ""):
    apiEndpoints = config['prismacloud']['apiEndpoints']
    api = pclib.read_api(apiEndpoints)


####################################################################
# Obtain Prisma Cloud token
####################################################################
jwt = pclib.get_pc_token(user,pw,api)


####################################################################
# Get resource to query
####################################################################
resourceToQuery = pclib.get_resource_to_query(resourceoptions)
apiToQuery = config['pccresources'][resourceToQuery]


####################################################################
# Get CSV for resource
####################################################################
print(pclib.get_query_csv(jwt,apiToQuery,api))
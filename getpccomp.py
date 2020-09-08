import pclib
import configparser

####################################################################
# Read In config.ini
####################################################################
config = configparser.ConfigParser()
config.read("config.ini")
pcuser = config['prismacloudcompute']['pcuser']
pcpass = config['prismacloudcompute']['pcpass']
api = config['prismacloudcompute']['api']


####################################################################
# Check for user and password from config
# If not, then get creds
####################################################################
if (pcuser is ""): user = pclib.read_user()
if (pcpass is ""): pw = pclib.read_pw()


####################################################################
# Obtain Prisma Cloud Compute API URL
####################################################################
if (api is ""):
    api = pclib.get_input_string("Enter Prisma Cloud Compute URL: ")


####################################################################
# Obtain Prisma Cloud token
####################################################################
jwt = pclib.get_pcc_token(pcuser,pcpass,api)


####################################################################
# Obtain Prisma Cloud Compute Compliance Policies
####################################################################
comp_policies = pclib.get_comp_policies(jwt,api)
import pclib
import configparser

####################################################################
# Read In config.ini
####################################################################
config = configparser.ConfigParser()
config.read("config.ini")
user = config['prismacloud']['user']
pw = config['prismacloud']['password']
api = config['prismacloud']['api']


####################################################################
# Check for user and password from config
# If not, then get creds
####################################################################
if (user is None): user = pclib.read_user()
if (pw is None): pw = pclib.read_pw()


####################################################################
# Obtain Prisma Cloud Stack
####################################################################
print(api)
if (api is None): api = pclib.read_api()
print(api)

####################################################################
# Obtain Prisma Cloud token
####################################################################

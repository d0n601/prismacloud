
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
#  Inputs: None
#  Returns:
#    pw - string
#######################################################################
def read_api():
    print("here")
    api = 'https://api.prismacloud.io'
    return (api)

import os

#--------------------------------------------------------------------

_net_connection_handler = None

def registerNetConnectionHandler(handler):
    global _net_connection_handler
    _net_connection_handler = handler

def checkNetConnection(path):
    unc = os.path.splitunc(path)
    if unc[0]:
        remote_resource_name = unc[0].replace('/','\\').rstrip('\\')
        try:
            _net_connection_handler(remote_resource_name)
        except Exception as e:
            print( e )

#--------------------------------------------------------------------


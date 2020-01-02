import os

#--------------------------------------------------------------------

_net_connection_handler = None

def registerNetConnectionHandler(handler):
    global _net_connection_handler
    _net_connection_handler = handler

def checkNetConnection(path):

    drive, tail = os.path.splitdrive(path)
    unc = ( drive.startswith("\\\\") or drive.startswith("//") )
    
    if unc:
        remote_resource_name = drive.replace('/','\\').rstrip('\\')
        try:
            _net_connection_handler(remote_resource_name)
        except Exception as e:
            print( e )

#--------------------------------------------------------------------


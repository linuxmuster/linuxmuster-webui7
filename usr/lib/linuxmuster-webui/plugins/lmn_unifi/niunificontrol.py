#!/usr/bin/env python3
# Netzint AT 20201023
# Python ni-control-unifi

from .unifi import API as Unifi_API
import json
import sys
import datetime
import argparse
import paramiko # python3-paramiko
import ipaddress


#{	
#	"username": "admin",
#	"baseurl" : "https://unifi:8443",
#	"password": "secret",
#	"sites": {
#		"default":{}
#		}
#}


def getConfig(path=""):
    # get password
    try:
        if path == "":
            configFile = '/etc/netzint/unifi-control.conf'
        else:
            configFile = path
        with open(configFile) as file:
            data = json.load(file)
            file.close()            
            return(data)
            
    except Exception as err:
        print ("unifi-control - no config file found in " + configFile +"\n"+ str(err))
        sys.exit()

def getElement(element,scope, subscope=None):
    try:
        if subscope:
            returnvalue= element[scope][subscope]
        else:
            returnvalue = element[scope]
    except Exception as err:
        #print (str(err))
        if scope=="uptime":
            returnvalue=0
        else:
            returnvalue=""
        #pass
    return returnvalue



def printDevicesInfo(devicesList):
    # Print the names of the columns. 
    print ("{:<25} {:<18} {:<19} {:<16} {:<5} {:<14} {:<8} {:<11} {:<10} {:<10} {:<40} {:<20} {:<10} {:<20}".format(
                            "ID",
                            "Internal Name", 
                            "Mac", 
                            "Ip", 
                            "Type", 
                            "Device_Model", 
                            "IP_Type",
                            "Site",
                            "Clients", 
                            "State",
                            "Device_Name",
                            "Uptime",
                            "Disabled",
                            "Tags"
                            ))
    print ("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    for key, value in devicesList.items():
        print ("{:<25} {:<18} {:<19} {:<16} {:<5} {:<14} {:<8} {:<11} {:<10} {:<10} {:<40} {:<20} {:<10} {:<20}".format(
                                value["DEVICE_ID"],
                                value["CHECK_NAME"], 
                                value["DEVICE_MAC"], 
                                value["DEVICE_IP"],
                                value["DEVICE_TYPE"],
                                value["DEVICE_MODEL"],
                                value["DEVICE_IP_TYPE"],
                                value["SITE"],
                                value["CLIENTS"],
                                value["STATE"],
                                value["DEVICE_NAME"],
                                str(datetime.timedelta(seconds=int(value["DEVICE_UPTIME"]))),
                                "True" if value["DISABLED"] > 0 else "False",
                                str(value["DEVICE_TAGS"])
                                ))

def getDevicesList(config, unifiApi):
    devicesList={}
    for site in config['sites']:
        #print (site)

        unifiApi._site = site
        DICT = unifiApi.list_devices()
        tags =  unifiApi.get_tags()

        #print (DICT)
        for element in DICT:
            DEVICE_NAME = getElement(element,'name')
            DEVICE_IP = getElement(element,'connect_request_ip')
            DEVICE_ID = getElement(element, '_id')
            SITE = site
            DEVICE_TYPE = getElement(element,'type')
            CHECK_NAME = DEVICE_TYPE+"_"+getElement(element,'serial')
            DEVICE_MODEL = getElement(element,'model')
            DEVICE_MAC = getElement(element,'mac')
            DEVICE_UPTIME = getElement(element,'uptime')
            DEVICE_IP_TYPE = getElement(element,'config_network', 'type')
            CLIENTS = getElement(element,'num_sta')
            STATE = getElement(element,'state')
            
            if getElement(element, 'disabled'):
                DISABLED = getElement(element, 'disabled')
            else:
                DISABLED = 0

            DEVICE_TAGS = []

            devicesList.update(
                                {DEVICE_MAC: 
                                    {
                                    "DEVICE_ID": DEVICE_ID,
                                    "CHECK_NAME":CHECK_NAME,    
                                    "DEVICE_MAC": DEVICE_MAC,
                                    "DEVICE_IP":DEVICE_IP,
                                    "DEVICE_TYPE":DEVICE_TYPE,
                                    "DEVICE_MODEL":DEVICE_MODEL,
                                    "DEVICE_IP_TYPE":DEVICE_IP_TYPE,
                                    "DEVICE_TAGS": DEVICE_TAGS,
                                    "SITE":SITE,
                                    "CLIENTS": CLIENTS,
                                    "STATE": STATE,
                                    "DEVICE_UPTIME": DEVICE_UPTIME,
                                    "DEVICE_NAME":DEVICE_NAME,
                                    "DISABLED": DISABLED
                                    }
                                })

        for tag in tags:
            for member in tag['member_table']:
                if member in devicesList:
                    devicesList[member]['DEVICE_TAGS'].append(tag['name'])

    return devicesList

def getSshConfig(config, unifiApi, site):
    # for site in config['sites']:
    #     try: 
    #         password=config['password']
    #         if not config['baseurl']:
    #             baseurl="https://unifi:8443"
    #         else:
    #             baseurl=config['baseurl']
    #         if not config['username']:
    #             username="admin"
    #         else:
    #             username=config['username']
    #     except Exception as err:
    #         print ("Unable to get userinformation from credentials\n" + str(err))
    #         sys.exit()

    # for site in config['sites']:
    #     try:
    #         with Unifi_API(username=username, password=password, baseurl=baseurl, site=site, verify_ssl=False) as api:
    #             DICT = (api.list_settings())
    #             for entry in DICT:
    #                 if "x_ssh_username" in entry:
    #                     config['sites'][site]["ssh-user"] = entry["x_ssh_username"]
    #                 if "x_ssh_password" in entry:
    #                     config['sites'][site]["ssh-password"] = entry["x_ssh_password"]
    #     except Exception as err:
    #         print ("unifi-control - wrong credentials, unable to get SSH information\n" + str(err))
    #         sys.exit()

    unifiApi._site = site
    DICT = (unifiApi.list_settings())
    sshconfig = {}
    for entry in DICT:
        if "x_ssh_username" in entry:
            sshconfig["ssh-user"] = entry["x_ssh_username"]
        if "x_ssh_password" in entry:
            sshconfig["ssh-password"] = entry["x_ssh_password"]

    return sshconfig

def askProceed():
    user_input = input('Proceed?[y/Y]\n')
    if user_input == 'y' or user_input == 'Y':
        return True
    else:
        return False
        

def rebootDevice(client, sshconfig):
    try:
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.load_system_host_keys()
        sshClient.connect(client, username=sshconfig["ssh-user"], password=sshconfig["ssh-password"],look_for_keys=False, allow_agent=False, timeout=5)
        stdin, stdout, stderr = sshClient.exec_command('reboot')
        print (stdout.readlines())
        #print (stderr.stderr.readlines())
        sshClient.close()
        return { "status": "success", "data": "" }
    except Exception as err:
        #print ("Failed to connect "+str(err))
        return { "status": "error", "data": str(err) }
    #print ("reboot "+ client)

def rebootDevices(devicesList,site):
    getSshConfig()

    # remove devices without IP
    for key, value in dict(devicesList).items():
        if key in devicesList:
            if value["DEVICE_IP"] == "":
                del devicesList[key]

    if not args.forceExecute:
        print ('Going to reboot the shown devices, accept with y to proceed. Use --force to skip this step:\n')
        printDevicesInfo(devicesList)
        if askProceed():
            for key, value in devicesList.items():
                rebootDevice(value["DEVICE_IP"], value["SITE"])
        else:
            print ('Aborted')

    else:
        print ("Execution forced, going to restart following devices:\n")
        printDevicesInfo(devicesList)
        for key, value in devicesList.items():
            print ("\nGoing to reboot: " + value["DEVICE_IP"] + " " + value["DEVICE_MAC"] + " " + value["DEVICE_IP"]  + " " + value["DEVICE_NAME"])
            rebootDevice(value["DEVICE_IP"], value["SITE"])

def disableDevice(device, unifiApi):
    if device["DEVICE_ID"] == "":
        return { "status": "error", "message": "Could not read device_id!" }

    unifiApi.modify_device(device["DEVICE_ID"], {
            "disabled": True
    })

    return { "status": "success", "data": "" }

def enableDevice(device, unifiApi):
    if device["DEVICE_ID"] == "":
        return { "status": "error", "message": "Could not read device_id!" }

    unifiApi.modify_device(device["DEVICE_ID"], {
            "disabled": False
    })

    return { "status": "success", "data": "" }
    

def setDevicesDisabled(devicesList, site, disabled):
    global unifyApi

    # remove devices without ID
    for key, value in dict(devicesList).items():
        if key in devicesList:
            if value["DEVICE_ID"] == "":
                del devicesList[key]

    if not args.forceExecute:
        print ('Going to {} the shown devices, accept with y to proceed. Use --force to skip this step:\n'.format("disable" if disabled else "enable"))
        printDevicesInfo(devicesList)
        if not askProceed():
            print ('Aborted')
            return

    else:
        print ("Execution forced, going to restart following devices:\n")
        printDevicesInfo(devicesList)


    for key, value in devicesList.items():
        unifyApi._site = value["SITE"]
        print ("\nGoing to {}: ".format("disable" if disabled else "enable") + value["DEVICE_IP"] + " " + value["DEVICE_MAC"] + " " + value["DEVICE_IP"]  + " " + value["DEVICE_NAME"])
        unifyApi.modify_device(value["DEVICE_ID"], {
            "disabled": disabled
        })


def parseArguments():

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
                                    description='Netzint Unifi-Control \operate unifi controller and devices via cli',
                                    epilog='Netzint Unifi-Control Version 1.0\nNetzint GmbH 2020 \nWritten by Andreas Till <<andreas.till@netzint.de>>\
                                                \nUnifi control via cli')
    parser.add_argument('-i ', '--info', required=False, dest='info', action='store_true',
                        help='Shows information for devices in unifi controller')
    parser.add_argument('-f', '--filter', required=False, dest='filter', action='store_true',
                        help='filter devices, needs additional argument (--type, --iprange, --name)')
    
    # filters
    parser.add_argument('--type', type=str, required=False, dest='filter_type', default=None,
                        help='filter devices by type, eg. usw (Switch) or uap (Access Point)')
    parser.add_argument('--iprange', type=str, required=False, dest='filter_iprange', default=None,
                        help='filter devices by iprange')
    parser.add_argument('--dname', type=str, required=False, dest='filter_dname', default=None,
                        help='filter devices by device_name (user given)')
    parser.add_argument('--tag', type=str, required=False, dest='filter_tag', default=None,
                        help='filter devices by tags (user given)')
    
    parser.add_argument('-s ', '--site', type=str, required=False, dest='filter_site', default=None,
                        help='limits commands to given site')
    parser.add_argument('--reboot', required=False, dest='rebootDevice', action='store_true',
                        help='Reboots Access Points of the provided site, use all for all sites')
    parser.add_argument('--disable', required=False, dest='disableDevice', action='store_true',
                        help='Disables Access Points of the provided site, use all for all sites')
    parser.add_argument('--enable', required=False, dest='enableDevice', action='store_true',
                        help='Enables Access Points of the provided site, use all for all sites')
    
    parser.add_argument('--force', required=False, dest='forceExecute', action='store_true',
                        help='Force provided action, no questions aksed')
    parser.add_argument('-j ' '--json', required=False, dest='json', action='store_true',
                        help='print all devices in an json object for handling with other applications (ignores all other options but filters)')

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args=parser.parse_args()
    return (args)


def getDevicesInfoJson(devicesList):
    print (devicesList)

def validateIp(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError as err:
        print (err)
        sys.exit()

def validateIpNetwork(network):
    try:
         ipaddress.ip_network(network)
         return True
    except ValueError as err:
        print (err)
        sys.exit()

def checkIfIpInRange(ip, start, end):
    iprange=[]
    start_ip = ipaddress.IPv4Address(start)
    end_ip = ipaddress.IPv4Address(end)
    for ip_int in range(int(start_ip), int(end_ip+1)):
        iprange.append(str(ipaddress.IPv4Address(ip_int)))
        if len(iprange) > 4000:
            print ("error")
            sys.exit(1)
    if ip not in iprange:
        return False
    return True

def filterDevicelist(devicesList):
    for key, value in dict(devicesList).items():
            # filter type
            if args.filter_type:
                if args.filter_type not in value["DEVICE_TYPE"]:
                    del devicesList[key]
            
            # filter device_name
            if args.filter_dname:
                if key in devicesList:
                    if args.filter_dname not in value["DEVICE_NAME"]:
                        del devicesList[key]
            
            # filter site
            if args.filter_site and args.filter_site != "all":
                if key in devicesList:
                    if args.filter_site != value["SITE"]:
                        del devicesList[key]

            # filter iprange
            if args.filter_iprange:
                if key in devicesList:
                    if value["DEVICE_IP"] == "":
                        del devicesList[key]
                    else:
                        if '/' in args.filter_iprange:
                            validateIpNetwork(args.filter_iprange)
                            if ipaddress.ip_address(value["DEVICE_IP"]) not in ipaddress.ip_network(args.filter_iprange):
                                del devicesList[key]
                        if '-' in args.filter_iprange:
                            start, end = args.filter_iprange.split('-')                            
                            validateIp(start)
                            validateIp(end)
                            if not checkIfIpInRange(value["DEVICE_IP"], start,end):
                                del devicesList[key]
                        if '-' not in  args.filter_iprange and '/' not in args.filter_iprange:
                            if validateIp(args.filter_iprange):
                                if not checkIfIpInRange(value["DEVICE_IP"], args.filter_iprange,args.filter_iprange):
                                    del devicesList[key]

            if args.filter_tag:
                if key in devicesList:
                    if not args.filter_tag in value["DEVICE_TAGS"]:
                        del devicesList[key]

    return devicesList

def initAPI(username, password, baseurl):
    unifyApi = Unifi_API(username=username, password=password, baseurl=baseurl, verify_ssl=False)
    unifyApi.login()
    return unifyApi


def main():
    global args
    global config
    global unifyApi

    config=getConfig()
    args=parseArguments()

    if (
        args.rebootDevice or args.disableDevice or args.enableDevice
        ) and args.filter_site == None:
        print ("Cannot use rebootDevice, enable or disable without -s --site argument! You have to specify a site. You can also use 'all' to specify all sites")
        sys.exit()
    elif args.filter_site not in config['sites'] and args.filter_site != "all":
        print ("Site \"{}\" not found in configuration file".format(args.filter_site))
        sys.exit(1)

    # authenticate to unify
    try: 
        password=config['password']
        if not config['baseurl']:
            baseurl="https://unifi:8443"
        else:
            baseurl=config['baseurl']
        if not config['username']:
            username="admin"
        else:
            username=config['username']
    except Exception as err:
        print ("Unable to get userinformation from credentials\n" + str(err))
        sys.exit()

    try:
        # unifyApi = Unifi_API(username=username, password=password, baseurl=baseurl, site=args.filter_site, verify_ssl=False)
        # unifyApi.login()
        unifyApi = initAPI(username, password, baseurl, args.filter_site)
    except Exception as err:
        print ("unifi-control - wrong credentials\n" + str(err))
        sys.exit(1)

    # check if filter has additional arguments
    if args.filter:
        if not args.filter_type and not args.filter_iprange and not args.filter_dname and not args.filter_site:
            print ("Filter used withoud additional argument for filter condition (type, iprange, dname)")
            sys.exit()

    # get devicesList once we know the arguments are right
    if args.info or args.json or args.rebootDevice or args.rebootDevice or args.disableDevice or args.enableDevice:
        devicesList=getDevicesList(config)
    else:
        print ("You need at least one of the options --info, --json, --rebootDevice, --disable, --enable")
        sys.exit()

    # filter deviceList
    if args.filter:
        # apply filters     
        # create copy of dict to iterate over due dict changes during looping causes RunTimeError
        devicesList=filterDevicelist(devicesList)

    if args.rebootDevice:
        rebootDevices(devicesList, args.filter_site)
            
    elif args.disableDevice:
        setDevicesDisabled(devicesList, args.filter_site, True)
    
    elif args.enableDevice:
        setDevicesDisabled(devicesList, args.filter_site, False)

    elif args.json:
        getDevicesInfoJson(devicesList)

    elif args.info:
        printDevicesInfo(devicesList)

    sys.exit(0)

if __name__ == "__main__":
    main()
    sys.exit()


